"""Orchestrator: capture -> locate -> run rules -> AuditResult."""

from __future__ import annotations

from pathlib import Path

from uxlint.capture import capture
from uxlint.locator import get_locator
from uxlint.locator.base import Locator
from uxlint.rules import ALL_RULES, all_queries
from uxlint.rules.base import RuleContext
from uxlint.types import AuditResult


def audit(
    url: str,
    out_dir: str | Path = "uxlint-report",
    viewport: str = "desktop",
    backend: str | Locator = "mock",
) -> AuditResult:
    """Audit a URL and return the result. Writes the screenshot into `out_dir`."""
    out_dir = Path(out_dir)
    shot_path = out_dir / "screenshot.png"

    shot = capture(url, shot_path, viewport=viewport)
    locator = backend if isinstance(backend, Locator) else get_locator(backend)

    queries = all_queries(ALL_RULES)
    located = locator.locate(str(shot.path), queries)

    ctx = RuleContext(
        viewport=viewport,
        image_width=shot.width,
        image_height=shot.height,
        located=located,
    )

    findings = []
    for rule in ALL_RULES:
        findings.extend(rule.check(ctx))

    # Critical first, then warnings, then info.
    order = {"critical": 0, "warning": 1, "info": 2}
    findings.sort(key=lambda f: order[f.severity.value])

    return AuditResult(
        url=url,
        viewport=viewport,
        screenshot_path=str(shot.path),
        image_width=shot.width,
        image_height=shot.height,
        findings=findings,
    )
