# Copyright 2026 Firefly Software Solutions Inc
# tests/integration/test_datasets_crud.py
import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_then_list_dataset() -> None:
    from flyquery.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        # First create a workspace
        r = await c.post(
            "/api/v1/workspaces",
            json={"slug": "ds-ws-1", "name": "DS Workspace 1"},
            headers={"X-Tenant-Id": "tenant-ds", "X-Workspace-Id": "00000000-0000-0000-0000-000000000001"},
        )
        assert r.status_code == 201, r.text
        ws_id = r.json()["id"]

        # Create a dataset inside that workspace
        r = await c.post(
            "/api/v1/datasets",
            json={"name": "Sales 2026"},
            headers={"X-Tenant-Id": "tenant-ds", "X-Workspace-Id": ws_id},
        )
        assert r.status_code == 201, r.text
        ds = r.json()
        assert ds["name"] == "Sales 2026"
        assert ds["drift_policy"] == "AUTO"
        assert ds["status"] == "ACTIVE"
        ds_id = ds["id"]

        # List datasets for that workspace
        r = await c.get(
            "/api/v1/datasets",
            headers={"X-Tenant-Id": "tenant-ds", "X-Workspace-Id": ws_id},
        )
        assert r.status_code == 200
        body = r.json()
        assert any(item["id"] == ds_id for item in body["items"])


@pytest.mark.integration
@pytest.mark.asyncio
async def test_archive_dataset() -> None:
    from flyquery.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        # Create workspace
        r = await c.post(
            "/api/v1/workspaces",
            json={"slug": "ds-ws-2", "name": "DS Workspace 2"},
            headers={"X-Tenant-Id": "tenant-ds2", "X-Workspace-Id": "00000000-0000-0000-0000-000000000002"},
        )
        assert r.status_code == 201, r.text
        ws_id = r.json()["id"]

        # Create dataset
        r = await c.post(
            "/api/v1/datasets",
            json={"name": "Archive Me"},
            headers={"X-Tenant-Id": "tenant-ds2", "X-Workspace-Id": ws_id},
        )
        assert r.status_code == 201, r.text
        ds_id = r.json()["id"]

        # Archive it
        r = await c.delete(
            f"/api/v1/datasets/{ds_id}",
            headers={"X-Tenant-Id": "tenant-ds2", "X-Workspace-Id": ws_id},
        )
        assert r.status_code == 200, r.text
        assert r.json()["status"] == "ARCHIVED"
