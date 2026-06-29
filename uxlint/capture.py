"""Take a screenshot of a URL with Playwright.

We capture the *above-the-fold* viewport (not the full scrolling page),
because most CRO heuristics care about what the visitor sees first.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

# Common device viewports. Width x height in CSS pixels.
VIEWPORTS = {
    "desktop": (1366, 768),
    "mobile": (390, 844),  # iPhone-ish
}


@dataclass
class Screenshot:
    path: str
    width: int
    height: int
    viewport: str


def capture(
    url: str,
    out_path: str | Path,
    viewport: str = "desktop",
    full_page: bool = False,
    wait_ms: int = 1500,
) -> Screenshot:
    """Screenshot `url` to `out_path`.

    Raises a friendly error if Playwright (or its browser) is not installed.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:  # pragma: no cover - import-guard
        raise RuntimeError(
            "Playwright is not installed. Run:\n"
            "    pip install uxlint && playwright install chromium"
        ) from exc

    if viewport not in VIEWPORTS:
        raise ValueError(
            f"Unknown viewport {viewport!r}. Choose from: {', '.join(VIEWPORTS)}"
        )

    vw, vh = VIEWPORTS[viewport]
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": vw, "height": vh})
        try:
            page.goto(url, wait_until="networkidle", timeout=30_000)
        except Exception:
            # networkidle can hang on chatty sites; fall back to DOM-ready.
            page.goto(url, wait_until="domcontentloaded", timeout=30_000)
        page.wait_for_timeout(wait_ms)
        page.screenshot(path=str(out_path), full_page=full_page)
        browser.close()

    width, height = (vw, vh) if not full_page else _image_size(out_path)
    return Screenshot(str(out_path), width, height, viewport)


def _image_size(path: str | Path) -> tuple[int, int]:
    from PIL import Image

    with Image.open(path) as im:
        return im.size
