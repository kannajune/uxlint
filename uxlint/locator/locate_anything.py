"""Real backend: NVIDIA LocateAnything (open-vocabulary visual grounding).

Model card: https://huggingface.co/nvidia/LocateAnything-3B
Project:    https://research.nvidia.com/labs/lpr/locate-anything/

This is intentionally thin and isolated so the rest of uxlint never has
to import torch. It is loaded only when you pass `--backend locate-anything`.

NOTE: the exact processor/output API of the published checkpoint may differ
from the placeholder below. Treat `_parse_output` as the one spot to adapt
to the real model card once you wire it up — everything else is stable.
"""

from __future__ import annotations

from uxlint.types import Box

DEFAULT_MODEL = "nvidia/LocateAnything-3B"


class LocateAnythingLocator:
    def __init__(self, model: str = DEFAULT_MODEL, device: str | None = None) -> None:
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoProcessor
        except ImportError as exc:  # pragma: no cover - import-guard
            raise RuntimeError(
                "The LocateAnything backend needs the model extras. Install with:\n"
                "    pip install 'uxlint[model]'"
            ) from exc

        self._torch = torch
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.processor = AutoProcessor.from_pretrained(model, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            model, trust_remote_code=True, torch_dtype="auto"
        ).to(self.device)

    def locate(self, image_path: str, queries: list[str]) -> dict[str, list[Box]]:
        from PIL import Image

        image = Image.open(image_path).convert("RGB")
        out: dict[str, list[Box]] = {}
        for q in queries:
            prompt = f"Locate: {q}"
            inputs = self.processor(images=image, text=prompt, return_tensors="pt").to(
                self.device
            )
            with self._torch.no_grad():
                generated = self.model.generate(**inputs, max_new_tokens=256)
            decoded = self.processor.batch_decode(generated, skip_special_tokens=True)[0]
            out[q] = self._parse_output(decoded, q, image.size)
        return out

    @staticmethod
    def _parse_output(text: str, label: str, image_size: tuple[int, int]) -> list[Box]:
        """Turn the model's textual box output into Box objects.

        LocateAnything emits coordinates; adapt this parser to the exact
        format on the model card (normalized 0-1 vs pixel, JSON vs tags).
        Below handles a simple ``[x1, y1, x2, y2]`` (normalized) form.
        """
        import re

        w, h = image_size
        boxes: list[Box] = []
        for m in re.finditer(
            r"\[?\s*([0-9.]+)[,\s]+([0-9.]+)[,\s]+([0-9.]+)[,\s]+([0-9.]+)\s*\]?", text
        ):
            x1, y1, x2, y2 = (float(g) for g in m.groups())
            if max(x1, y1, x2, y2) <= 1.0:  # normalized -> pixels
                x1, x2 = x1 * w, x2 * w
                y1, y2 = y1 * h, y2 * h
            boxes.append(Box(label=label, x1=x1, y1=y1, x2=x2, y2=y2, score=1.0))
        return boxes
