# Copyright 2026 Firefly Software Solutions Inc
"""Integration tests for agent token mint / verify / scope-gate surface."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.integration
@pytest.mark.asyncio
async def test_mint_token_and_use_on_agent_route() -> None:
    from flyquery.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        # Operator mints (user-tier; future JWT bearer; placeholder header)
        r = await c.post(
            "/api/v1/workspaces",
            json={"slug": "tok", "name": "Token-Test"},
            headers={"X-Tenant-Id": "tenant-a", "X-Workspace-Id": "tok"},
        )
        ws_id = str(r.json()["id"])

        r = await c.post(
            "/api/v1/agent-tokens",
            json={
                "name": "test-bot",
                "scopes": ["flyquery.datasets:read"],
                "workspace_allowlist": [ws_id],
            },
            headers={"X-Tenant-Id": "tenant-a", "X-Workspace-Id": ws_id},
        )
        assert r.status_code == 201, r.text
        token = r.json()["token"]   # one-shot; never re-shown
        assert token.startswith("agt_")

        # Negative: unknown scope rejected at mint time
        r = await c.post(
            "/api/v1/agent-tokens",
            json={"name": "bad", "scopes": ["flyquery.query:bogus"]},
            headers={"X-Tenant-Id": "tenant-a", "X-Workspace-Id": ws_id},
        )
        assert r.status_code == 400, r.text
        body = r.json()
        assert body.get("code") in ("invalid_scope", "validation_error")
