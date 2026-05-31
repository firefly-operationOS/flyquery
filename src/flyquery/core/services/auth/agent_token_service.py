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

"""Agent token mint + verify + list + revoke.

Tokens are stored as ``agt_<8hex>_<32hex>``; the first 12 chars
(``agt_<8hex>``) are the public prefix used as the lookup key,
the trailing 32 hex chars are the secret. Only the SHA-256 hash
of the full token is persisted.
"""

from __future__ import annotations

import hashlib
import secrets
import time
from collections import deque
from dataclasses import dataclass
from datetime import UTC, datetime
from threading import Lock
from typing import Protocol
from uuid import uuid4

from flyquery.web.conventions.exceptions import FireflyHTTPException

# -- Concrete exceptions exposed to controllers ---------------------


class InvalidAgentToken(FireflyHTTPException):
    status = 403
    code = "invalid_agent_token"
    title = "Invalid agent token"


class AgentTokenExpired(FireflyHTTPException):
    status = 403
    code = "agent_token_expired"
    title = "Agent token expired"


class AgentWorkspaceNotInAllowlist(FireflyHTTPException):
    status = 403
    code = "agent_workspace_not_in_allowlist"
    title = "Agent workspace not in allowlist"


class AgentScopeDenied(FireflyHTTPException):
    status = 403
    code = "agent_scope_denied"
    title = "Agent scope denied"


class AgentCannotMint(FireflyHTTPException):
    """Raised when an agent-tier caller tries to mint a token.

    Agents authenticate via ``X-Agent-Token`` (verified by
    :func:`require_agent_token`) and are never authorised to mint
    new tokens for other agents -- minting is a user-tier
    operation that requires an interactive operator JWT.
    """

    status = 403
    code = "agent_cannot_mint"
    title = "Agent cannot mint"


class RateLimitExceeded(FireflyHTTPException):
    """Raised when a token has exhausted its per-minute request budget.

    The token's ``rate_limit_rpm`` value is enforced inside
    :meth:`AgentTokenService.verify` via a per-token sliding 60s
    window counter. ``rate_limit_rpm = None`` (or 0) disables the
    check. The default in-memory counter is process-local; a
    Redis-backed counter is available via
    :class:`flyquery.core.services.auth.redis_rate_limiter.RedisRateLimiter`
    (opt-in through ``FLYQUERY_REDIS_URL`` /
    ``FLYQUERY_RATE_LIMIT_BACKEND=redis`` -- see
    :mod:`flyquery.core.configuration`).
    """

    status = 429
    code = "rate_limit_exceeded"
    title = "Too many requests"


# -- Domain types ---------------------------------------------------


@dataclass(frozen=True)
class MintRequest:
    tenant_id: str
    name: str
    workspace_allowlist: list[str] | None
    scopes: list[str]
    rate_limit_rpm: int | None
    expires_at: datetime | None


@dataclass(frozen=True)
class MintedAgentToken:
    id: str
    prefix: str
    token: str  # raw, returned ONCE


@dataclass(frozen=True)
class AgentTokenSummary:
    id: str
    tenant_id: str
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


@dataclass(frozen=True)
class VerifiedAgentToken:
    token_id: str
    actor: str
    prefix: str


# -- Repository protocol -------------------------------------------


class AgentTokenRepository(Protocol):
    """Persistence contract used by :class:`AgentTokenService`.

    Implemented by
    :class:`flyquery.models.repositories.agent_token_repository.AgentTokenRepository`
    for production; the unit tests substitute an in-memory double.

    ``get_by_prefix`` / ``revoke`` / ``mark_used`` all require a
    ``tenant_id`` kwarg -- the WHERE clauses filter by both the
    natural key (id or prefix) AND tenant so a cross-tenant operation
    can never succeed at the SQL layer regardless of caller path.
    Defense-in-depth alongside the ``tenant_isolation`` RLS policy on
    ``flyquery_agent_tokens``.
    """

    async def insert(self, row: dict) -> None: ...

    async def get_by_prefix(self, prefix: str, *, tenant_id: str) -> dict | None: ...

    async def list_for_tenant(self, tenant_id: str) -> list[dict]: ...

    async def revoke(self, token_id: str, *, tenant_id: str, at: datetime) -> bool: ...

    async def mark_used(self, token_id: str, *, tenant_id: str, at: datetime) -> None: ...


# -- Service --------------------------------------------------------


