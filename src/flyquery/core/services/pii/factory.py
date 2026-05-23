# Copyright 2026 Firefly Software Solutions Inc
"""PiiScanner factory — resolves adapter from FLYQUERY_PII_SCANNER env.

Recognised values:
    regex     — default; pattern-based, no extra deps
    presidio  — wraps presidio-analyzer [presidio] extra (fails loudly if missing)
    disabled  — always returns None (explicit opt-out)

Unknown values fall back to the regex scanner (same as canon) so a typo
never silently disables PII detection.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def build_pii_scanner(name: str | None = None):
    """Return the appropriate PiiScanner instance for the given name.

    Args:
        name: Value of FLYQUERY_PII_SCANNER env var (or None → default "regex").
    """
    key = (name or "regex").strip().lower()

    if key == "disabled":
        from flyquery.core.services.pii.adapters.disabled_scanner import DisabledPiiScanner

        return DisabledPiiScanner()

    if key == "presidio":
        from flyquery.core.services.pii.adapters.presidio_scanner import PresidioPiiScanner

        return PresidioPiiScanner()  # ImportError raised here if extra missing

    if key != "regex":
        logger.warning("unknown FLYQUERY_PII_SCANNER=%r — falling back to regex scanner", name)

    from flyquery.core.services.pii.adapters.regex_scanner import RegexPiiScanner

    return RegexPiiScanner()
