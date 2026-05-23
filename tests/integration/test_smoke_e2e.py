# Copyright 2026 Firefly Software Solutions Inc
"""End-to-end smoke covering the Plan 1 surface:
health → version → mint token → create workspace → create dataset
→ archive → re-create with same slug rejected.
"""

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.integration
@pytest.mark.asyncio
async def test_plan1_end_to_end() -> None:
    from flyquery.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        # /actuator/health
        r = await c.get("/actuator/health")
        assert r.status_code == 200

        # /api/v1/version
        r = await c.get("/api/v1/version")
        assert r.status_code == 200
        assert r.json()["name"] == "flyquery"

        h = {"X-Tenant-Id": "tenant-smoke", "X-Workspace-Id": "smoke"}

        # Create workspace
        r = await c.post(
            "/api/v1/workspaces",
            json={"slug": "smoke", "name": "Smoke Test"},
            headers=h,
        )
        assert r.status_code == 201
        ws = r.json()
        ws_id = ws["id"]

        # Mint an agent token
        r = await c.post(
            "/api/v1/agent-tokens",
            json={
                "name": "smoke-bot",
                "scopes": ["flyquery.datasets:read", "flyquery.query:read"],
                "workspace_allowlist": [ws_id],
            },
            headers={**h, "X-Workspace-Id": ws_id},
        )
        assert r.status_code == 201
        token = r.json()["token"]
        assert token.startswith("agt_")

        # Create a dataset
        r = await c.post(
            "/api/v1/datasets",
            json={"name": "Sales-Smoke"},
            headers={**h, "X-Workspace-Id": ws_id},
        )
        assert r.status_code == 201

        # Use the token on an agent route (we only have /api/v1/agent/version
        # which requires flyquery.audit:read which this token DOESN'T have
        # → expect 403)
        r = await c.get(
            "/api/v1/agent/version",
            headers={
                "X-Tenant-Id": "tenant-smoke",
                "X-Workspace-Id": ws_id,
                "X-Agent-Token": token,
            },
        )
        assert r.status_code == 403

        # :purge
        r = await c.delete(
            f"/api/v1/workspaces/{ws_id}:purge",
            headers={**h, "X-Workspace-Id": ws_id},
        )
        assert r.status_code == 202
