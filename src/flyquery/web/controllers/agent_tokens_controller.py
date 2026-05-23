# Copyright 2026 Firefly Software Solutions Inc
"""User-tier CRUD endpoints for agent bearer tokens.

Three routes mounted under ``/api/v1/agent-tokens``:

* ``POST /api/v1/agent-tokens``       -- mint a new token. The full
  secret is returned in the response *exactly once* under ``token``;
  the server only persists the SHA-256 hash + the public 12-char
  prefix. Callers MUST capture the token at this point.
* ``GET /api/v1/agent-tokens``        -- list tokens for the
  current tenant (newest first). The list omits the secret and
  exposes only the public prefix + metadata.
* ``DELETE /api/v1/agent-tokens/{token_id}`` -- revoke. Idempotent:
  revoking an already-revoked token is a no-op (still 204).
  Unknown ``token_id`` returns 404 ``resource_not_found``.

The CRUD is **user-tier**. We parse the standard tenant headers via
:func:`tenant_context_from_request` and additionally refuse any
caller whose JWT actor is itself an agent (``ctx.actor`` prefixed
``"agent:"``) -- agents cannot mint or manage tokens for other
agents. In dev / unauthenticated test contexts ``ctx.actor`` is
``None`` and the route falls back to the ``"anonymous"`` actor
string.
"""

from __future__ import annotations

import logging

from pyfly.container import rest_controller
from pyfly.web import (
    Body,
    PathVar,
    Valid,
    delete_mapping,
    get_mapping,
    post_mapping,
    request_mapping,
)
from starlette.requests import Request

from flyquery.core.services.auth.agent_token_service import (
    AgentCannotMint,
    AgentTokenService,
    AgentTokenSummary,
    MintedAgentToken,
    MintRequest,
)
from flyquery.interfaces.dtos.agent_token import (
    AgentTokenCreated,
    AgentTokenMintRequest,
    AgentTokenSummaryDto,
)
from flyquery.web.conventions import (
    ResourceNotFound,
    TenantContext,
    tenant_context_from_request,
)

logger = logging.getLogger(__name__)


@rest_controller
@request_mapping("/api/v1/agent-tokens")
class AgentTokensController:
    """REST adapter for :class:`AgentTokenService` -- user-tier surface.

    Mirrors the controller shape used elsewhere in flyquery (see
    ``workspaces_controller``): pyfly's ``@rest_controller`` skips
    FastAPI ``Depends()`` resolution, so we inject the raw Starlette
    ``Request`` and parse the tenant context with the canonical helper.
    """

    def __init__(self, agent_token_service: AgentTokenService) -> None:
        self._service = agent_token_service

    @post_mapping("", status_code=201)
    async def mint(
        self,
        http_request: Request,
        body: Valid[Body[AgentTokenMintRequest]],
    ) -> AgentTokenCreated:
        """Mint a new agent token.

        Returns 201 with the full ``token`` populated. The token is
        only returned this once -- subsequent reads expose only
        ``prefix``. Refuses agent-tier callers with
        ``403 agent_cannot_mint``.
        """
        ctx = tenant_context_from_request(http_request)
        _reject_agent_actor(ctx)
        minted = await self._service.mint(
            MintRequest(
                tenant_id=ctx.tenant_id,
                name=body.name,
                workspace_allowlist=list(body.workspace_allowlist)
                if body.workspace_allowlist is not None
                else None,
                scopes=list(body.scopes),
                rate_limit_rpm=body.rate_limit_rpm,
                expires_at=body.expires_at,
            ),
            actor=ctx.actor or "anonymous",
        )
        # Read back the summary so the response carries every persisted
        # field (created_at, created_by, etc.) -- the service exposes
        # those on the ``AgentTokenSummary`` shape only.
        summary = await _find_minted_summary(self._service, ctx.tenant_id, minted)
        return _to_created(summary, minted.token)

    @get_mapping("")
    async def list_tokens(self, http_request: Request) -> list[AgentTokenSummaryDto]:
        """List tokens for the current tenant (newest first).

        Returns the summary shape only -- the secret is never
        round-tripped on this endpoint.
        """
        ctx = tenant_context_from_request(http_request)
        _reject_agent_actor(ctx)
        rows = await self._service.list_for_tenant(ctx.tenant_id)
        return [_to_summary(row) for row in rows]

    @delete_mapping("/{token_id}", status_code=204)
    async def revoke(self, http_request: Request, token_id: PathVar[str]) -> None:
        """Revoke a token. Idempotent -- already-revoked is a no-op (204).

        Unknown ``token_id`` returns ``404 resource_not_found``.
        """
        ctx = tenant_context_from_request(http_request)
        _reject_agent_actor(ctx)
        # The repository's ``revoke`` returns False both when the row
        # is missing AND when it was already revoked. Distinguish the
        # two by checking the tenant's listing first -- this is the
        # CRUD surface, so the extra query is acceptable.
        #
        # Cross-tenant safety is enforced at the SQL layer by
        # ``service.revoke`` (which forwards ``tenant_id`` to the repo
        # WHERE clause). The list lookup here is purely for the 404 vs
        # 204 distinction; even if the listing were stale, a
        # cross-tenant revoke could not succeed.
        rows = await self._service.list_for_tenant(ctx.tenant_id)
        if not any(row.id == token_id for row in rows):
            raise ResourceNotFound(f"Agent token {token_id!r} not found.")
        await self._service.revoke(token_id, tenant_id=ctx.tenant_id)
        return None


