# Copyright 2026 Firefly Software Solutions Inc
"""Per-handler ``Idempotency-Key`` replay-dedup wrapper.

The :class:`IdempotencyStore` Protocol in
:mod:`flyquery.web.conventions.idempotency` has been wired into the DI
container for two releases but no controller had been calling it -- so
every mutating endpoint (especially the agent-tier writes
``/agent/query``, ``/agent/sql:execute``, ``/agent/examples``,
``/agent-tokens``, ``/datasets/{id}/files:bulk``, ``/query:batch``) was
silently replay-vulnerable. A spec-declared header was an empty
promise.

This module provides the missing glue: :func:`replay_dedup` wraps a
handler callable, takes the request, the store, the routing label, and:

1. If the ``Idempotency-Key`` header is present, validates its charset
   (1-128 ``[A-Za-z0-9_-]`` chars). Bad charset raises
   :class:`InvalidIdempotencyKeyError` (mapped to ``400`` by the
   conventions error handler).
2. Calls :meth:`IdempotencyStore.lookup` -- if a cached response
   exists for ``(tenant, route, key)``, returns it directly without
   invoking the handler.
3. Otherwise invokes the handler, serialises the response (Pydantic
   model -> ``.model_dump(mode="json")``; dict / list passed
   through), persists it via :meth:`IdempotencyStore.record_response`
   under the configured TTL, and returns the wire body.
4. If the caller passed ``require_key=True`` (agent-tier policy) and
   the header is missing, raises :class:`IdempotencyKeyMissing`
   (mapped to ``400``). User-tier endpoints can leave it ``False`` so
   the header is optional but honoured when present.

The helper returns a Starlette :class:`JSONResponse` instead of the
underlying Pydantic model so pyfly's route resolver passes it through
verbatim -- avoiding double-serialisation that would otherwise mutate
field ordering and break ``ETag`` parity for replayed calls.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import JSONResponse

from flyquery.web.conventions.exceptions import MissingIdempotencyKey
from flyquery.web.conventions.headers import HEADER_IDEMPOTENCY_KEY
from flyquery.web.conventions.idempotency import (
    IdempotencyKey,
    IdempotencyStore,
)

# Re-export under a more verb-suggestive alias so the call sites read
# cleanly (``raise IdempotencyKeyMissing()`` vs the noun form).
IdempotencyKeyMissing = MissingIdempotencyKey


HandlerResult = BaseModel | dict[str, Any] | list[Any] | None
"""Allowed return types for handlers wrapped in :func:`replay_dedup`."""


def _serialise(result: HandlerResult) -> dict[str, Any] | list[Any]:
    """Convert a handler's return value to a JSON-ready payload.

    Pydantic models are dumped with ``mode="json"`` so datetime, UUID,
    and Decimal serialise the same way pyfly would. Bare dict / list
    are passed through (callers occasionally need to return envelopes
    that don't have a corresponding model).
    """
    if result is None:
        # 204-style empty body -- represent as ``{}`` so JSON round-trip
        # is well-defined for replay caching.
        return {}
    if isinstance(result, BaseModel):
        return result.model_dump(mode="json")
    if isinstance(result, (dict, list)):
        return result
    raise TypeError(
        f"replay_dedup handler returned unsupported type {type(result).__name__}; "
        "return a Pydantic model, dict, list, or None."
    )


async def replay_dedup(
    *,
    request: Request,
    store: IdempotencyStore,
    tenant_id: str,
    route: str,
    handler: Callable[[], Awaitable[HandlerResult]],
    status_code: int = 200,
    require_key: bool = False,
) -> JSONResponse:
    """Run ``handler`` with idempotency-key replay-dedup semantics.

    Parameters
    ----------
    request:
        The Starlette request -- only the ``Idempotency-Key`` header is
        read.
    store:
        The pluggable :class:`IdempotencyStore`. In production this is
        Redis-backed; tests + dev use the in-memory variant.
    tenant_id:
        Namespace for the cache key. Per the agent contract, replays
        are tenant-scoped (a tenant cannot replay another tenant's
        cached response).
    route:
        A stable routing label (e.g. ``"POST /api/v1/agent/query"``).
        Used as the second leg of the cache key so the same key value
        can be reused across different endpoints without collision.
    handler:
        Async no-arg callable that produces the response model.
    status_code:
        HTTP status for the freshly-produced response. Replays preserve
        the *original* status from the cached entry.
    require_key:
        If ``True`` and the header is absent, raise
        :class:`IdempotencyKeyMissing` (400). Agent-tier writes set
        this; user-tier endpoints generally leave it optional so
        legacy clients keep working.

    Returns
    -------
    A :class:`starlette.responses.JSONResponse` with the (cached or
    freshly produced) body.
    """
    raw_key = request.headers.get(HEADER_IDEMPOTENCY_KEY, "").strip()

    if not raw_key:
        if require_key:
            raise IdempotencyKeyMissing(
                "Idempotency-Key header is required for this endpoint. "
                "Send a unique 1-128 char [A-Za-z0-9_-] value to make "
                "the request safely retryable."
            )
        # No key -> no caching, no validation, just run.
        body = _serialise(await handler())
        return JSONResponse(status_code=status_code, content=body)

    # Validate charset eagerly so we fail with a typed 400 BEFORE
    # invoking the handler (which may be expensive -- e.g. a 4-agent
    # NL->SQL pipeline). ``IdempotencyKey.__post_init__`` raises
    # ``InvalidIdempotencyKeyError`` which the conventions handler
    # table maps to 400.
    IdempotencyKey(raw_key)

    cached = await store.lookup(tenant_id=tenant_id, route=route, key=raw_key)
    if cached is not None:
        return JSONResponse(status_code=cached.status, content=cached.body)

    body = _serialise(await handler())
    await store.record_response(
        tenant_id=tenant_id,
        route=route,
        key=raw_key,
        status=status_code,
        json_body=body,
    )
    return JSONResponse(status_code=status_code, content=body)


__all__ = ["IdempotencyKeyMissing", "replay_dedup"]
