# Copyright 2024-2026 Firefly Software Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""``require_tenant_context()`` -- FastAPI dependency.

Parses ``X-Tenant-Id`` + ``X-Workspace-Id`` (required) and
``X-Correlation-Id`` (optional). If ``Authorization: Bearer ...``
is present, decodes the JWT claims (no signature verification --
that's the gateway's job) and:
- raises ``TenantClaimMismatch`` whenever a ``tenant`` claim is
  present and disagrees with ``X-Tenant-Id`` (string mismatch OR
  any non-string claim value), regardless of whether ``sub`` is
  resolvable;
- uses ``sub`` as the actor when it is a non-empty string.
If ``X-Agent-Token`` is present and no JWT actor was resolved,
uses the token prefix as the actor.

Binds the resulting ``TenantContext`` to the ContextVar so the
exception handlers, repositories, and tenant-safe HTTP client
can read it without threading it through every signature. The
dependency is a yield-dependency so the ContextVar is reset on
request teardown (defensive: today each request runs in its own
asyncio task, but if that changes the cleanup keeps us safe).

The dep MUST be ``async def``. A sync dep would be run in a
threadpool worker by FastAPI/anyio and ``set_tenant_context()``
would bind the ContextVar in the WORKER thread's copied context
-- that mutation would not propagate back to the event-loop task
running the endpoint, so ``current_tenant_context()`` would
return ``None`` for downstream code.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any
from uuid import uuid4

from fastapi import Header

from flyquery.web.conventions.actor import (
    actor_from_agent_token,
    actor_from_jwt_claims,
    decode_jwt_unverified,
)
from flyquery.web.conventions.context import (
    TenantContext,
    set_tenant_context,
)
from flyquery.web.conventions.exceptions import (
    MissingTenantContext,
    TenantClaimMismatch,
)
from flyquery.web.conventions.headers import (
    HEADER_AGENT_TOKEN,
    HEADER_AUTHORIZATION,
    HEADER_CORRELATION_ID,
    HEADER_TENANT_ID,
    HEADER_WORKSPACE_ID,
)
from flyquery.web.conventions.validation import (
    InvalidSlugError,
    validate_slug,
)


def _new_correlation_id() -> str:
    return uuid4().hex


def _check_jwt_tenant_claim(claims: dict[str, Any], tenant_id: str) -> None:
    """Raise ``TenantClaimMismatch`` on any tenant-claim disagreement.

    Bypass-safe: runs regardless of ``sub``. Non-string claim values
    are treated as mismatches (a non-string ``tenant`` claim is
    malformed and cannot prove agreement with the header).
    """
    if "tenant" not in claims:
        return
    claim_value = claims["tenant"]
    if not isinstance(claim_value, str) or claim_value != tenant_id:
        raise TenantClaimMismatch(
            f"JWT tenant claim {claim_value!r} does not match {HEADER_TENANT_ID} {tenant_id!r}."
        )


def _resolve_actor(
    authorization: str | None,
    x_agent_token: str | None,
    tenant_id: str,
) -> str | None:
    if authorization:
        claims = decode_jwt_unverified(authorization)
        if claims is not None:
            _check_jwt_tenant_claim(claims, tenant_id)
            actor = actor_from_jwt_claims(claims)
            if actor is not None:
                return actor.value
    if x_agent_token:
        actor = actor_from_agent_token(x_agent_token)
        if actor is not None:
            return actor.value
    return None


def tenant_context_from_headers(
    *,
    x_tenant_id: str | None,
    x_workspace_id: str | None,
    x_correlation_id: str | None = None,
    authorization: str | None = None,
    x_agent_token: str | None = None,
) -> TenantContext:
    """Build a :class:`TenantContext` from already-extracted header values.

    Same validation + JWT cross-check as :func:`require_tenant_context`,
    but parameter-only (no FastAPI ``Header(...)`` defaults). Lets
    pyfly's ``@rest_controller`` methods bind the headers through
    pyfly's ``Header[str]`` resolver and then materialise the context
    without going through FastAPI's dependency-injection layer (which
    pyfly's ``add_api_route`` lazy wrapper bypasses).

    Raises :class:`MissingTenantContext` on missing/invalid tenant or
    workspace headers, and :class:`TenantClaimMismatch` when an
    ``Authorization`` JWT carries a ``tenant`` claim that disagrees
    with the header.
    """
    if not x_tenant_id or not x_workspace_id:
        raise MissingTenantContext(f"Both {HEADER_TENANT_ID} and {HEADER_WORKSPACE_ID} headers are required.")
    try:
        tenant = validate_slug(x_tenant_id)
        workspace = validate_slug(x_workspace_id)
    except InvalidSlugError as exc:
        raise MissingTenantContext(str(exc)) from exc

    actor = _resolve_actor(authorization, x_agent_token, tenant)

    return TenantContext(
        tenant_id=tenant,
        workspace_id=workspace,
        actor=actor,
        correlation_id=x_correlation_id or _new_correlation_id(),
    )


def tenant_context_from_request(request: Any) -> TenantContext:
    """Build a :class:`TenantContext` from a Starlette ``Request``.

    Thin wrapper over :func:`tenant_context_from_headers` -- used by
    pyfly ``@rest_controller`` methods that inject the raw
    Starlette ``Request`` (pyfly's parameter resolver bypasses
    FastAPI ``Depends`` so this is the in-controller equivalent of
    ``Depends(require_tenant_context)``).

    Does NOT bind the resulting context to the request-scoped
    ContextVar -- the caller is expected to pass the returned ctx
    explicitly to downstream handlers. Use :func:`require_tenant_context`
    when ContextVar binding (e.g. for ``tenant_safe_client``) is
    required.
    """
    headers = request.headers
    return tenant_context_from_headers(
        x_tenant_id=headers.get(HEADER_TENANT_ID),
        x_workspace_id=headers.get(HEADER_WORKSPACE_ID),
        x_correlation_id=headers.get(HEADER_CORRELATION_ID),
        authorization=headers.get(HEADER_AUTHORIZATION),
        x_agent_token=headers.get(HEADER_AGENT_TOKEN),
    )


async def require_tenant_context(
    x_tenant_id: str | None = Header(default=None, alias=HEADER_TENANT_ID),
    x_workspace_id: str | None = Header(default=None, alias=HEADER_WORKSPACE_ID),
    x_correlation_id: str | None = Header(default=None, alias=HEADER_CORRELATION_ID),
    authorization: str | None = Header(default=None, alias=HEADER_AUTHORIZATION),
    x_agent_token: str | None = Header(default=None, alias=HEADER_AGENT_TOKEN),
) -> AsyncIterator[TenantContext]:
    ctx = tenant_context_from_headers(
        x_tenant_id=x_tenant_id,
        x_workspace_id=x_workspace_id,
        x_correlation_id=x_correlation_id,
        authorization=authorization,
        x_agent_token=x_agent_token,
    )
    token = set_tenant_context(ctx)
    try:
        yield ctx
    finally:
        token.var.reset(token.token)
