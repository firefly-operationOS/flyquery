# Copyright 2026 Firefly Software Solutions Inc
"""Tenant-context binding middleware.

Pyfly's ``@rest_controller`` parameter resolver bypasses FastAPI's
``Depends`` chain, so :func:`require_tenant_context` (which binds the
request-scoped ContextVar) does not run for pyfly-mounted routes.
Controllers reach for :func:`tenant_context_from_request` instead --
that helper builds a :class:`TenantContext` but does **not** bind it.

The downstream RLS scheme (installed by
:func:`flyquery.web.conventions.db.install_tenant_guc_hook`) listens
to SQLAlchemy's ``after_begin`` event and reads
:func:`current_tenant_context` to issue ``SET LOCAL app.tenant_id`` /
``app.workspace_id`` on every transaction. Without a bound ContextVar
those GUCs are never set; Postgres ``current_setting('app.tenant_id',
true)`` returns the empty string; every RLS policy in migration
``0013_rls_policies`` fails to match; and any read through a
non-``BYPASSRLS`` role returns zero rows. In dev/test the connection
role has ``BYPASSRLS`` so the bug is silently masked.

This middleware closes that gap by binding the ContextVar from
request headers BEFORE the route runs (and therefore before any DB
session opens) and resetting it after the response. Routes that
require tenant context still raise :class:`MissingTenantContext` at
their own validation point; the middleware is intentionally
permissive on missing/invalid headers so unauthenticated surfaces
(``/health``, ``/version``, ``/api/v1/setup/status``) keep working.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from starlette.middleware.base import BaseHTTPMiddleware

from flyquery.web.conventions.context import set_tenant_context
from flyquery.web.conventions.deps import tenant_context_from_headers
from flyquery.web.conventions.exceptions import (
    FireflyHTTPException,
    MissingTenantContext,
)
from flyquery.web.conventions.headers import (
    HEADER_AGENT_TOKEN,
    HEADER_AUTHORIZATION,
    HEADER_CORRELATION_ID,
    HEADER_TENANT_ID,
    HEADER_WORKSPACE_ID,
)

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from starlette.requests import Request
    from starlette.responses import Response


class TenantContextMiddleware(BaseHTTPMiddleware):
    """Bind :class:`TenantContext` to the request-scoped ContextVar.

    Runs early in the request lifecycle so the ContextVar is set
    before any DB session opens. The SQLAlchemy ``after_begin``
    listener (installed by
    :func:`flyquery.web.conventions.db.install_tenant_guc_hook`)
    reads the ContextVar to issue ``SET LOCAL app.tenant_id`` /
    ``app.workspace_id`` per transaction. RLS policies in migration
    ``0013_rls_policies`` rely on those GUCs.

    Skips binding when tenant/workspace headers are absent or invalid
    (health checks, ``/api/v1/setup/status``, ``/api/v1/version``,
    OpenAPI docs). Routes that require tenant context will still
    raise :class:`MissingTenantContext` at their own validation point
    -- the middleware is permissive on purpose.

    The reset lives in a ``finally`` block so a route exception still
    unbinds the ContextVar; without that, an exception that escapes
    the route would leak the prior request's scope into whatever
    task picked the contextvars-copy from the event loop next.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        token = None
        try:
            ctx = tenant_context_from_headers(
                x_tenant_id=request.headers.get(HEADER_TENANT_ID),
                x_workspace_id=request.headers.get(HEADER_WORKSPACE_ID),
                x_correlation_id=request.headers.get(HEADER_CORRELATION_ID),
                authorization=request.headers.get(HEADER_AUTHORIZATION),
                x_agent_token=request.headers.get(HEADER_AGENT_TOKEN),
            )
            token = set_tenant_context(ctx)
        except MissingTenantContext:
            # No / invalid tenant headers -- let the route decide
            # whether tenant context is required. Health, setup,
            # version, and OpenAPI docs all flow through here.
            pass
        except FireflyHTTPException:
            # A JWT tenant-claim mismatch (or any other 4xx convention
            # exception raised by tenant_context_from_headers) must
            # not be swallowed -- the route's downstream call would
            # rebuild the ctx and raise the same error to the FastAPI
            # exception handler. Leaving ``token = None`` is enough;
            # the route invocation will surface the problem.
            pass

        try:
            return await call_next(request)
        finally:
            if token is not None:
                token.var.reset(token.token)
