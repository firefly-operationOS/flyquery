# Copyright 2026 Firefly Software Solutions Inc
# tests/integration/test_workspaces_crud.py
import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_then_list_workspace() -> None:
    from flyquery.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        r = await c.post(
            "/api/v1/workspaces",
            json={"slug": "alpha", "name": "Alpha"},
            headers={"X-Tenant-Id": "tenant-a", "X-Workspace-Id": "alpha"},
        )
        assert r.status_code == 201, r.text
        ws_id = r.json()["id"]

        r = await c.get(
            "/api/v1/workspaces",
            headers={"X-Tenant-Id": "tenant-a", "X-Workspace-Id": ws_id},
        )
        assert r.status_code == 200
        body = r.json()
        slugs = {item["slug"] for item in body["items"]}
        assert "alpha" in slugs


@pytest.mark.integration
@pytest.mark.asyncio
async def test_purge_workspace_marks_for_tombstone() -> None:
    from flyquery.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        r = await c.post(
            "/api/v1/workspaces",
            json={"slug": "beta", "name": "Beta"},
            headers={"X-Tenant-Id": "tenant-a", "X-Workspace-Id": "beta"},
        )
        ws_id = r.json()["id"]
        r = await c.delete(
            f"/api/v1/workspaces/{ws_id}:purge",
            headers={"X-Tenant-Id": "tenant-a", "X-Workspace-Id": ws_id},
        )
        assert r.status_code == 202   # accepted; purge is async
        # 30-day tombstone — status flips, bytes not yet gone
