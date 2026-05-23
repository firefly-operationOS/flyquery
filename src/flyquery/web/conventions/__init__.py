# Copyright 2026 Firefly Software Solutions Inc
"""flyquery HTTP conventions.

This package owns the wire-contract primitives both flyradar and
flyquery agree on (per the 2026-05-21 unification spec):

* header-name constants,
* the ``TenantContext`` request scope,
* the RFC 7807 ``ProblemDetail`` envelope (with a separate ``code``
  field for machine-readable identifiers),
* concrete exception classes that carry that ``code``,
* a FastAPI ``require_tenant_context()`` dependency,
* ``IdempotencyKey`` + store protocol,
* a tenant-safe HTTPX client that auto-propagates the headers on
  outbound service-to-service calls.

The mirror module ``flyradar.web.conventions`` is the sibling copy
and MUST stay byte-for-byte equivalent in shape; changes go through
both repos in lock-step.
"""

from __future__ import annotations

from flyquery.web.conventions.actor import (
    Actor,
    actor_from_agent_token,
    actor_from_jwt_claims,
    decode_jwt_unverified,
)
from flyquery.web.conventions.context import (
    TenantContext,
    current_tenant_context,
    set_tenant_context,
)
from flyquery.web.conventions.deps import (
    require_tenant_context,
    tenant_context_from_headers,
    tenant_context_from_request,
)
from flyquery.web.conventions.errors import ProblemDetail
from flyquery.web.conventions.exceptions import (
    BudgetExceeded,
    FireflyHTTPException,
    IdempotencyKeyConflict,
    InvalidRequest,
    MissingIdempotencyKey,
    MissingTenantContext,
    ResourceNotFound,
    TenantClaimMismatch,
    WorkspaceNotFound,
)
from flyquery.web.conventions.handlers import register_exception_handlers
from flyquery.web.conventions.headers import (
    HEADER_AGENT_TOKEN,
    HEADER_AUTHORIZATION,
    HEADER_CORRELATION_ID,
    HEADER_IDEMPOTENCY_KEY,
    HEADER_TENANT_ID,
    HEADER_WORKSPACE_ID,
)
from flyquery.web.conventions.http_client import (
    MissingOutboundContextError,
    tenant_safe_client,
)
from flyquery.web.conventions.idempotency import (
    IdempotencyEntry,
    IdempotencyKey,
    IdempotencyStore,
    InMemoryIdempotencyStore,
    InvalidIdempotencyKeyError,
    StoredResponse,
)
from flyquery.web.conventions.middleware import TenantContextMiddleware
from flyquery.web.conventions.validation import (
    InvalidSlugError,
    validate_slug,
)

__all__ = [
    # actor
    "Actor",
    "actor_from_agent_token",
    "actor_from_jwt_claims",
    "decode_jwt_unverified",
    # context
    "TenantContext",
    "current_tenant_context",
    "set_tenant_context",
    # deps
    "require_tenant_context",
    "tenant_context_from_headers",
    "tenant_context_from_request",
    # errors
    "ProblemDetail",
    # exceptions
    "BudgetExceeded",
    "FireflyHTTPException",
    "IdempotencyKeyConflict",
    "InvalidRequest",
    "MissingIdempotencyKey",
    "MissingTenantContext",
    "ResourceNotFound",
    "TenantClaimMismatch",
    "WorkspaceNotFound",
    # handlers
    "register_exception_handlers",
    # headers
    "HEADER_AGENT_TOKEN",
    "HEADER_AUTHORIZATION",
    "HEADER_CORRELATION_ID",
    "HEADER_IDEMPOTENCY_KEY",
    "HEADER_TENANT_ID",
    "HEADER_WORKSPACE_ID",
    # http_client
    "MissingOutboundContextError",
    "tenant_safe_client",
    # idempotency
    "IdempotencyEntry",
    "IdempotencyKey",
    "IdempotencyStore",
    "InMemoryIdempotencyStore",
    "InvalidIdempotencyKeyError",
    "StoredResponse",
    # middleware
    "TenantContextMiddleware",
    # validation
    "InvalidSlugError",
    "validate_slug",
]
