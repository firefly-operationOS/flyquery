# Copyright 2026 Firefly Software Solutions Inc
"""Redis-backed :class:`IdempotencyStore` adapter.

Companion to
:class:`flyquery.web.conventions.idempotency.InMemoryIdempotencyStore`
(the default). Both honour the
:class:`flyquery.web.conventions.idempotency.IdempotencyStore` Protocol
so the agent controllers can swap one for the other without code
changes; selection happens in :mod:`flyquery.core.configuration` based
on the ``FLYQUERY_REDIS_URL`` setting.

Storage shape: each ``(tenant_id, route, key)`` tuple maps to a single
Redis string holding the JSON-serialised response envelope
(``{"status": int, "body": dict|list}``). The key carries a TTL
equal to :data:`DEFAULT_IDEMPOTENCY_TTL` so Redis evicts the entry
natively -- the in-memory variant's FIFO cap (``max_entries``) is
unnecessary here because Redis handles expiry without us.

Legacy :meth:`get` / :meth:`put` are deliberately not implemented for
the Redis adapter: those are tied to the older
``IdempotencyEntry`` row shape used by the workspace-scoped index and
are only consumed by the in-memory store's unit tests. The replay
path used by the agent controllers exclusively reads :meth:`lookup`
and writes :meth:`record_response`.
"""

from __future__ import annotations

import json
from typing import Any

import redis.asyncio as redis_async

from flyquery.web.conventions.idempotency import (
    DEFAULT_IDEMPOTENCY_TTL,
    IdempotencyEntry,
    IdempotencyKey,
    StoredResponse,
)


class RedisIdempotencyStore:
    """Redis-backed replay-dedup store for agent-tier POSTs.

    Each ``(tenant_id, route, key)`` tuple is one Redis string keyed
    ``<prefix><tenant>:<route>:<key>`` holding the JSON-serialised
    ``{"status": int, "body": dict|list}`` envelope. ``EXPIRE`` is
    set on write so entries age out without an explicit sweep --
    matches the contract documented on the in-memory variant
    (``second call within 24h returns the original response``).
    """

    def __init__(self, client: redis_async.Redis, *, prefix: str = "idemp:") -> None:
        """Bind a Redis client + key prefix.

        ``prefix`` defaults to ``"idemp:"`` so multiple Firefly
        services sharing the same Redis instance can coexist without
        colliding (flyquery uses ``"idemp:"`` by convention; flyradar
        mirrors it).
        """
        self._client = client
        self._prefix = prefix

    # -- Legacy sync surface -- not implemented for Redis ---------------
    #
    # The agent-tier replay path uses :meth:`lookup` /
    # :meth:`record_response` exclusively. The legacy ``get`` / ``put``
    # surface targets the (tenant, workspace, route, key) index used
    # only by unit tests of the in-memory variant; we deliberately
    # do not back it with Redis to keep this adapter minimal.

    def get(
        self,
        tenant_id: str,
        workspace_id: str,
        route: str,
        key: IdempotencyKey,
    ) -> IdempotencyEntry | None:
        """Always returns ``None`` -- legacy index is not Redis-backed."""
        return None

    def put(self, entry: IdempotencyEntry) -> None:
        """No-op -- legacy index is not Redis-backed."""
        return None

    # -- Replay-dedup surface (the active path) --------------------------

    def _key(self, tenant_id: str, route: str, key: str) -> str:
        """Build the canonical Redis key for a replay slot."""
        return f"{self._prefix}{tenant_id}:{route}:{key}"

    async def lookup(
        self,
        *,
        tenant_id: str,
        route: str,
        key: str,
    ) -> StoredResponse | None:
        """Return the cached response for ``(tenant, route, key)`` or ``None``.

        Empty key short-circuits to ``None`` (same defensive
        behaviour as the in-memory variant).
        """
        if not key:
            return None
        raw = await self._client.get(self._key(tenant_id, route, key))
        if raw is None:
            return None
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")
        entry = json.loads(raw)
        return StoredResponse(status=entry["status"], body=entry["body"])

    async def record_response(
        self,
        *,
        tenant_id: str,
        route: str,
        key: str,
        status: int,
        json_body: dict[str, Any] | list[Any],
    ) -> None:
        """Persist the response payload under ``(tenant, route, key)``.

        Empty key is a no-op so the agent controllers can call this
        unconditionally without worrying about whether the header
        was present (the helper upstream raises 400 when it isn't).

        ``EX = DEFAULT_IDEMPOTENCY_TTL`` lets Redis evict the entry
        natively -- no in-process FIFO cap required.
        """
        if not key:
            return
        await self._client.set(
            self._key(tenant_id, route, key),
            json.dumps({"status": status, "body": json_body}),
            ex=int(DEFAULT_IDEMPOTENCY_TTL.total_seconds()),
        )
