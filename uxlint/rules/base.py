"""Rule base class and the context passed to every rule."""

from __future__ import annotations

from dataclasses import dataclass

from uxlint.types import Box, Finding


@dataclass
class RuleContext:
    """Everything a rule needs to make a judgement."""

    viewport: str  # "desktop" | "mobile"
    image_width: int
    image_height: int
    located: dict[str, list[Box]]  # query -> boxes found

    def boxes(self, query: str) -> list[Box]:
        return self.located.get(query, [])

    @property
    def fold_y(self) -> float:
        """The y-pixel of the fold. We screenshot the viewport, so it's the bottom."""
        return float(self.image_height)


class Rule:
    """Base class. Subclasses set `id`, `queries`, and implement `check`."""

    id: str = "rule"
    queries: list[str] = []

    def check(self, ctx: RuleContext) -> list[Finding]:  # pragma: no cover - abstract
        raise NotImplementedError
