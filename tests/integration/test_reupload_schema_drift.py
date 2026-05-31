# Copyright 2024-2026 Firefly Software Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Integration tests for PUT /datasets/{ds}/tables/{table_id}:upload (re-upload).

Verifies:
- Re-upload creates a new snapshot (N snapshots after N uploads)
- current_snapshot_id always points to the latest READY snapshot
- Schema changes (ADDED, REMOVED, TYPE_CHANGED) are correctly recorded
"""

from __future__ import annotations

import io

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture
async def _base_upload(started_app):  # noqa: ANN001
    """Set up workspace, dataset, and initial upload; yield (client, h, ds_id, table_id)."""
    from flyquery.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        r = await c.post(
            "/api/v1/workspaces",
            json={"slug": "reuptest", "name": "Reupload Test"},
            headers={"X-Tenant-Id": "tenant-reup", "X-Workspace-Id": "reuptest"},
        )
        ws_id = r.json()["id"]
        h = {"X-Tenant-Id": "tenant-reup", "X-Workspace-Id": ws_id}

        r = await c.post("/api/v1/datasets", json={"name": "drift-demo"}, headers=h)
        ds_id = r.json()["id"]

        csv_v1 = b"order_id,customer_id,total\n1,42,9.95\n2,42,12.50\n"
        r = await c.post(
            f"/api/v1/datasets/{ds_id}/files",
            files={"file": ("orders.csv", io.BytesIO(csv_v1), "text/csv")},
            headers=h,
        )
        assert r.status_code == 201, r.text
        table_id = r.json()["tables"][0]["table_id"]
        yield c, h, ds_id, table_id


@pytest.mark.integration
@pytest.mark.asyncio
async def test_reupload_adds_column(started_app) -> None:  # noqa: ANN001
    from flyquery.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        r = await c.post(
            "/api/v1/workspaces",
            json={"slug": "reupadd", "name": "Reupload Add"},
            headers={"X-Tenant-Id": "tenant-reupadd", "X-Workspace-Id": "reupadd"},
        )
        ws_id = r.json()["id"]
        h = {"X-Tenant-Id": "tenant-reupadd", "X-Workspace-Id": ws_id}

        r = await c.post("/api/v1/datasets", json={"name": "drift"}, headers=h)
        ds_id = r.json()["id"]

        # v1: 3 columns
        csv_v1 = b"order_id,customer_id,total\n1,42,9.95\n2,7,12.50\n"
        r = await c.post(
            f"/api/v1/datasets/{ds_id}/files",
            files={"file": ("orders.csv", io.BytesIO(csv_v1), "text/csv")},
            headers=h,
        )
        assert r.status_code == 201, r.text
        table_id = r.json()["tables"][0]["table_id"]

        # v2: 4 columns (status added)
        csv_v2 = b"order_id,customer_id,total,status\n1,42,9.95,shipped\n2,7,12.50,pending\n"
        r = await c.put(
            f"/api/v1/datasets/{ds_id}/tables/{table_id}:upload",
            files={"file": ("orders.csv", io.BytesIO(csv_v2), "text/csv")},
            headers=h,
        )
        assert r.status_code == 201, r.text
        reup = r.json()
        assert reup["n_columns"] == 4
        snap2_id = reup["snapshot_id"]

        # Snapshots: should be 2 now
        r = await c.get(f"/api/v1/tables/{table_id}/snapshots", headers=h)
        snaps = r.json()["items"]
        assert len(snaps) == 2

        # current_snapshot_id should point to snap2
        r = await c.get(f"/api/v1/tables/{table_id}", headers=h)
        assert str(r.json()["current_snapshot_id"]) == snap2_id

        # Changes: one ADDED
        r = await c.get(f"/api/v1/tables/{table_id}/changes", headers=h)
        changes = r.json()["items"]
        assert any(ch["change"] == "ADDED" and ch["column_name"] == "status" for ch in changes), (
            f"expected ADDED:status in {changes}"
        )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_reupload_removes_column(started_app) -> None:  # noqa: ANN001
    from flyquery.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        r = await c.post(
            "/api/v1/workspaces",
            json={"slug": "reuprm", "name": "Reupload Remove"},
            headers={"X-Tenant-Id": "tenant-reuprm", "X-Workspace-Id": "reuprm"},
        )
        ws_id = r.json()["id"]
        h = {"X-Tenant-Id": "tenant-reuprm", "X-Workspace-Id": ws_id}

        r = await c.post("/api/v1/datasets", json={"name": "drift2"}, headers=h)
        ds_id = r.json()["id"]

        # v1: 4 columns
        csv_v1 = b"id,name,email,region\n1,Alice,a@b.com,EU\n2,Bob,b@c.com,US\n"
        r = await c.post(
            f"/api/v1/datasets/{ds_id}/files",
            files={"file": ("customers.csv", io.BytesIO(csv_v1), "text/csv")},
            headers=h,
        )
        assert r.status_code == 201, r.text
        table_id = r.json()["tables"][0]["table_id"]

        # v2: 3 columns (email removed)
        csv_v2 = b"id,name,region\n1,Alice,EU\n2,Bob,US\n"
        r = await c.put(
            f"/api/v1/datasets/{ds_id}/tables/{table_id}:upload",
            files={"file": ("customers.csv", io.BytesIO(csv_v2), "text/csv")},
            headers=h,
        )
        assert r.status_code == 201, r.text

        r = await c.get(f"/api/v1/tables/{table_id}/changes", headers=h)
        changes = r.json()["items"]
        assert any(ch["change"] == "REMOVED" and ch["column_name"] == "email" for ch in changes), (
            f"expected REMOVED:email in {changes}"
        )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_removed_column_marked_inactive(started_app) -> None:  # noqa: ANN001
    """Removed column's schema_objects row must have is_active=false after re-upload."""
    import sqlalchemy as sa
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

    from flyquery.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        r = await c.post(
            "/api/v1/workspaces",
            json={"slug": "reuprminact", "name": "Reupload Remove Inactive"},
            headers={"X-Tenant-Id": "tenant-reuprminact", "X-Workspace-Id": "reuprminact"},
        )
        ws_id = r.json()["id"]
        h = {"X-Tenant-Id": "tenant-reuprminact", "X-Workspace-Id": ws_id}

        r = await c.post("/api/v1/datasets", json={"name": "inactive-test"}, headers=h)
        ds_id = r.json()["id"]

        csv_v1 = b"id,name,email\n1,Alice,a@b.com\n2,Bob,b@c.com\n"
        r = await c.post(
            f"/api/v1/datasets/{ds_id}/files",
            files={"file": ("cols.csv", io.BytesIO(csv_v1), "text/csv")},
            headers=h,
        )
        assert r.status_code == 201, r.text
        table_id = r.json()["tables"][0]["table_id"]

        # Re-upload without `email`
        csv_v2 = b"id,name\n1,Alice\n2,Bob\n"
        r = await c.put(
            f"/api/v1/datasets/{ds_id}/tables/{table_id}:upload",
            files={"file": ("cols.csv", io.BytesIO(csv_v2), "text/csv")},
            headers=h,
        )
        assert r.status_code == 201, r.text
        r.json()["snapshot_id"]

        # The PREVIOUS snapshot's `email` row should be is_active=false.
        # We need the first snapshot id — GET /tables/{id}/snapshots
        r = await c.get(f"/api/v1/tables/{table_id}/snapshots", headers=h)
        snaps = r.json()["items"]
        # snaps ordered by taken_at; first one is the original
        prev_snap_id = snaps[0]["id"]

        # Check directly via DB (admin URL bypasses RLS so we can query freely).
        import os

        admin_url = os.environ["FLYQUERY_DATABASE_URL_ADMIN"]
        # Admin URL is sync (+psycopg); convert to async (+asyncpg)
        async_admin_url = admin_url.replace("+psycopg", "+asyncpg").replace("+psycopg2", "+asyncpg")
        engine = create_async_engine(async_admin_url)
        async with AsyncSession(engine) as session:
            result = await session.execute(
                sa.text(
                    """
                    SELECT is_active FROM flyquery_schema_objects
                    WHERE snapshot_id = :snap AND kind = 'COLUMN'
                      AND qualified_name LIKE '%.email'
                    """
                ),
                {"snap": prev_snap_id},
            )
            rows = result.all()
        await engine.dispose()

        assert rows, "expected to find email column in prev snapshot"
        assert all(row[0] is False for row in rows), (
            f"expected is_active=false for removed email column, got {rows}"
        )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_type_changed_recorded(started_app) -> None:  # noqa: ANN001
    """TYPE_CHANGED entry is written when a column's data type changes across uploads."""
    from flyquery.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        r = await c.post(
            "/api/v1/workspaces",
            json={"slug": "reuptc", "name": "Reupload TypeChange"},
            headers={"X-Tenant-Id": "tenant-reuptc", "X-Workspace-Id": "reuptc"},
        )
        ws_id = r.json()["id"]
        h = {"X-Tenant-Id": "tenant-reuptc", "X-Workspace-Id": ws_id}

        r = await c.post("/api/v1/datasets", json={"name": "tc-demo"}, headers=h)
        ds_id = r.json()["id"]

        # v1: total as integer
        csv_v1 = b"order_id,total\n1,10\n2,20\n3,30\n"
        r = await c.post(
            f"/api/v1/datasets/{ds_id}/files",
            files={"file": ("orders.csv", io.BytesIO(csv_v1), "text/csv")},
            headers=h,
        )
        assert r.status_code == 201, r.text
        table_id = r.json()["tables"][0]["table_id"]

        # v2: total as float
        csv_v2 = b"order_id,total\n1,10.5\n2,20.75\n3,30.0\n"
        r = await c.put(
            f"/api/v1/datasets/{ds_id}/tables/{table_id}:upload",
            files={"file": ("orders.csv", io.BytesIO(csv_v2), "text/csv")},
            headers=h,
        )
        assert r.status_code == 201, r.text

        r = await c.get(f"/api/v1/tables/{table_id}/changes", headers=h)
        changes = r.json()["items"]
        type_changes = [
            ch for ch in changes if ch["change"] == "TYPE_CHANGED" and ch["column_name"] == "total"
        ]
        assert type_changes, f"expected TYPE_CHANGED:total in {changes}"
        tc = type_changes[0]
        assert tc["before_json"] is not None
        assert tc["after_json"] is not None
