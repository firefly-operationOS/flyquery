# Copyright 2026 Firefly Software Solutions Inc
"""flyquery agent-token scope catalog (spec §7.3).

Lock-step note: canon + radar each maintain their own catalog. The
``agent_token_service`` (lock-step from canon) consumes a callable
``validate_scopes`` per service. This module is the flyquery-specific
binding.
"""

from __future__ import annotations

from typing import Final


class InvalidScopeError(ValueError):
    """Raised when a token mint or check sees an unknown scope."""


ALL_SCOPES: Final[tuple[str, ...]] = (
    "flyquery.datasets:read",
    "flyquery.datasets:write",
    "flyquery.files:upload",
    "flyquery.files:read",
    "flyquery.schema:read",
    "flyquery.schema:annotate",
    "flyquery.relations:read",
    "flyquery.relations:write",
    "flyquery.semantic:read",
    "flyquery.semantic:author",
    "flyquery.examples:read",
    "flyquery.examples:author",
    "flyquery.query:read",
    "flyquery.derived:write",
    "flyquery.sql:execute",
    "flyquery.conversations:read",
    "flyquery.conversations:write",
    "flyquery.ingest:read",
    "flyquery.ingest:run",
    "flyquery.lineage:read",
    "flyquery.audit:read",
    "flyquery.billing:read",
    "*",  # operator-only wildcard
)


def is_valid_scope(scope: str) -> bool:
    return scope in ALL_SCOPES


def validate_scopes(scopes: list[str]) -> None:
    """Raise :class:`InvalidScopeError` on the first unknown scope."""
    for s in scopes:
        if not is_valid_scope(s):
            raise InvalidScopeError(f"unknown scope: {s!r}")
