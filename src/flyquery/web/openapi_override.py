# Copyright 2026 Firefly Software Solutions Inc
"""Replace FastAPI's auto-generated OpenAPI with pyfly's richer schema.

The pyfly FastAPI adapter registers every controller method behind a
single ``lazy_endpoint(request: Request)`` shim so the DI container can
resolve the controller bean on first hit. The side-effect is that
FastAPI's built-in OpenAPI introspector sees only that shim -- no
request body, no response model, no tags, no docstring.

This module bridges the gap. After the FastAPI app is built we install
a custom ``app.openapi`` callable that:

1. Collects per-route metadata from the original controller signatures
   via pyfly's :class:`ControllerRegistrar.collect_route_metadata`.
2. Renders the spec through pyfly's :class:`OpenAPIGenerator`.
3. Enriches the result with rich global tags (with business +
   technical descriptions) and the OpenAPI ``info`` block we want
   Swagger / ReDoc to display.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI
from pyfly.context.application_context import ApplicationContext
from pyfly.web.adapters.starlette.controller import ControllerRegistrar
from pyfly.web.openapi import OpenAPIGenerator

logger = logging.getLogger(__name__)


#: Maps the auto-derived PascalCase controller tag (``_derive_tag``)
#: to the canonical lowercase kebab-case tag used in the SDK.
#:
#: openapi-generator derives class names from these tags, so:
#: ``"workspaces"``  → ``WorkspacesApi``
#: ``"agent-query"`` → ``AgentQueryApi``
#:
#: Any controller class NOT listed here keeps its auto-derived tag.
TAG_OVERRIDES: dict[str, str] = {
    "Workspaces": "workspaces",
    "Datasets": "datasets",
    "Files": "files",
    "Tables": "tables",
    "SchemaObjects": "schema",
    "SchemaChanges": "schema",
    "Relations": "relations",
    "SemanticMetrics": "semantic",
    "SemanticDimensions": "semantic",
    "Glossary": "glossary",
    "Examples": "examples",
    "Query": "query",
    "Conversations": "conversations",
    "IngestJobs": "ingest",
    "SqlExecute": "sql",
    "TablesDerive": "tables",
    "AgentTokens": "agent-tokens",
    "Version": "meta",
    "AgentVersionController": "meta",
    "AgentVersion": "meta",
    "AgentExamples": "agent-examples",
    "AgentQuery": "agent-query",
    "AgentSqlExecute": "agent-sql",
    "AgentIngestJobs": "ingest",
}

#: Per-tag descriptions rendered on the Swagger / ReDoc landing page.
#: Each entry mixes the business intent with the technical contract so
#: the docs read like a runbook, not just a wire reference.
TAG_DESCRIPTIONS: dict[str, str] = {
    "workspaces": (
        "Multi-tenant workspace management. Each workspace scopes "
        "datasets, schema KB, relations, and agent tokens."
    ),
    "datasets": (
        "Dataset lifecycle (create, fetch, delete). A dataset groups "
        "one or more uploaded files into a named schema boundary."
    ),
    "files": (
        "File upload + re-upload. POST a structured file (CSV, TSV, "
        "XLSX, XLS, ODS, JSON, JSONL, Parquet, Avro, ORC, Arrow, "
        "Feather) to kick off the 10-stage ingestion pipeline. "
        "Re-upload triggers schema-drift detection and annotation transplant."
    ),
    "tables": (
        "Materialised table catalogue. Read table snapshots, column "
        "profiles, and schema change history produced by the ingestion pipeline."
    ),
    "schema": (
        "Schema knowledge-base objects and change proposals. "
        "Column-level AI descriptions, domain metadata, and the diff "
        "stream from re-uploads."
    ),
    "relations": (
        "Cross-table join proposals. Heuristic + AI-proposed foreign-key "
        "candidates with human approve/reject workflow."
    ),
    "semantic": (
        "Semantic layer -- MetricFlow-compatible metrics and dimensions derived from the ingested schema KB."
    ),
    "glossary": "Business glossary terms linked to schema columns and datasets.",
    "examples": "Few-shot Text-to-SQL examples stored in the workspace vector index.",
    "query": (
        "Text-to-SQL query pipeline. Converts natural-language questions "
        "to validated SQL, executes against DuckDB, and returns structured results."
    ),
    "conversations": "Multi-turn conversation sessions backed by the schema KB.",
    "ingest": "Ingestion job tracking and SSE event streaming.",
    "sql": "Direct SQL execution surface (scoped by workspace RLS).",
    "agent-tokens": "Lifecycle management for machine-to-machine agent tokens (create, list, revoke).",
    "agent-examples": "Agent-tier few-shot example management (requires X-Agent-Token).",
    "agent-query": "Agent-tier Text-to-SQL pipeline (requires X-Agent-Token with query scope).",
    "agent-sql": "Agent-tier direct SQL execution (requires X-Agent-Token with sql:execute scope).",
    "meta": (
        "Service identity. Returns deployed CalVer, service name. "
        "The agent-tier variant requires a valid X-Agent-Token."
    ),
}


# Operation-level header parameters injected into every applicable route.
# Defined once as ``components.parameters`` and referenced via ``$ref``
# so the Swagger payload stays small even with 80+ operations.
#
# Tenant/workspace headers are REQUIRED on every operation under
# ``/api/v1/*`` except the agent-tier (which uses ``X-Agent-Token``
# instead). ``Idempotency-Key`` is OPTIONAL but documented on
# mutating verbs (POST / PUT / DELETE) so SDK users see the contract.
# ``X-Correlation-Id`` is OPTIONAL everywhere -- if absent the
# service mints one and echoes it back in the response.

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

# Component-level definitions; routes reference these via ``$ref``.
_HEADER_PARAM_COMPONENTS: dict[str, dict[str, Any]] = {
    "TenantIdHeader": _PARAM_X_TENANT_ID,
    "WorkspaceIdHeader": _PARAM_X_WORKSPACE_ID,
    "AgentTokenHeader": _PARAM_X_AGENT_TOKEN,
    "CorrelationIdHeader": _PARAM_X_CORRELATION_ID,
    "IdempotencyKeyHeader": _PARAM_IDEMPOTENCY_KEY,
}

# Security schemes for the bearer/api-key auth flows.
_SECURITY_SCHEMES: dict[str, dict[str, Any]] = {
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
    """Add header ``$ref`` parameters + security requirements to ``op``."""
    params = op.setdefault("parameters", [])

    # Avoid duplicate injection when the override is called twice.
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


def _enrich_with_headers(spec: dict[str, Any]) -> None:
    """Inject the global header parameters + security schemes into ``spec``."""
    components = spec.setdefault("components", {})

    # Component-level parameter definitions.
    param_components = components.setdefault("parameters", {})
    for name, defn in _HEADER_PARAM_COMPONENTS.items():
        param_components.setdefault(name, defn)

    # Security schemes.
    security_schemes = components.setdefault("securitySchemes", {})
    for name, defn in _SECURITY_SCHEMES.items():
        security_schemes.setdefault(name, defn)

    # Per-operation header injection. We walk every path; for paths
    # under ``/api/v1/agent/*`` we attach the agent-token header,
    # otherwise the tenant + workspace pair.
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


def install_openapi(
    app: FastAPI,
    context: ApplicationContext,
    *,
    title: str,
    version: str,
    description: str,
) -> None:
    """Replace ``app.openapi`` with a pyfly-driven generator.

    Cached after the first call -- FastAPI's own ``openapi()`` method
    caches via ``app.openapi_schema`` and our override follows the
    same contract.
    """
    registrar = ControllerRegistrar()
    generator = OpenAPIGenerator(title=title, version=version, description=description)

    def _custom_openapi() -> dict[str, Any]:
        if app.openapi_schema is not None:
            return app.openapi_schema
        route_metadata = registrar.collect_route_metadata(context)

        # Apply tag overrides: replace pyfly's auto-derived PascalCase tags
        # with the canonical lowercase kebab-case names used in the SDK.
        for meta in route_metadata:
            if meta.tag in TAG_OVERRIDES:
                meta.tag = TAG_OVERRIDES[meta.tag]

        spec = generator.generate(route_metadata=route_metadata)

        # Enrich tag entries with human-readable descriptions.
        if spec.get("tags"):
            for tag in spec["tags"]:
                name = tag.get("name")
                if name and name in TAG_DESCRIPTIONS:
                    tag["description"] = TAG_DESCRIPTIONS[name]

        # Add the deployment's contact info + servers + license to
        # the info block so the docs landing page is usable on its
        # own (without a separate page).
        info = spec.setdefault("info", {})
        info.setdefault(
            "contact",
            {
                "name": "Firefly OperationOS",
                "url": "https://github.com/firefly-operationOS/flyquery",
            },
        )
        info.setdefault(
            "license",
            {
                "name": "Proprietary -- service",
                "url": "https://github.com/firefly-operationOS/flyquery/blob/main/LICENSE",
            },
        )

        # Servers block: lets Swagger UI's "Try it out" send to the
        # right host without manual editing.
        spec.setdefault(
            "servers",
            [
                {"url": "/", "description": "This service"},
            ],
        )

        # Inject the global header parameters (X-Tenant-Id, X-Workspace-Id,
        # X-Agent-Token, X-Correlation-Id, Idempotency-Key) + security
        # schemes onto every operation. Without this the Swagger "Try it
        # out" panel and the openapi-generator clients have no idea the
        # tenant/workspace/agent-token headers are required.
        _enrich_with_headers(spec)

        app.openapi_schema = spec
        logger.info(
            "openapi schema generated (paths=%d, schemas=%d, tags=%d)",
            len(spec.get("paths", {})),
            len((spec.get("components") or {}).get("schemas", {})),
            len(spec.get("tags", [])),
        )
        return spec

    app.openapi = _custom_openapi  # type: ignore[method-assign]
