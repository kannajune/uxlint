"""Core data types shared across uxlint.

Kept dependency-free on purpose so rules and reporting can import these
without pulling in Playwright or torch.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any


class Severity(str, Enum):
    """How badly a finding is likely to hurt conversion."""

    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"

    @property
    def weight(self) -> int:
        return {"critical": 30, "warning": 12, "info": 3}[self.value]


@dataclass
class Box:
    """An element located in the screenshot, in pixel coordinates.

    (x1, y1) is the top-left corner, (x2, y2) the bottom-right.
    `label` is the query that produced it, e.g. "primary call-to-action button".
    """

    label: str
    x1: float
    y1: float
    x2: float
    y2: float
    score: float = 1.0

    @property
    def width(self) -> float:
        return max(0.0, self.x2 - self.x1)

    @property
    def height(self) -> float:
        return max(0.0, self.y2 - self.y1)

    @property
    def center(self) -> tuple[float, float]:
        return (self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Finding:
    """One CRO/UX issue (or pass) produced by a rule."""

    rule_id: str
    title: str
    severity: Severity
    message: str
    recommendation: str = ""
    boxes: list[Box] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "title": self.title,
            "severity": self.severity.value,
            "message": self.message,
            "recommendation": self.recommendation,
            "boxes": [b.to_dict() for b in self.boxes],
        }


@dataclass
class AuditResult:
    """The full result of auditing one page."""

    url: str
    viewport: str
    screenshot_path: str
    image_width: int
    image_height: int
    findings: list[Finding] = field(default_factory=list)

    @property
    def score(self) -> int:
        """A 0-100 conversion-readiness score. Higher is better.

        Starts at 100 and subtracts a weight per finding by severity.
        """
        penalty = sum(f.severity.weight for f in self.findings)
        return max(0, 100 - penalty)

    def to_dict(self) -> dict[str, Any]:
        return {
            "url": self.url,
            "viewport": self.viewport,
            "screenshot_path": self.screenshot_path,
            "image_width": self.image_width,
            "image_height": self.image_height,
            "score": self.score,
            "findings": [f.to_dict() for f in self.findings],
        }
