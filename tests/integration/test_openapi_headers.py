# Copyright 2026 Firefly Software Solutions Inc
"""Verify the OpenAPI override injects the required headers + security schemes.

Without this enrichment the Swagger UI ``Try it out`` panel and the
openapi-generator clients have no idea ``X-Tenant-Id`` / ``X-Workspace-Id``
/ ``X-Agent-Token`` are required.
"""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient


def _header_refs(op: dict) -> set[str]:
    return {p.get("$ref", "") for p in op.get("parameters", []) if "$ref" in p}


@pytest.mark.integration
@pytest.mark.asyncio
async def test_openapi_components_define_header_parameters() -> None:
    from flyquery.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        r = await c.get("/openapi.json")
        assert r.status_code == 200
        spec = r.json()

        comp = spec.get("components", {})
        params = comp.get("parameters", {})
        # All five header parameters must be declared as reusable components.
        assert "TenantIdHeader" in params
        assert "WorkspaceIdHeader" in params
        assert "AgentTokenHeader" in params
        assert "CorrelationIdHeader" in params
        assert "IdempotencyKeyHeader" in params

        # Each must declare ``in: header``, be flagged required where
        # appropriate, and carry a human-readable description + example.
        tenant_h = params["TenantIdHeader"]
        assert tenant_h["in"] == "header"
        assert tenant_h["required"] is True
        assert "tenant" in tenant_h["description"].lower()
        assert "example" in tenant_h

        agent_h = params["AgentTokenHeader"]
        assert agent_h["in"] == "header"
        assert agent_h["required"] is True

        idem_h = params["IdempotencyKeyHeader"]
        assert idem_h["required"] is False

        # Security schemes must be present.
        sec = comp.get("securitySchemes", {})
        assert "TenantContext" in sec
        assert "WorkspaceContext" in sec
        assert "AgentToken" in sec
        assert sec["TenantContext"]["in"] == "header"
        assert sec["AgentToken"]["name"] == "X-Agent-Token"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_openapi_non_agent_get_has_tenant_workspace_correlation() -> None:
    from flyquery.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        r = await c.get("/openapi.json")
        spec = r.json()
        op = spec["paths"]["/api/v1/workspaces"]["get"]
        refs = _header_refs(op)
        assert "#/components/parameters/TenantIdHeader" in refs
        assert "#/components/parameters/WorkspaceIdHeader" in refs
        assert "#/components/parameters/CorrelationIdHeader" in refs
        # GET is not mutating -> no idempotency header
        assert "#/components/parameters/IdempotencyKeyHeader" not in refs
        # Security must require both tenant + workspace context
        sec = op.get("security") or []
        assert any("TenantContext" in s for s in sec)
        assert any("WorkspaceContext" in s for s in sec)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_openapi_mutating_op_has_idempotency_header() -> None:
    from flyquery.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        r = await c.get("/openapi.json")
        spec = r.json()
        op = spec["paths"]["/api/v1/workspaces"]["post"]
        refs = _header_refs(op)
        # POST -> Idempotency-Key is documented as optional
        assert "#/components/parameters/IdempotencyKeyHeader" in refs


@pytest.mark.integration
@pytest.mark.asyncio
async def test_openapi_agent_op_swaps_to_agent_token_security() -> None:
    from flyquery.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        r = await c.get("/openapi.json")
        spec = r.json()
        # Pick any agent-tier path
        agent_paths = [p for p in spec["paths"] if "/agent/" in p]
        assert agent_paths, "expected at least one /api/v1/agent/* path"
        for path in agent_paths:
            for verb, op in spec["paths"][path].items():
                if verb.lower() not in {"get", "post", "put", "delete"}:
                    continue
                refs = _header_refs(op)
                # Agent routes carry the agent-token header, NOT the
                # tenant/workspace pair.
                assert "#/components/parameters/AgentTokenHeader" in refs, path
                assert "#/components/parameters/TenantIdHeader" not in refs, path
                assert "#/components/parameters/WorkspaceIdHeader" not in refs, path
                sec = op.get("security") or []
                assert any("AgentToken" in s for s in sec), path
