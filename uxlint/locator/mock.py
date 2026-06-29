"""A deterministic, dependency-free locator for demos and tests.

It does NOT look at the image — it fabricates plausible boxes from the
query text and image size, seeded by the query so results are stable.
Use it to develop rules and see the full pipeline run without a GPU.
"""

from __future__ import annotations

import hashlib

from PIL import Image

from uxlint.types import Box


class MockLocator:
    def __init__(self, **_: object) -> None:
        pass

    def _seed(self, text: str) -> float:
        h = hashlib.sha1(text.encode()).hexdigest()
        return int(h[:8], 16) / 0xFFFFFFFF  # 0.0 - 1.0

    def locate(self, image_path: str, queries: list[str]) -> dict[str, list[Box]]:
        with Image.open(image_path) as im:
            w, h = im.size

        out: dict[str, list[Box]] = {}
        for q in queries:
            s = self._seed(q)
            # Place a box deterministically based on the query hash.
            bw = w * (0.15 + 0.2 * s)
            bh = h * (0.04 + 0.06 * s)
            x1 = (w - bw) * s
            y1 = (h - bh) * self._seed(q + "y")
            out[q] = [Box(label=q, x1=x1, y1=y1, x2=x1 + bw, y2=y1 + bh, score=0.5 + 0.5 * s)]
        return out
