# Copyright 2026 Firefly Software Solutions Inc
"""``TenantContext`` — request-scoped (tenant, workspace, actor) tuple.

The FastAPI ``require_tenant_context()`` dependency builds a
``TenantContext`` from request headers and stashes it in a
ContextVar. Downstream code (services, repositories, the
tenant-safe HTTP client) reads it via ``current_tenant_context()``.
"""

from __future__ import annotations

from contextvars import ContextVar, Token
from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict, field_validator

from flyquery.web.conventions.validation import InvalidSlugError, validate_slug


class TenantContext(BaseModel):
    """Frozen (tenant_id, workspace_id, actor, correlation_id)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    tenant_id: str
    workspace_id: str
    actor: str | None = None
    correlation_id: str

    @field_validator("tenant_id", "workspace_id")
    @classmethod
    def _slug(cls, value: str) -> str:
        try:
            return validate_slug(value)
        except InvalidSlugError as exc:
            raise ValueError(str(exc)) from exc


_current: ContextVar[TenantContext | None] = ContextVar("firefly_tenant_context", default=None)


@dataclass(frozen=True)
class TenantContextToken:
    """Returned by ``set_tenant_context`` so the caller can reset on exit."""

    var: ContextVar[TenantContext | None]
    token: Token[TenantContext | None]


def set_tenant_context(ctx: TenantContext) -> TenantContextToken:
    """Bind ``ctx`` to the current async task / thread."""
    return TenantContextToken(var=_current, token=_current.set(ctx))


def current_tenant_context() -> TenantContext | None:
    """Return the bound context, or ``None`` outside a request."""
    return _current.get()
