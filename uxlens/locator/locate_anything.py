"""Real backend: NVIDIA LocateAnything (open-vocabulary visual grounding).

Model card: https://huggingface.co/nvidia/LocateAnything-3B
Project:    https://research.nvidia.com/labs/lpr/locate-anything/

Isolated so the rest of uxlens never imports torch. Loaded only when you
pass `--backend locate-anything`.

LICENSE NOTE: LocateAnything-3B is released for **non-commercial** use only.
uxlens itself is MIT, but this optional backend inherits NVIDIA's licence —
use it for research/personal audits, not commercially.

Loading/inference/parsing below follows the published model card. The model
emits boxes as `<box><x1><y1><x2><y2></box>` with coordinates normalized to
the integer range [0, 1000].
"""

from __future__ import annotations

import re

from uxlens.types import Box

DEFAULT_MODEL = "nvidia/LocateAnything-3B"

# Coordinates come back in 0..1000; divide by this then scale by image size.
COORD_SCALE = 1000.0


class LocateAnythingLocator:
    def __init__(self, model: str = DEFAULT_MODEL, device: str | None = None) -> None:
        try:
            import torch
            from transformers import AutoModel, AutoProcessor, AutoTokenizer
        except ImportError as exc:  # pragma: no cover - import-guard
            raise RuntimeError(
                "The LocateAnything backend needs the model extras. Install with:\n"
                "    pip install 'uxlens[model]'"
            ) from exc

        self._torch = torch
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(model, trust_remote_code=True)
        self.processor = AutoProcessor.from_pretrained(model, trust_remote_code=True)
        self.model = (
            AutoModel.from_pretrained(
                model, torch_dtype=torch.bfloat16, trust_remote_code=True
            )
            .to(self.device)
            .eval()
        )

    def locate(self, image_path: str, queries: list[str]) -> dict[str, list[Box]]:
        from PIL import Image

        image = Image.open(image_path).convert("RGB")
        w, h = image.size
        out: dict[str, list[Box]] = {}
        for q in queries:
            text = self._raw_inference(image, self._prompt(q))
            out[q] = self._parse_boxes(text, q, (w, h))
        return out

    @staticmethod
    def _prompt(query: str) -> str:
        # Phrase-grounding prompt from the model card.
        return f"Locate all the instances that match the following description: {query}."

    def _raw_inference(self, image, question: str) -> str:
        torch = self._torch
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {"type": "text", "text": question},
                ],
            }
        ]
        text = self.processor.py_apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        inputs = self.processor(text=[text], images=[image], return_tensors="pt").to(
            self.device
        )
        with torch.no_grad():
            response = self.model.generate(
                pixel_values=inputs["pixel_values"].to(torch.bfloat16),
                input_ids=inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                tokenizer=self.tokenizer,
                max_new_tokens=2048,
                generation_mode="hybrid",
                use_cache=True,  # the model asserts this is required
            )
        return self._decode(response)

    def _decode(self, response) -> str:
        """The custom generate() may return text or token ids; handle both."""
        if isinstance(response, str):
            return response
        if isinstance(response, (list, tuple)) and response and isinstance(response[0], str):
            return response[0]
        try:
            return self.tokenizer.batch_decode(response, skip_special_tokens=False)[0]
        except Exception:
            return str(response)

    @staticmethod
    def _parse_boxes(text: str, label: str, image_size: tuple[int, int]) -> list[Box]:
        """Parse `<box>...</box>` blocks into pixel-space Box objects.

        Each block holds 4 ints (box) or 2 ints (point), normalized 0..1000.
        Points are expanded into a tiny box so the rule engine still works.
        """
        w, h = image_size
        boxes: list[Box] = []
        for block in re.findall(r"<box>(.*?)</box>", text, flags=re.DOTALL):
            nums = [int(n) for n in re.findall(r"-?\d+", block)]
            if len(nums) >= 4:
                x1, y1, x2, y2 = nums[:4]
            elif len(nums) == 2:
                x, y = nums
                x1, y1, x2, y2 = x - 5, y - 5, x + 5, y + 5
            else:
                continue
            boxes.append(
                Box(
                    label=label,
                    x1=x1 / COORD_SCALE * w,
                    y1=y1 / COORD_SCALE * h,
                    x2=x2 / COORD_SCALE * w,
                    y2=y2 / COORD_SCALE * h,
                    score=1.0,
                )
            )
        return boxes
