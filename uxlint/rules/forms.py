"""Form-friction rules. Fewer fields generally convert better."""

from __future__ import annotations

from uxlint.rules.base import Rule, RuleContext
from uxlint.types import Finding, Severity

FIELD_QUERY = "form input field"

# Above this many visible fields in the hero, friction tends to hurt signups.
MAX_COMFORTABLE_FIELDS = 4


class FormFriction(Rule):
    id = "form-friction"
    queries = [FIELD_QUERY]

    def check(self, ctx: RuleContext) -> list[Finding]:
        fields = ctx.boxes(FIELD_QUERY)
        if len(fields) > MAX_COMFORTABLE_FIELDS:
            return [
                Finding(
                    rule_id=self.id,
                    title="Signup form may have too many fields",
                    severity=Severity.WARNING,
                    message=f"{len(fields)} input fields detected above the fold.",
                    recommendation="Ask only for what you truly need now; defer the rest to "
                    "after signup. Every removed field lifts completion.",
                    boxes=fields,
                )
            ]
        return []
