# Copyright 2026 Firefly Software Solutions Inc
"""Inject flyquery's required HTTP headers + security schemes into OpenAPI.

This module lives next to ``openapi_override.py`` but is intentionally
NOT lockstep-tracked with flycanon / flyradar -- the header surface is
flyquery-specific (multi-resource API with tenant + workspace + agent
token contexts and an Idempotency-Key on mutating verbs).

What this adds to ``app.openapi()`` output
-------------------------------------------

* ``components.parameters`` -- five reusable header parameters,
  referenced by every operation via ``$ref`` so the payload stays
  compact:

  - ``TenantIdHeader``       required on every non-agent op
  - ``WorkspaceIdHeader``    required on every non-agent op
  - ``AgentTokenHeader``     required on every ``/api/v1/agent/*`` op
  - ``CorrelationIdHeader``  optional everywhere
  - ``IdempotencyKeyHeader`` optional on POST / PUT / DELETE / PATCH

* ``components.securitySchemes`` -- three apiKey schemes so Swagger
  UI's "Authorize" dialog can prefill the headers globally:

  - ``TenantContext``   -- ``X-Tenant-Id``
  - ``WorkspaceContext``-- ``X-Workspace-Id``
  - ``AgentToken``      -- ``X-Agent-Token``

* Per-operation header parameters + ``security`` requirements. The
  agent tier swaps in ``AgentToken`` and drops the tenant + workspace
  pair (the token's claims encode both).
"""

from __future__ import annotations

from typing import Any

_PARAM_X_TENANT_ID: dict[str, Any] = {
    "name": "X-Tenant-Id",
    "in": "header",
    "required": True,
    "schema": {"type": "string", "minLength": 1, "maxLength": 128},
    "description": (
        "Tenant slug. Required on every non-agent endpoint -- bounds the "
        "row-level security policy and appears in every audit event. "
        "Must match the JWT tenant claim if Authorization is also present."
    ),
    "example": "acme-corp",
}

_PARAM_X_WORKSPACE_ID: dict[str, Any] = {
    "name": "X-Workspace-Id",
    "in": "header",
    "required": True,
    "schema": {"type": "string", "minLength": 1, "maxLength": 128},
    "description": (
        "Workspace identifier. Accepts either the workspace UUID or its "
        "slug -- the slug form lets SDKs avoid carrying UUIDs around. "
        "Used to scope every query, ingest, and schema KB operation."
    ),
    "example": "00000000-0000-0000-0000-000000000001",
}

_PARAM_X_AGENT_TOKEN: dict[str, Any] = {
    "name": "X-Agent-Token",
    "in": "header",
    "required": True,
    "schema": {"type": "string", "minLength": 32},
    "description": (
        "Machine-to-machine bearer token. Replaces X-Tenant-Id and "
        "X-Workspace-Id on agent-tier endpoints -- the token's claims "
        "encode the tenant + workspace + scopes. Issue via "
        "``POST /api/v1/agent-tokens``."
    ),
    "example": "fqt_live_aBcDeF1234567890aBcDeF1234567890",
}

_PARAM_X_CORRELATION_ID: dict[str, Any] = {
    "name": "X-Correlation-Id",
    "in": "header",
    "required": False,
    "schema": {"type": "string", "format": "uuid"},
    "description": (
        "Optional client-supplied correlation id. The service uses this "
        "in every log line and downstream call. If absent the service "
        "mints a new UUID and echoes it in the response header."
    ),
    "example": "550e8400-e29b-41d4-a716-446655440000",
}

_PARAM_IDEMPOTENCY_KEY: dict[str, Any] = {
    "name": "Idempotency-Key",
    "in": "header",
    "required": False,
    "schema": {"type": "string", "minLength": 1, "maxLength": 256},
    "description": (
        "Optional client-supplied idempotency key for mutating "
        "operations. The first request with a key persists its result; "
        "subsequent requests with the same key + same tenant return the "
        "cached response. Keys expire after 24h."
    ),
    "example": "ingest-2026-05-23-abc123",
}

HEADER_PARAM_COMPONENTS: dict[str, dict[str, Any]] = {
    "TenantIdHeader": _PARAM_X_TENANT_ID,
    "WorkspaceIdHeader": _PARAM_X_WORKSPACE_ID,
    "AgentTokenHeader": _PARAM_X_AGENT_TOKEN,
    "CorrelationIdHeader": _PARAM_X_CORRELATION_ID,
    "IdempotencyKeyHeader": _PARAM_IDEMPOTENCY_KEY,
}

SECURITY_SCHEMES: dict[str, dict[str, Any]] = {
    "TenantContext": {
        "type": "apiKey",
        "in": "header",
        "name": "X-Tenant-Id",
        "description": (
            "Non-agent operations require ``X-Tenant-Id`` + ``X-Workspace-Id`` "
            "headers. Treated as an apiKey scheme so Swagger UI's `Authorize` "
            "dialog can prefill them across all requests."
        ),
    },
    "WorkspaceContext": {
        "type": "apiKey",
        "in": "header",
        "name": "X-Workspace-Id",
        "description": "Companion header to TenantContext (accepts UUID or slug).",
    },
    "AgentToken": {
        "type": "apiKey",
        "in": "header",
        "name": "X-Agent-Token",
        "description": (
            "Bearer token for the agent tier. Required on every "
            "``/api/v1/agent/*`` operation. Replaces tenant + workspace "
            "headers -- the token's claims carry both."
        ),
    },
}


def _inject_headers_into_operation(
    op: dict[str, Any],
    *,
    is_agent_route: bool,
    is_mutating: bool,
) -> None:
    """Attach the header ``$ref`` parameters + security requirements to ``op``."""
    params = op.setdefault("parameters", [])
    existing = {(p.get("$ref"), p.get("name")) for p in params}

    def _add_ref(name: str) -> None:
        ref = {"$ref": f"#/components/parameters/{name}"}
        if (ref["$ref"], None) not in existing:
            params.append(ref)
            existing.add((ref["$ref"], None))

    if is_agent_route:
        _add_ref("AgentTokenHeader")
        op.setdefault("security", [{"AgentToken": []}])
    else:
        _add_ref("TenantIdHeader")
        _add_ref("WorkspaceIdHeader")
        op.setdefault("security", [{"TenantContext": [], "WorkspaceContext": []}])

    _add_ref("CorrelationIdHeader")
    if is_mutating:
        _add_ref("IdempotencyKeyHeader")


def enrich_openapi_with_headers(spec: dict[str, Any]) -> None:
    """Mutate ``spec`` in place with flyquery's header + security surface.

    Idempotent -- calling this twice on the same spec is a no-op for
    components and a deduped no-op for per-operation refs.
    """
    components = spec.setdefault("components", {})

    param_components = components.setdefault("parameters", {})
    for name, defn in HEADER_PARAM_COMPONENTS.items():
        param_components.setdefault(name, defn)

    security_schemes = components.setdefault("securitySchemes", {})
    for name, defn in SECURITY_SCHEMES.items():
        security_schemes.setdefault(name, defn)

    for path, path_item in spec.get("paths", {}).items():
        is_agent_route = "/agent/" in path
        for verb, op in path_item.items():
            if verb.lower() not in {"get", "post", "put", "delete", "patch"}:
                continue
            is_mutating = verb.lower() in {"post", "put", "delete", "patch"}
            _inject_headers_into_operation(
                op,
                is_agent_route=is_agent_route,
                is_mutating=is_mutating,
            )
