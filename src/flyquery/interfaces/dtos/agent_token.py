# Copyright 2026 Firefly Software Solutions Inc
"""Wire DTOs for the agent-tokens user-tier surface.

These DTOs back the ``POST/GET/DELETE /api/v1/agent-tokens`` CRUD
endpoints. The mint request is the only one that accepts secret
input; every response shape is built on top of
:class:`AgentTokenSummaryDto`, which deliberately omits the raw
token and only exposes the public ``prefix``. The mint endpoint
extends the summary with :class:`AgentTokenCreated`, which adds
the raw ``token`` field exactly once -- subsequent reads through
list/revoke never expose it again.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AgentTokenMintRequest(BaseModel):
    """Request body for ``POST /api/v1/agent-tokens``.

    ``workspace_allowlist`` is optional -- ``None`` means the token
    can be used in any workspace under the tenant. ``scopes``
    defaults to ``["*"]`` (all scopes); the verify path treats
    ``"*"`` as a wildcard. ``rate_limit_rpm`` is advisory metadata
    today and reserved for the per-token rate limiter we add
    later; ``expires_at`` is enforced by the verify path.
    """

    model_config = ConfigDict(frozen=True)

    name: str = Field(min_length=1, max_length=128)
    workspace_allowlist: list[str] | None = None
    scopes: list[str] = Field(default_factory=lambda: ["*"])
    rate_limit_rpm: int | None = Field(default=None, ge=1, le=10_000)
    expires_at: datetime | None = None


class AgentTokenSummaryDto(BaseModel):
    """Token surface as listed back to user-tier callers -- secret omitted.

    Every read path through ``GET /api/v1/agent-tokens`` returns
    this shape. The raw token is *only* available on the
    :class:`AgentTokenCreated` returned by the mint endpoint and
    is never round-tripped through any other endpoint.
    """

    model_config = ConfigDict(frozen=True)

    id: str
    name: str
    prefix: str
    workspace_allowlist: list[str] | None
    scopes: list[str]
    rate_limit_rpm: int | None
    expires_at: datetime | None
    created_at: datetime
    created_by: str
    revoked_at: datetime | None
    last_used_at: datetime | None


class AgentTokenCreated(AgentTokenSummaryDto):
    """Mint response: includes the full ``token`` ONCE.

    Subsequent reads only ever expose ``prefix`` -- the secret hash
    is stored server-side and never returned. Callers MUST
    capture the token at mint time; there is no recovery path.
    """

    token: str


__all__ = [
    "AgentTokenCreated",
    "AgentTokenMintRequest",
    "AgentTokenSummaryDto",
]
