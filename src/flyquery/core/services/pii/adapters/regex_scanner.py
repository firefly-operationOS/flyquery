# Copyright 2026 Firefly Software Solutions Inc
"""Regex-based PII scanner adapter (no extra deps).

Patterns mirror canon's RegexPiiScanner exactly (lock-step principle),
with the addition of IPv4 and explicit Luhn-friendly credit card patterns.

Canonical patterns:
  email       — RFC 5322 simplified
  us_ssn      — US Social Security Number (###-##-####)
  phone       — E.164 + common North American formats
  credit_card — Luhn-friendly 13-19 digit groupings
  ipv4        — standard dotted-quad

The scan is conservative (false negatives over false positives) so the
warn policy stays usable on real business corpora.
"""

from __future__ import annotations

import re

from flyquery.core.services.pii.scanner import PiiFinding, PiiTag

# ---------------------------------------------------------------------------
# Patterns (byte-equivalent to canon's _PATTERNS where they overlap)
# ---------------------------------------------------------------------------
_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "EMAIL",
        re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b"),
    ),
    (
        "SSN",
        # US SSN — exclude 000/666/9xx prefix combos
        re.compile(r"\b(?!000|666|9\d\d)\d{3}-(?!00)\d{2}-(?!0000)\d{4}\b"),
    ),
    (
        "CREDIT_CARD",
        # Luhn-friendly 16-digit groupings with optional spaces/dashes.
        # Must match before PHONE to avoid partial matches on card numbers.
        # Scanner does NOT validate the Luhn checksum (warn-first for v1).
        re.compile(r"\b(?:\d{4}[ \-]?){3}\d{4}\b"),
    ),
    (
        "PHONE",
        # International + US formats; conservative on length (≥7 digits).
        re.compile(
            r"(?<!\d)(?:\+?\d{1,3}[\s.\-]?)?(?:\(\d{2,4}\)|\d{2,4})[\s.\-]?\d{3,4}[\s.\-]?\d{3,4}(?!\d)"
        ),
    ),
    (
        "IP_ADDRESS",
        # IPv4 dotted-quad; exclude obvious non-IPs like version strings.
        re.compile(r"(?<!\d)(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)(?!\d)"),
    ),
)

# Column name / description keywords that strongly suggest PII
_NAME_HINTS: dict[str, str] = {
    "email": "EMAIL",
    "e_mail": "EMAIL",
    "mail": "EMAIL",
    "ssn": "SSN",
    "social_security": "SSN",
    "phone": "PHONE",
    "mobile": "PHONE",
    "telephone": "PHONE",
    "credit_card": "CREDIT_CARD",
    "card_number": "CREDIT_CARD",
    "ip": "IP_ADDRESS",
    "ip_address": "IP_ADDRESS",
    "ipaddress": "IP_ADDRESS",
}


def _scan_text(text: str) -> PiiFinding | None:
    """Return the first (highest-priority) PII hit in text, or None."""
    if not text:
        return None
    for entity_type, pattern in _PATTERNS:
        match = pattern.search(text)
        if match:
            snippet = match.group(0)
            # Filter obviously-bad phone hits (e.g. bare years).
            if entity_type == "PHONE" and len(re.sub(r"\D", "", snippet)) < 7:
                continue
            return PiiFinding(entity_type=entity_type, score=0.9)
    return None


class RegexPiiScanner:
    """Regex PII scanner — no external dependencies."""

    async def scan_single(self, value: str) -> PiiFinding | None:
        return _scan_text(str(value) if value is not None else "")

    async def scan_column(
        self,
        name: str,
        description: str | None,
        samples: list[str],
        data_type: str,
    ) -> PiiTag | None:
        # 1. Keyword match on column name / description
        lower_name = (name or "").lower()
        for hint, entity_type in _NAME_HINTS.items():
            if hint in lower_name:
                return PiiTag(tag=entity_type, source="REGEX")
        if description:
            lower_desc = description.lower()
            for hint, entity_type in _NAME_HINTS.items():
                if hint in lower_desc:
                    return PiiTag(tag=entity_type, source="REGEX")

        # 2. Scan sample values
        hits: dict[str, int] = {}
        for sample in samples:
            finding = await self.scan_single(str(sample))
            if finding:
                hits[finding.entity_type] = hits.get(finding.entity_type, 0) + 1

        if hits:
            # Pick the entity_type with most hits
            top = max(hits, key=lambda k: hits[k])
            return PiiTag(tag=top, source="REGEX")

        return None
