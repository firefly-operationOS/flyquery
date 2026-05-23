# Copyright 2026 Firefly Software Solutions Inc
"""Integration tests for agent token mint / verify / scope-gate surface."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

# Shared tenant/workspace for all tests in this module.
_TENANT = "tenant-tokens"
_WORKSPACE_SLUG = "tok-ws"
_HEADERS: dict = {}  # populated by test_mint_token_and_use_on_agent_route
_WS_ID: str = ""
_AUDIT_TOKEN: str = ""
_DATASET_TOKEN: str = ""


@pytest.mark.integration
@pytest.mark.asyncio
async def test_mint_token_and_use_on_agent_route() -> None:
    global _WS_ID, _AUDIT_TOKEN, _DATASET_TOKEN

    from flyquery.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        # Create a workspace to anchor the allowlist tests.
        r = await c.post(
            "/api/v1/workspaces",
            json={"slug": _WORKSPACE_SLUG, "name": "Token-Test"},
            headers={"X-Tenant-Id": _TENANT, "X-Workspace-Id": _WORKSPACE_SLUG},
        )
        assert r.status_code == 201, r.text
        _WS_ID = str(r.json()["id"])

        # Mint a token with audit:read scope (used by test_agent_route test).
        r = await c.post(
            "/api/v1/agent-tokens",
            json={
                "name": "audit-bot",
                "scopes": ["flyquery.audit:read"],
                "workspace_allowlist": [_WS_ID],
            },
            headers={"X-Tenant-Id": _TENANT, "X-Workspace-Id": _WS_ID},
        )
        assert r.status_code == 201, r.text
        _AUDIT_TOKEN = r.json()["token"]
        assert _AUDIT_TOKEN.startswith("agt_")

        # Mint a token with only dataset:read (NOT audit:read).
        r = await c.post(
            "/api/v1/agent-tokens",
            json={
                "name": "dataset-bot",
                "scopes": ["flyquery.datasets:read"],
                "workspace_allowlist": [_WS_ID],
            },
            headers={"X-Tenant-Id": _TENANT, "X-Workspace-Id": _WS_ID},
        )
        assert r.status_code == 201, r.text
        _DATASET_TOKEN = r.json()["token"]
        assert _DATASET_TOKEN.startswith("agt_")

        # Negative: unknown scope rejected at mint time.
        r = await c.post(
            "/api/v1/agent-tokens",
            json={"name": "bad", "scopes": ["flyquery.query:bogus"]},
            headers={"X-Tenant-Id": _TENANT, "X-Workspace-Id": _WS_ID},
        )
        # Pydantic field_validator raises pre-controller -> 422 (RFC 4918,
        # standard for semantic validation failures). 400 is the legacy
        # shape from before scope validation moved to the DTO.
        assert r.status_code in (400, 422), r.text
        body = r.json()
        # RFC 7807 nests the envelope under ``error``; accept both shapes.
        code = (
            body.get("code")
            or body.get("error", {}).get("code", "").lower()
            or ""
        )
        assert code.lower() in ("invalid_scope", "validation_error"), body
        # Per-field error code lives inside the validation context.
        errors = body.get("error", {}).get("context", {}).get("errors", [])
        assert any(e.get("type") == "invalid_scope" for e in errors), body


@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_route_requires_valid_token_and_scope() -> None:
    from flyquery.main import app

    assert _WS_ID, "test_mint_token_and_use_on_agent_route must run first"

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        tenant_headers = {"X-Tenant-Id": _TENANT, "X-Workspace-Id": _WS_ID}

        # 1) No token → 401
        r = await c.get("/api/v1/agent/version", headers=tenant_headers)
        assert r.status_code == 401, r.text

        # 2) Valid token but missing the required scope (datasets:read, not audit:read) → 403
        r = await c.get(
            "/api/v1/agent/version",
            headers={**tenant_headers, "X-Agent-Token": _DATASET_TOKEN},
        )
        assert r.status_code == 403, r.text

        # 3) Valid token with flyquery.audit:read → 200
        r = await c.get(
            "/api/v1/agent/version",
            headers={**tenant_headers, "X-Agent-Token": _AUDIT_TOKEN},
        )
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["name"] == "flyquery"