def _generate_token() -> tuple[str, str]:
    """Return ``(token, prefix)``. Token shape: ``agt_<8hex>_<32hex>``."""
    prefix_part = secrets.token_hex(4)  # 8 hex chars
    secret_part = secrets.token_hex(16)  # 32 hex chars
    prefix = f"agt_{prefix_part}"
    return f"{prefix}_{secret_part}", prefix


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _as_aware_utc(value: datetime | None) -> datetime | None:
    """Coerce a datetime to tz-aware UTC, treating naive values as UTC.

    Postgres ``DateTime(timezone=True)`` columns round-trip tz-aware,
    but SQLite (used by the integration suite) strips tz info on
    read and hands back naive ``datetime``s. Comparing those against
    ``datetime.now(UTC)`` raises ``TypeError: can't subtract offset-
    naive and offset-aware datetimes``, so we normalise at every
    comparison site that mixes a stored timestamp with ``now(UTC)``.
    """
    if value is None:
        return None
    return value if value.tzinfo is not None else value.replace(tzinfo=UTC)


class RateLimiter(Protocol):
    """Pluggable per-token sliding-window rate limiter contract.

    Two implementations ship today:

    * :class:`_RateLimiter` -- process-local, in-memory; the default
      wired by :class:`AgentTokenService` when no explicit limiter is
      passed in. Fine for single-replica dev / test.
    * :class:`flyquery.core.services.auth.redis_rate_limiter.RedisRateLimiter`
      -- Redis-backed sliding window using a ZSET + Lua script.
      Atomic across replicas; opt-in via ``FLYQUERY_REDIS_URL`` /
      ``FLYQUERY_RATE_LIMIT_BACKEND=redis`` (see
      :mod:`flyquery.core.configuration`).

    Both methods are ``async`` so the Redis adapter can speak to the
    async Redis client; the in-memory variant's bodies are sync but
    keep the ``async`` keyword so the Protocol is honoured.
    """

    async def consume(self, *, token_id: str, limit_per_minute: int | None, now: float) -> bool: ...

    async def drop(self, token_id: str) -> None: ...


class _TokenBucket:
    """Sliding-window counter per ``(token_id)``.

    Stores monotonic timestamps for each accepted request inside a
    rolling 60s window; a request is accepted iff the window holds
    fewer than ``limit_per_minute`` entries. Process-local; not
    durable across restarts and not shared across replicas (the Redis
    backing in :class:`RedisRateLimiter` closes the latter gap).
    """

    def __init__(self) -> None:
        self._timestamps: deque[float] = deque(maxlen=10000)

    def try_take(self, *, limit_per_minute: int, now: float) -> bool:
        """Return True if a slot was available; record the timestamp."""
        cutoff = now - 60.0
        while self._timestamps and self._timestamps[0] < cutoff:
            self._timestamps.popleft()
        if len(self._timestamps) >= limit_per_minute:
            return False
        self._timestamps.append(now)
        return True


class _RateLimiter:
    """Tracks per-token sliding-window counters. Process-local.

    Keyed by ``token_id`` so a single token's budget applies across
    all routes / workspaces; this matches the semantics documented on
    the ``rate_limit_rpm`` column. A ``threading.Lock`` guards the
    bucket dict so concurrent requests from the same token never race
    on bucket creation / mutation.

    ``consume`` / ``drop`` are ``async`` to honour the
    :class:`RateLimiter` Protocol -- the bodies stay synchronous
    (in-memory dict mutation under a threading lock) but the ``async``
    declaration lets :class:`AgentTokenService` await either this or
    the Redis-backed variant uniformly.
    """

    def __init__(self) -> None:
        self._buckets: dict[str, _TokenBucket] = {}
        self._lock = Lock()

    async def consume(self, *, token_id: str, limit_per_minute: int | None, now: float) -> bool:
        if limit_per_minute is None or limit_per_minute <= 0:
            return True
        with self._lock:
            bucket = self._buckets.setdefault(token_id, _TokenBucket())
            return bucket.try_take(limit_per_minute=limit_per_minute, now=now)

    async def drop(self, token_id: str) -> None:
        with self._lock:
            self._buckets.pop(token_id, None)


