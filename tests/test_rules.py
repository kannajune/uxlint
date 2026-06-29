"""Unit tests for the rule engine — run without a browser or a model."""

from uxlint.rules.base import RuleContext
from uxlint.rules.cta import CTA_QUERY, PrimaryCtaAboveFold, SinglePrimaryCta, CtaTapTarget
from uxlint.rules.forms import FIELD_QUERY, FormFriction
from uxlint.rules.trust import TRUST_QUERY, TrustSignalsPresent
from uxlint.types import Box, Severity


def ctx(located, viewport="desktop", w=1366, h=768):
    return RuleContext(viewport=viewport, image_width=w, image_height=h, located=located)


def test_missing_cta_is_critical():
    findings = PrimaryCtaAboveFold().check(ctx({CTA_QUERY: []}))
    assert findings and findings[0].severity is Severity.CRITICAL


def test_cta_present_high_passes():
    box = Box(CTA_QUERY, 100, 50, 300, 100)
    assert PrimaryCtaAboveFold().check(ctx({CTA_QUERY: [box]})) == []


def test_low_cta_warns():
    box = Box(CTA_QUERY, 100, 740, 300, 760)  # near bottom of 768px fold
    findings = PrimaryCtaAboveFold().check(ctx({CTA_QUERY: [box]}))
    assert findings and findings[0].severity is Severity.WARNING


def test_multiple_ctas_warn():
    boxes = [Box(CTA_QUERY, 0, 0, 10, 10), Box(CTA_QUERY, 20, 0, 30, 10)]
    findings = SinglePrimaryCta().check(ctx({CTA_QUERY: boxes}))
    assert findings and findings[0].severity is Severity.WARNING


def test_small_tap_target_only_on_mobile():
    tiny = Box(CTA_QUERY, 0, 0, 100, 20)  # 20px tall < 44px
    assert CtaTapTarget().check(ctx({CTA_QUERY: [tiny]}, viewport="desktop")) == []
    assert CtaTapTarget().check(ctx({CTA_QUERY: [tiny]}, viewport="mobile"))


def test_form_friction():
    many = [Box(FIELD_QUERY, 0, i * 10, 50, i * 10 + 8) for i in range(6)]
    assert FormFriction().check(ctx({FIELD_QUERY: many}))
    few = many[:3]
    assert FormFriction().check(ctx({FIELD_QUERY: few})) == []


def test_trust_signal_absent_is_info():
    findings = TrustSignalsPresent().check(ctx({TRUST_QUERY: []}))
    assert findings and findings[0].severity is Severity.INFO
