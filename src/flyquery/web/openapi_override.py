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
    "workspaces": "Multi-tenant workspace management. Each workspace scopes datasets, schema KB, relations, and agent tokens.",
    "datasets": "Dataset lifecycle (create, fetch, delete). A dataset groups one or more uploaded files into a named schema boundary.",
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
        "Semantic layer -- MetricFlow-compatible metrics and dimensions "
        "derived from the ingested schema KB."
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

        app.openapi_schema = spec
        logger.info(
            "openapi schema generated (paths=%d, schemas=%d, tags=%d)",
            len(spec.get("paths", {})),
            len((spec.get("components") or {}).get("schemas", {})),
            len(spec.get("tags", [])),
        )
        return spec

    app.openapi = _custom_openapi  # type: ignore[method-assign]
