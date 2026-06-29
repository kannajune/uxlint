"""Generate docs/demo.png — an annotated audit that actually shows findings.

The default `mock` backend returns one tidy box per element, so a healthy
page scores 100. To *illustrate* what a flagged report looks like, this
script uses a small DemoLocator that returns an intentionally poor layout
(two competing CTAs placed low, six form fields, no trust signals) over a
real screenshot, then renders the annotated image.

Run:  python examples/demo.py
"""

from __future__ import annotations

from pathlib import Path

from uxlint.audit import audit
from uxlint.rules.cta import CTA_QUERY
from uxlint.rules.forms import FIELD_QUERY
from uxlint.rules.trust import TRUST_QUERY
from uxlint.report import print_summary, write_annotated_image, write_json
from uxlint.types import Box

DOCS = Path(__file__).resolve().parent.parent / "docs"


class DemoLocator:
    """Returns a deliberately problematic layout to exercise every rule."""

    def locate(self, image_path: str, queries: list[str]) -> dict[str, list[Box]]:
        from PIL import Image

        with Image.open(image_path) as im:
            w, h = im.size

        return {
            # Two competing CTAs, both low on the page.
            CTA_QUERY: [
                Box(CTA_QUERY, w * 0.10, h * 0.88, w * 0.30, h * 0.95, 0.9),
                Box(CTA_QUERY, w * 0.60, h * 0.88, w * 0.80, h * 0.95, 0.8),
            ],
            # Six form fields -> friction.
            FIELD_QUERY: [
                Box(FIELD_QUERY, w * 0.35, h * (0.30 + i * 0.07),
                    w * 0.65, h * (0.30 + i * 0.07) + 18, 0.8)
                for i in range(6)
            ],
            # No trust signals at all.
            TRUST_QUERY: [],
        }


def main() -> None:
    result = audit(
        "https://example.com",
        out_dir=DOCS / "_work",
        viewport="desktop",
        backend=DemoLocator(),
    )
    print_summary(result)
    write_json(result, DOCS / "demo.json")
    out = write_annotated_image(result, DOCS / "demo.png")
    print(f"  wrote {out}")


if __name__ == "__main__":
    main()
