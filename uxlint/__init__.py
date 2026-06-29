"""uxlint — a linter for landing pages.

Screenshot a URL, locate the UX elements with a vision model, and get a
ranked list of conversion-rate (CRO) findings with an annotated image.
"""

from uxlint.types import Box, Finding, Severity, AuditResult

__version__ = "0.1.0"

__all__ = ["Box", "Finding", "Severity", "AuditResult", "__version__"]
