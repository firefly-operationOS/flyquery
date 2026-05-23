# Copyright 2026 Firefly Software Solutions Inc
"""Slug validation for tenant_id / workspace_id header values."""

from __future__ import annotations

import re

_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")


class InvalidSlugError(ValueError):
    """Raised when a slug fails the firefly charset.

    Carries the offending value (and *only* the value, not user PII)
    so callers can log a redacted error without leaking the rest of
    the request context.
    """

    def __init__(self, value: str) -> None:
        super().__init__(f"invalid slug: {value!r}")
        self.value = value


def validate_slug(value: str) -> str:
    """Return ``value`` unchanged if it matches the slug grammar.

    Slug grammar: ``^[a-z0-9][a-z0-9_-]{0,63}$`` — 1-64 chars,
    starts alphanumeric, lowercase ASCII + digits + ``_`` + ``-``.
    """
    if not isinstance(value, str) or not _SLUG_RE.fullmatch(value):
        raise InvalidSlugError(value if isinstance(value, str) else "")
    return value
