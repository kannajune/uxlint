"""Call-to-action rules — the highest-leverage CRO checks."""

from __future__ import annotations

from uxlint.rules.base import Rule, RuleContext
from uxlint.types import Finding, Severity

CTA_QUERY = "primary call-to-action button"

# Apple/Google recommend a minimum ~44px touch target.
MIN_TAP_TARGET_PX = 44


class PrimaryCtaAboveFold(Rule):
    id = "cta-above-fold"
    queries = [CTA_QUERY]

    def check(self, ctx: RuleContext) -> list[Finding]:
        ctas = ctx.boxes(CTA_QUERY)
        if not ctas:
            return [
                Finding(
                    rule_id=self.id,
                    title="No primary call-to-action found above the fold",
                    severity=Severity.CRITICAL,
                    message="No clear primary CTA was located in the first screenful.",
                    recommendation="Add one obvious primary action (e.g. 'Start free trial') "
                    "visible without scrolling.",
                )
            ]
        # Best CTA should sit in the upper portion of the viewport.
        top = min(ctas, key=lambda b: b.y1)
        if top.center[1] > ctx.fold_y * 0.85:
            return [
                Finding(
                    rule_id=self.id,
                    title="Primary CTA sits low on the page",
                    severity=Severity.WARNING,
                    message="The primary CTA is near the bottom of the first screen.",
                    recommendation="Move the main CTA higher so it is seen immediately.",
                    boxes=[top],
                )
            ]
        return []


class SinglePrimaryCta(Rule):
    id = "cta-single-primary"
    queries = [CTA_QUERY]

    def check(self, ctx: RuleContext) -> list[Finding]:
        ctas = ctx.boxes(CTA_QUERY)
        if len(ctas) > 1:
            return [
                Finding(
                    rule_id=self.id,
                    title="Competing primary CTAs",
                    severity=Severity.WARNING,
                    message=f"{len(ctas)} elements look like primary CTAs above the fold.",
                    recommendation="Keep one visually dominant primary action; demote the rest "
                    "to secondary styling to avoid choice paralysis.",
                    boxes=ctas,
                )
            ]
        return []


class CtaTapTarget(Rule):
    id = "cta-tap-target"
    queries = [CTA_QUERY]

    def check(self, ctx: RuleContext) -> list[Finding]:
        if ctx.viewport != "mobile":
            return []
        small = [b for b in ctx.boxes(CTA_QUERY) if b.height < MIN_TAP_TARGET_PX]
        if small:
            return [
                Finding(
                    rule_id=self.id,
                    title="CTA is too small to tap comfortably",
                    severity=Severity.WARNING,
                    message=f"CTA height is below the {MIN_TAP_TARGET_PX}px mobile tap-target guideline.",
                    recommendation=f"Make the button at least {MIN_TAP_TARGET_PX}px tall on mobile.",
                    boxes=small,
                )
            ]
        return []