class AgentTokenService:
    """Mint / verify / list / revoke long-lived agent bearer tokens.

    The raw token is returned to the caller exactly once at mint time;
    only the SHA-256 hash plus the public 12-char prefix are
    persisted. ``verify`` is the hot path used by the
    ``require_agent_token`` FastAPI dependency: it looks the row up by
    prefix, constant-equality compares the full-token hash, then
    enforces tenant / expiry / workspace-allowlist / scope / rate
    limit in that order.
    """

    def __init__(
        self,
        repo: AgentTokenRepository,
        *,
        rate_limiter: RateLimiter | None = None,
    ) -> None:
        """Construct the service with an optional pluggable rate limiter.

        ``rate_limiter`` defaults to a fresh in-memory
        :class:`_RateLimiter`; pass a
        :class:`flyquery.core.services.auth.redis_rate_limiter.RedisRateLimiter`
        instance (wired by :mod:`flyquery.core.configuration` when
        ``FLYQUERY_REDIS_URL`` is set) to share the sliding window
        across replicas.
        """
        self._repo = repo
        self._rate_limiter: RateLimiter = rate_limiter if rate_limiter is not None else _RateLimiter()

    async def mint(self, request: MintRequest, *, actor: str) -> MintedAgentToken:
        token, prefix = _generate_token()
        token_id = uuid4().hex
        row = {
            "id": token_id,
            "tenant_id": request.tenant_id,
            "name": request.name,
            "prefix": prefix,
            "secret_hash": _hash(token),
            "workspace_allowlist_json": request.workspace_allowlist,
            "scopes_json": request.scopes,
            "rate_limit_rpm": request.rate_limit_rpm,
            "expires_at": request.expires_at,
            "created_at": datetime.now(UTC),
            "created_by": actor,
            "revoked_at": None,
            "last_used_at": None,
        }
        await self._repo.insert(row)
        return MintedAgentToken(id=token_id, prefix=prefix, token=token)

    async def verify(
        self,
        token: str,
        *,
        tenant_id: str,
        workspace_id: str,
        scope: str,
    ) -> VerifiedAgentToken:
        if not token.startswith("agt_") or len(token) < 12:
            raise InvalidAgentToken("Token shape is invalid.")
        prefix = token[:12]
        # The repository filters by (prefix, tenant_id) -- a row with the
        # right prefix but wrong tenant comes back as None below, raising
        # InvalidAgentToken("Unknown agent token.") rather than leaking
        # the tenant-mismatch distinction.
        row = await self._repo.get_by_prefix(prefix, tenant_id=tenant_id)
        if row is None:
            raise InvalidAgentToken("Unknown agent token.")
        # Defense-in-depth: the repo's WHERE clause already enforces
        # tenant scoping, but we keep this check so a bug that ever
        # weakens the repo filter (e.g., default kwarg, accidental
        # bypass) still fails closed at the service layer.
        if row["tenant_id"] != tenant_id:
            raise InvalidAgentToken("Token does not match the tenant header.")
        if not secrets.compare_digest(row["secret_hash"], _hash(token)):
            raise InvalidAgentToken("Token signature mismatch.")
        expires = _as_aware_utc(row.get("expires_at"))
        if expires is not None and expires <= datetime.now(UTC):
            raise AgentTokenExpired(f"Token expired at {expires.isoformat()}.")
        allowlist = row.get("workspace_allowlist_json")
        if allowlist is not None and workspace_id not in allowlist:
            raise AgentWorkspaceNotInAllowlist(f"Token is not allowed for workspace {workspace_id!r}.")
        scopes = row.get("scopes_json") or []
        if "*" not in scopes and scope not in scopes:
            raise AgentScopeDenied(f"Token scope does not permit {scope!r}.")
        rate_limit = row.get("rate_limit_rpm")
        if rate_limit is not None and not await self._rate_limiter.consume(
            token_id=row["id"],
            limit_per_minute=rate_limit,
            now=time.monotonic(),
        ):
            raise RateLimitExceeded(
                f"Token has exhausted its budget of {rate_limit} requests per minute.",
            )
        now = datetime.now(UTC)
        last_used = _as_aware_utc(row.get("last_used_at"))
        if last_used is None or (now - last_used).total_seconds() > 60:
            await self._repo.mark_used(row["id"], tenant_id=tenant_id, at=now)
        return VerifiedAgentToken(token_id=row["id"], actor=f"agent:{prefix}", prefix=prefix)

    async def list_for_tenant(self, tenant_id: str) -> list[AgentTokenSummary]:
        rows = await self._repo.list_for_tenant(tenant_id)
        return [
            AgentTokenSummary(
                id=row["id"],
                tenant_id=row["tenant_id"],
                name=row["name"],
                prefix=row["prefix"],
                workspace_allowlist=row.get("workspace_allowlist_json"),
                scopes=row.get("scopes_json") or [],
                rate_limit_rpm=row.get("rate_limit_rpm"),
                expires_at=row.get("expires_at"),
                created_at=row["created_at"],
                created_by=row["created_by"],
                revoked_at=row.get("revoked_at"),
                last_used_at=row.get("last_used_at"),
            )
            for row in rows
        ]

    async def revoke(self, token_id: str, *, tenant_id: str) -> bool:
        """Revoke a token for the given tenant.

        ``tenant_id`` is REQUIRED and is forwarded to the repository's
        WHERE clause -- a caller from tenant A can never revoke a
        token belonging to tenant B even if they hand-craft the
        ``token_id``. Defense-in-depth alongside the
        ``tenant_isolation`` RLS policy on ``flyquery_agent_tokens``.

        On success the in-memory rate-limit bucket for the revoked
        ``token_id`` is dropped so a subsequent re-mint that happens
        to collide on ``token_id`` (e.g. tests, deterministic UUIDs)
        starts with a fresh window.
        """
        revoked = await self._repo.revoke(token_id, tenant_id=tenant_id, at=datetime.now(UTC))
        if revoked:
            await self._rate_limiter.drop(token_id)
        return revoked
