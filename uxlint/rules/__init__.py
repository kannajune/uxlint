"""The CRO/UX rule engine.

Each rule declares which elements it needs located (`queries`) and inspects
the resulting boxes to emit Findings. Add a new heuristic by writing a Rule
and registering it in `ALL_RULES`.
"""

from uxlint.rules.base import Rule, RuleContext
from uxlint.rules.cta import PrimaryCtaAboveFold, SinglePrimaryCta, CtaTapTarget
from uxlint.rules.forms import FormFriction
from uxlint.rules.trust import TrustSignalsPresent

# The default rule set, ordered roughly by impact.
ALL_RULES: list[Rule] = [
    PrimaryCtaAboveFold(),
    SinglePrimaryCta(),
    CtaTapTarget(),
    FormFriction(),
    TrustSignalsPresent(),
]


def all_queries(rules: list[Rule] | None = None) -> list[str]:
    """Every distinct element query the given rules need located."""
    rules = rules or ALL_RULES
    seen: list[str] = []
    for r in rules:
        for q in r.queries:
            if q not in seen:
                seen.append(q)
    return seen


__all__ = ["Rule", "RuleContext", "ALL_RULES", "all_queries"]
