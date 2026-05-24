# Copyright 2026 Firefly Software Solutions Inc
"""Unit tests for replay_dedup -- the per-handler idempotency wrapper.

Covers cold/hot/missing-key/invalid-key paths so the bulk + agent-tier
write surfaces can safely call it without further validation.
"""

from __future__ import annotations

from typing import Any

import pytest
from pydantic import BaseModel
from starlette.requests import Request

from flyquery.web.conventions.idempotency import InMemoryIdempotencyStore
from flyquery.web.idempotent_handler import (
    IdempotencyKeyMissing,
    replay_dedup,
)


class _Echo(BaseModel):
    message: str


def _make_request(headers: dict[str, str] | None = None) -> Request:
    """Build a minimal ASGI Starlette Request for the helper to read headers."""
    raw_headers = [(k.lower().encode(), v.encode()) for k, v in (headers or {}).items()]
    scope: dict[str, Any] = {
        "type": "http",
        "method": "POST",
        "path": "/api/v1/agent/query",
        "headers": raw_headers,
    }
    return Request(scope)


@pytest.mark.asyncio
async def test_cold_call_invokes_handler_and_records_response() -> None:
    """First call: no cached entry -> handler runs, response is cached."""
    store = InMemoryIdempotencyStore()
    request = _make_request({"Idempotency-Key": "key-abc-001"})
    calls = 0

    async def handler() -> _Echo:
        nonlocal calls
        calls += 1
        return _Echo(message="hello")

    response = await replay_dedup(
        request=request,
        store=store,
        tenant_id="acme",
        route="POST /api/v1/agent/query",
        handler=handler,
        status_code=201,
    )

    assert calls == 1
    assert response.status_code == 201
    cached = await store.lookup(tenant_id="acme", route="POST /api/v1/agent/query", key="key-abc-001")
    assert cached is not None
    assert cached.status == 201
    assert cached.body == {"message": "hello"}


@pytest.mark.asyncio
async def test_warm_call_returns_cached_without_invoking_handler() -> None:
    """Replay: cached entry exists -> handler must NOT run."""
    store = InMemoryIdempotencyStore()
    await store.record_response(
        tenant_id="acme",
        route="POST /api/v1/agent/query",
        key="key-abc-002",
        status=200,
        json_body={"message": "cached"},
    )
    request = _make_request({"Idempotency-Key": "key-abc-002"})

    async def handler() -> _Echo:
        raise AssertionError("handler must NOT run on replay")

    response = await replay_dedup(
        request=request,
        store=store,
        tenant_id="acme",
        route="POST /api/v1/agent/query",
        handler=handler,
        status_code=201,
    )

    assert response.status_code == 200
    import json as _json

    assert _json.loads(response.body) == {"message": "cached"}


@pytest.mark.asyncio
async def test_missing_key_passthrough_when_optional() -> None:
    """No header + require_key=False -> handler runs, no caching."""
    store = InMemoryIdempotencyStore()
    request = _make_request({})
    calls = 0

    async def handler() -> _Echo:
        nonlocal calls
        calls += 1
        return _Echo(message="no-cache")

    response = await replay_dedup(
        request=request,
        store=store,
        tenant_id="acme",
        route="POST /api/v1/foo",
        handler=handler,
        require_key=False,
    )

    assert calls == 1
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_missing_key_raises_when_required() -> None:
    """No header + require_key=True -> IdempotencyKeyMissing (400)."""
    store = InMemoryIdempotencyStore()
    request = _make_request({})

    async def handler() -> _Echo:
        raise AssertionError("handler must NOT run when key required+missing")

    with pytest.raises(IdempotencyKeyMissing):
        await replay_dedup(
            request=request,
            store=store,
            tenant_id="acme",
            route="POST /api/v1/agent/query",
            handler=handler,
            require_key=True,
        )


@pytest.mark.asyncio
async def test_invalid_key_charset_raises() -> None:
    """Idempotency-Key with bad charset -> bubbles up the validation error."""
    from flyquery.web.conventions.idempotency import InvalidIdempotencyKeyError

    store = InMemoryIdempotencyStore()
    request = _make_request({"Idempotency-Key": "bad key with spaces"})

    async def handler() -> _Echo:
        raise AssertionError("handler must NOT run on invalid key")

    with pytest.raises(InvalidIdempotencyKeyError):
        await replay_dedup(
            request=request,
            store=store,
            tenant_id="acme",
            route="POST /api/v1/foo",
            handler=handler,
        )


@pytest.mark.asyncio
async def test_handler_returning_dict_is_supported() -> None:
    """Bulk endpoints often return list/dict envelopes -- replay_dedup handles them."""
    store = InMemoryIdempotencyStore()
    request = _make_request({"Idempotency-Key": "key-abc-003"})

    async def handler() -> dict[str, Any]:
        return {"items": [{"id": 1}, {"id": 2}], "total": 2}

    response = await replay_dedup(
        request=request,
        store=store,
        tenant_id="acme",
        route="POST /api/v1/foo:bulk",
        handler=handler,
    )

    assert response.status_code == 200
    cached = await store.lookup(tenant_id="acme", route="POST /api/v1/foo:bulk", key="key-abc-003")
    assert cached is not None
    assert cached.body == {"items": [{"id": 1}, {"id": 2}], "total": 2}