def _reject_agent_actor(ctx: TenantContext) -> None:
    """Refuse agent-tier callers from the user-tier CRUD surface.

    Agents authenticate via ``X-Agent-Token``; their resolved actor
    string begins with ``"agent:"``. Minting / managing tokens is a
    user-tier operation -- one agent must never be able to fan out
    new credentials for another agent.
    """
    if ctx.actor is not None and ctx.actor.startswith("agent:"):
        raise AgentCannotMint("Agent-tier callers cannot manage agent tokens.")


async def _find_minted_summary(
    service: AgentTokenService,
    tenant_id: str,
    minted: MintedAgentToken,
) -> AgentTokenSummary:
    """Look the freshly-minted row up to read its persisted fields."""
    rows = await service.list_for_tenant(tenant_id)
    for row in rows:
        if row.id == minted.id:
            return row
    # The token was inserted moments earlier -- a missing row here is
    # a serious invariant violation (repository or DB issue). Bubble
    # up an exception so the call fails loudly rather than silently
    # returning an incomplete envelope.
    raise RuntimeError(f"Minted agent token {minted.id!r} not found in tenant listing.")


def _to_summary(row: AgentTokenSummary) -> AgentTokenSummaryDto:
    return AgentTokenSummaryDto(
        id=row.id,
        name=row.name,
        prefix=row.prefix,
        workspace_allowlist=row.workspace_allowlist,
        scopes=row.scopes,
        rate_limit_rpm=row.rate_limit_rpm,
        expires_at=row.expires_at,
        created_at=row.created_at,
        created_by=row.created_by,
        revoked_at=row.revoked_at,
        last_used_at=row.last_used_at,
    )


def _to_created(row: AgentTokenSummary, token: str) -> AgentTokenCreated:
    return AgentTokenCreated(
        id=row.id,
        name=row.name,
        prefix=row.prefix,
        workspace_allowlist=row.workspace_allowlist,
        scopes=row.scopes,
        rate_limit_rpm=row.rate_limit_rpm,
        expires_at=row.expires_at,
        created_at=row.created_at,
        created_by=row.created_by,
        revoked_at=row.revoked_at,
        last_used_at=row.last_used_at,
        token=token,
    )


__all__ = ["AgentTokensController"]
