"""Render an audit into an annotated PNG and a JSON report."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from uxlint.types import AuditResult, Severity

SEVERITY_COLOR = {
    Severity.CRITICAL: (220, 38, 38),   # red
    Severity.WARNING: (217, 119, 6),    # amber
    Severity.INFO: (37, 99, 235),       # blue
}


def write_json(result: AuditResult, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_dict(), indent=2))
    return path


def write_annotated_image(result: AuditResult, path: str | Path) -> Path:
    """Draw every finding's boxes onto the screenshot, colored by severity."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    base = Image.open(result.screenshot_path).convert("RGBA")
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    font = _load_font(16)

    for finding in result.findings:
        color = SEVERITY_COLOR[finding.severity]
        for box in finding.boxes:
            draw.rectangle([box.x1, box.y1, box.x2, box.y2], outline=color + (255,), width=3)
            label = finding.rule_id
            tx, ty = box.x1, max(0, box.y1 - 20)
            tw = draw.textlength(label, font=font)
            draw.rectangle([tx, ty, tx + tw + 8, ty + 19], fill=color + (230,))
            draw.text((tx + 4, ty + 2), label, fill=(255, 255, 255, 255), font=font)

    out = Image.alpha_composite(base, overlay).convert("RGB")
    out.save(path)
    return path


def _load_font(size: int):
    for name in ("Arial.ttf", "DejaVuSans.ttf", "Helvetica.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def print_summary(result: AuditResult) -> None:
    """Human-friendly terminal summary."""
    icons = {Severity.CRITICAL: "✗", Severity.WARNING: "!", Severity.INFO: "i"}
    print(f"\n  uxlint report for {result.url}")
    print(f"  viewport: {result.viewport}   score: {result.score}/100\n")
    if not result.findings:
        print("  ✓ No issues found. Nice.\n")
        return
    for f in result.findings:
        print(f"  [{icons[f.severity]}] {f.severity.value.upper():8} {f.title}")
        print(f"      {f.message}")
        if f.recommendation:
            print(f"      → {f.recommendation}")
        print()
