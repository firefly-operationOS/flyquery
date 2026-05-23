# Copyright 2026 Firefly Software Solutions Inc
"""Redis-backed sliding-window per-token rate limiter.

Companion to :class:`flyquery.core.services.auth.agent_token_service._RateLimiter`
(the default in-memory implementation). Both honour the
:class:`flyquery.core.services.auth.agent_token_service.RateLimiter`
Protocol so :class:`AgentTokenService` can swap one for the other
without touching any caller.

The in-memory variant is fine for single-replica dev / test posture.
The Redis variant is the production choice for any multi-replica
deployment -- without it, every replica enforces its own private
sliding window, and a token configured with ``rate_limit_rpm=N``
effectively gets ``N * replica_count`` real budget.

Wire it via :mod:`flyquery.core.configuration` (``redis_url`` is read
through :class:`FlyquerySettings`; ``FLYQUERY_RATE_LIMIT_BACKEND=redis``
forces it on; ``=in_memory`` forces the in-memory fallback even when
``redis_url`` is set).
"""

from __future__ import annotations

from collections.abc import Awaitable
from typing import Any, cast

import redis.asyncio as redis_async


class RedisRateLimiter:
    """Sliding-window per-token rate limiter backed by Redis ZSET.

    Each token's accepted-request timestamps are stored as a sorted
    set keyed by ``rl:<token_id>`` with member = monotonic timestamp,
    score = the same timestamp. On every :meth:`consume` call we
    (1) ``ZREMRANGEBYSCORE`` away entries older than 60s,
    (2) ``ZCARD`` to count the remaining entries,
    (3) ``ZADD`` the new timestamp iff the count is under the cap.

    The three commands run inside a single Lua script via ``EVALSHA``
    so the operation is atomic across replicas -- two concurrent
    requests on different boxes both see consistent ZCARD output
    before either inserts.

    The script's ``EXPIRE`` (65s, just over the window) lets idle
    tokens age out of Redis without leaking keys. ``EVALSHA`` cache
    misses (e.g. Redis restart, script flush) are handled by
    reloading the script transparently inside :meth:`consume`.
    """

    LUA_SCRIPT = """
    local key = KEYS[1]
    local now = tonumber(ARGV[1])
    local limit = tonumber(ARGV[2])
    local cutoff = now - 60
    redis.call('ZREMRANGEBYSCORE', key, '-inf', cutoff)
    local count = redis.call('ZCARD', key)
    if count >= limit then
      return 0
    end
    redis.call('ZADD', key, now, now)
    redis.call('EXPIRE', key, 65)
    return 1
    """

    def __init__(self, client: redis_async.Redis, *, prefix: str = "rl:") -> None:
        """Bind a Redis client + key prefix.

        ``prefix`` defaults to ``"rl:"`` so multiple Firefly services
        sharing the same Redis can coexist without colliding (flyquery
        uses ``"rl:"`` by convention; flyquery mirrors it).
        """
        self._client = client
        self._prefix = prefix
        self._script_sha: str | None = None

    async def consume(self, *, token_id: str, limit_per_minute: int | None, now: float) -> bool:
        """Atomic ZREMRANGEBYSCORE + ZCARD + (conditional) ZADD.

        Returns ``True`` if the new request fits inside the rolling
        60s window for ``token_id`` (and records the timestamp);
        ``False`` if the bucket is full. ``limit_per_minute is None``
        or ``<= 0`` short-circuits to ``True`` -- the same semantics
        as the in-memory variant.
        """
        if limit_per_minute is None or limit_per_minute <= 0:
            return True
        if self._script_sha is None:
            self._script_sha = await self._load_script()
        try:
            result = await self._evalsha(token_id, limit_per_minute, now)
        except redis_async.ResponseError:
            # NOSCRIPT -- the script cache was flushed (Redis restart,
            # ``SCRIPT FLUSH``, replica promotion). Reload + retry once.
            self._script_sha = await self._load_script()
            result = await self._evalsha(token_id, limit_per_minute, now)
        return bool(result)

    async def _load_script(self) -> str:
        """Wrap ``script_load`` with the explicit ``Awaitable`` cast.

        ``redis.asyncio.Redis.script_load`` is typed
        ``Awaitable[Any] | Any`` because the sync + async surfaces
        share the same method declaration. The cast pins the async
        return for the type checker without changing runtime
        behaviour.
        """
        return cast(str, await cast(Awaitable[Any], self._client.script_load(self.LUA_SCRIPT)))

    async def _evalsha(self, token_id: str, limit_per_minute: int, now: float) -> Any:
        """Invoke the Lua script via ``EVALSHA`` with the cached sha.

        Same ``Awaitable`` cast rationale as :meth:`_load_script`.
        """
        assert self._script_sha is not None  # narrow for the type checker
        return await cast(
            Awaitable[Any],
            self._client.evalsha(
                self._script_sha,
                1,
                f"{self._prefix}{token_id}",
                now,
                limit_per_minute,
            ),
        )

    async def drop(self, token_id: str) -> None:
        """Drop the bucket for ``token_id`` (called from ``revoke``).

        Mirrors :meth:`_RateLimiter.drop`: when a token is revoked we
        evict its sliding-window state so a re-mint that happens to
        collide on ``token_id`` starts with a fresh budget.
        """
        await cast(Awaitable[Any], self._client.delete(f"{self._prefix}{token_id}"))
