"""Trust-signal rules. Social proof reduces hesitation."""

from __future__ import annotations

from uxlint.rules.base import Rule, RuleContext
from uxlint.types import Finding, Severity

TRUST_QUERY = "customer testimonial or trust badge or rating"


class TrustSignalsPresent(Rule):
    id = "trust-signals"
    queries = [TRUST_QUERY]

    def check(self, ctx: RuleContext) -> list[Finding]:
        if not ctx.boxes(TRUST_QUERY):
            return [
                Finding(
                    rule_id=self.id,
                    title="No trust signals near the top",
                    severity=Severity.INFO,
                    message="No testimonial, rating, logo wall, or security badge was located "
                    "in the first screenful.",
                    recommendation="Add social proof above the fold (logos, ratings, a short "
                    "testimonial) to reduce hesitation before the CTA.",
                )
            ]
        return []
