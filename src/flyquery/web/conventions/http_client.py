# Copyright 2026 Firefly Software Solutions Inc
"""``tenant_safe_client`` -- HTTPX client that auto-injects firefly headers.

Reads ``current_tenant_context()`` and adds:
- ``X-Tenant-Id``
- ``X-Workspace-Id``
- ``X-Correlation-Id``

Fails closed if the context is not bound (``MissingOutboundContextError``).
Caller-supplied headers win over auto-injected ones.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

import httpx

from flyquery.web.conventions.context import current_tenant_context
from flyquery.web.conventions.headers import (
    HEADER_CORRELATION_ID,
    HEADER_TENANT_ID,
    HEADER_WORKSPACE_ID,
)


class MissingOutboundContextError(RuntimeError):
    """Raised when a tenant-safe call is attempted without a bound context."""


class _TenantSafeTransport(httpx.AsyncBaseTransport):
    def __init__(self, inner: httpx.AsyncBaseTransport) -> None:
        self._inner = inner

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        ctx = current_tenant_context()
        if ctx is None:
            raise MissingOutboundContextError(
                "tenant_safe_client requires a bound TenantContext "
                "(call set_tenant_context() or run inside a FastAPI "
                "endpoint that uses require_tenant_context())."
            )
        # Only inject when the caller hasn't already set the header.
        if HEADER_TENANT_ID not in request.headers:
            request.headers[HEADER_TENANT_ID] = ctx.tenant_id
        if HEADER_WORKSPACE_ID not in request.headers:
            request.headers[HEADER_WORKSPACE_ID] = ctx.workspace_id
        if HEADER_CORRELATION_ID not in request.headers:
            request.headers[HEADER_CORRELATION_ID] = ctx.correlation_id
        return await self._inner.handle_async_request(request)

    async def aclose(self) -> None:
        await self._inner.aclose()


@asynccontextmanager
async def tenant_safe_client(
    *,
    base_url: str,
    timeout: float | httpx.Timeout = 30.0,
    **kwargs: Any,
) -> AsyncGenerator[httpx.AsyncClient]:
    """Yield an ``httpx.AsyncClient`` that auto-propagates firefly headers."""
    inner_transport = httpx.AsyncHTTPTransport()
    transport = _TenantSafeTransport(inner_transport)
    async with httpx.AsyncClient(
        base_url=base_url,
        timeout=timeout,
        transport=transport,
        **kwargs,
    ) as client:
        yield client
