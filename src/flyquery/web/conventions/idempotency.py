# Copyright 2026 Firefly Software Solutions Inc
"""Idempotency primitives used by the agent + user tiers.

The store is a Protocol so production swaps the in-memory
implementation for a Postgres- or Redis-backed one in a later plan.

Two layers live in this module:

* :class:`IdempotencyKey` -- the value-object guard for the
  ``Idempotency-Key`` header charset (1-128 chars of
  ``[A-Za-z0-9_-]``).
* :class:`IdempotencyStore` -- the persistence surface used by the
  agent controllers to dedup replays. An entry stores both the
  bookkeeping (``response_hash`` / ``job_id``) and -- new in this
  iteration -- the response payload itself
  (``response_status`` + ``response_json``) so a replayed call can
  return the original wire response without re-dispatching the
  command.

Two index shapes are exposed by the store:

* :meth:`IdempotencyStore.get` -- legacy by-:class:`IdempotencyKey`
  read used by the ``test_idempotency`` suite and any caller that
  already validated the key.
* :meth:`IdempotencyStore.lookup` -- replay-dedup read that takes
  the raw string straight off the request header. Returns ``None``
  if the entry is absent, expired, or has no recorded response
  body (i.e. a partial entry from the legacy ``put`` path).

:meth:`IdempotencyStore.record_response` is the write surface used by
the agent controllers after dispatching a command -- it stores both
the status and the JSON body under ``(tenant_id, route, key)`` so a
replayed call short-circuits the command bus.

In-memory is fine for MVP; a real deployment would swap in a
Redis-backed or Postgres-backed implementation behind the same
:class:`IdempotencyStore` Protocol.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any, Protocol

_KEY_RE = re.compile(r"^[A-Za-z0-9_\-]{1,128}$")

# Default TTL for stored idempotency responses. The agent contract
# states "second call with the same key within 24h returns the
# original response"; longer windows are not required for MVP and
# would inflate the in-memory footprint.
DEFAULT_IDEMPOTENCY_TTL = timedelta(hours=24)


class InvalidIdempotencyKeyError(ValueError):
    """Raised when the Idempotency-Key header value fails the charset."""


@dataclass(frozen=True)
class IdempotencyKey:
    """1-128 chars of [A-Za-z0-9_-]."""

    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str) or not _KEY_RE.fullmatch(self.value):
            raise InvalidIdempotencyKeyError(f"invalid Idempotency-Key: {self.value!r}")


@dataclass(frozen=True)
class StoredResponse:
    """Cached agent response surfaced to a replayed POST.

    ``status`` is the HTTP status the original dispatch returned.
    ``body`` is the JSON-serialisable payload of the original
    response (the controller's pydantic model ``.model_dump(mode="json")``).
    """

    status: int
    body: dict[str, Any] | list[Any]


@dataclass(frozen=True)
class IdempotencyEntry:
    """One row in the idempotency store.

    Two halves of the row:

    * Bookkeeping -- ``response_hash`` + ``job_id`` retained for
      backward compatibility with the legacy ``put`` writers.
    * Replay payload -- ``response_status`` + ``response_json`` are
      the cached HTTP response used to short-circuit a replayed
      POST. Both default to ``None`` for entries written via the
      legacy ``put`` API.
    """

    tenant_id: str
    workspace_id: str
    route: str
    key: IdempotencyKey
    response_hash: str
    job_id: str | None
    expires_at: datetime
    response_status: int | None = None
    response_json: dict[str, Any] | list[Any] | None = None


class IdempotencyStore(Protocol):
    """Pluggable backing store. Production uses Redis/Postgres; tests use memory.

    Two read APIs:

    * :meth:`get` -- legacy by-:class:`IdempotencyKey` reader used by
      existing test coverage. Sync, returns the raw
      :class:`IdempotencyEntry` or ``None`` if absent / expired.
    * :meth:`lookup` -- replay-dedup reader used by the agent
      controllers. Async, takes the raw header string (workspace is
      *intentionally* not part of the namespace because the agent
      contract namespaces by ``(tenant_id, route, key)`` only --
      a token whose allowlist contains two workspaces should not be
      able to replay the same response across them, but the
      separation is enforced upstream by the agent token verifier,
      not by this store). Returns a :class:`StoredResponse` if the
      entry exists, is not expired, and carries a recorded response
      body; otherwise ``None``.

    Two write APIs:

    * :meth:`put` -- legacy direct-entry writer (sync).
    * :meth:`record_response` -- async; stores the response body
      keyed by ``(tenant_id, route, key)`` with the module-default
      TTL.

    ``lookup`` and ``record_response`` are ``async`` so the Redis
    adapter (see
    :class:`flyquery.web.conventions.redis_idempotency.RedisIdempotencyStore`)
    can speak to the async Redis client; the in-memory variant's
    bodies are sync but keep the ``async`` keyword so the Protocol is
    honoured uniformly.
    """

    def get(
        self,
        tenant_id: str,
        workspace_id: str,
        route: str,
        key: IdempotencyKey,
    ) -> IdempotencyEntry | None: ...

    def put(self, entry: IdempotencyEntry) -> None: ...

    async def lookup(
        self,
        *,
        tenant_id: str,
        route: str,
        key: str,
    ) -> StoredResponse | None: ...

    async def record_response(
        self,
        *,
        tenant_id: str,
        route: str,
        key: str,
        status: int,
        json_body: dict[str, Any] | list[Any],
    ) -> None: ...


@dataclass
class InMemoryIdempotencyStore(IdempotencyStore):
    """In-memory store. Expired entries are skipped on read.

    Two parallel indexes live inside the store:

    * ``_entries`` -- legacy (tenant, workspace, route, key) index
      used by :meth:`get` / :meth:`put`. Keeps the original test
      fixtures working.
    * ``_replays`` -- (tenant, route, key) index populated by
      :meth:`record_response` and consumed by :meth:`lookup`. This
      is the index the agent controllers read on every POST to
      decide whether to short-circuit the command bus.

    Both indexes are FIFO-capped at ``max_entries`` (default 100k).
    When a write would push past the cap, the oldest inserted entry
    is evicted. Python's ``dict`` preserves insertion order since 3.7
    so ``next(iter(...))`` gives the oldest key in O(1). Without this
    cap the dicts would grow unbounded across the 1h TTL window,
    which matters under sustained high write QPS (e.g., a busy ingest
    agent doing 50 writes per second over 24h would otherwise leak
    ~4M entries into the dict).

    The two indexes are deliberately independent: a writer can use
    either API without polluting the other. Production swaps both
    behind a Redis-backed implementation; the in-memory variant is
    test/dev only.
    """

    max_entries: int = 100_000
    _entries: dict[tuple[str, str, str, str], IdempotencyEntry] = field(default_factory=dict)
    _replays: dict[tuple[str, str, str], IdempotencyEntry] = field(default_factory=dict)

    def _enforce_replays_cap(self) -> None:
        while len(self._replays) >= self.max_entries:
            # ``next(iter(dict))`` returns the oldest inserted key (dict
            # preserves insertion order since Python 3.7).
            self._replays.pop(next(iter(self._replays)), None)

    def _enforce_entries_cap(self) -> None:
        while len(self._entries) >= self.max_entries:
            self._entries.pop(next(iter(self._entries)), None)

    def get(
        self,
        tenant_id: str,
        workspace_id: str,
        route: str,
        key: IdempotencyKey,
    ) -> IdempotencyEntry | None:
        entry = self._entries.get((tenant_id, workspace_id, route, key.value))
        if entry is None:
            return None
        if entry.expires_at <= datetime.now(UTC):
            return None
        return entry

    def put(self, entry: IdempotencyEntry) -> None:
        self._enforce_entries_cap()
        self._entries[(entry.tenant_id, entry.workspace_id, entry.route, entry.key.value)] = entry

    async def lookup(
        self,
        *,
        tenant_id: str,
        route: str,
        key: str,
    ) -> StoredResponse | None:
        """Return the cached response for ``(tenant, route, key)`` or ``None``.

        Returns ``None`` for any of:
        * unknown key,
        * empty key (the caller forgot to pass the header value
          through; mirrors the agent contract that mandates the
          header upstream),
        * expired entry (TTL elapsed),
        * entry written via :meth:`put` with no replay payload.

        Declared ``async`` to match the :class:`IdempotencyStore`
        Protocol; the body is sync (in-memory dict lookup) but the
        coroutine signature lets callers ``await`` either this or the
        Redis variant uniformly.
        """
        if not key:
            return None
        entry = self._replays.get((tenant_id, route, key))
        if entry is None:
            return None
        if entry.expires_at <= datetime.now(UTC):
            return None
        if entry.response_status is None or entry.response_json is None:
            return None
        return StoredResponse(status=entry.response_status, body=entry.response_json)

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
        was present (the helper upstream raises 400 when it isn't,
        but a defensive no-op keeps the store side-effect-free for
        any other caller).

        Declared ``async`` to match the :class:`IdempotencyStore`
        Protocol; see :meth:`lookup` for the rationale.
        """
        if not key:
            return
        # Reuse the IdempotencyEntry shape so a future Postgres-backed
        # implementation can union the two index tables under one row
        # schema. ``response_hash`` + ``job_id`` are unused by replay
        # but kept so the dataclass invariants don't drift.
        entry = IdempotencyEntry(
            tenant_id=tenant_id,
            workspace_id="",
            route=route,
            key=IdempotencyKey(key),
            response_hash="",
            job_id=None,
            expires_at=datetime.now(UTC) + DEFAULT_IDEMPOTENCY_TTL,
            response_status=status,
            response_json=json_body,
        )
        self._enforce_replays_cap()
        self._replays[(tenant_id, route, key)] = entry
