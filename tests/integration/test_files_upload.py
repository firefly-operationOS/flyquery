# Copyright 2026 Firefly Software Solutions Inc
"""Integration tests for Phase B — upload + synchronous ingestion pipeline.

7-step scenario:
1. Upload orders.csv → POST /datasets/{id}/files → 201 + file_id + 1 table
2. GET /datasets/{id}/tables → table visible with current_snapshot_id
3. GET /tables/{id} → columns=3, description=NULL (DescribeAgent ships Phase E)
4. Re-upload with an extra column → PUT /datasets/{ds}/tables/{id}:upload → 201
5. GET /tables/{id}/snapshots → 2 snapshots, current_snapshot_id points to newer
6. GET /tables/{id}/changes → 1 ADDED entry for the new column
"""

from __future__ import annotations

import io

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.integration
@pytest.mark.asyncio
async def test_upload_csv_first_time_creates_file_and_table() -> None:
    from flyquery.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        r = await c.post(
            "/api/v1/workspaces",
            json={"slug": "uptest", "name": "Upload Test"},
            headers={"X-Tenant-Id": "tenant-upload", "X-Workspace-Id": "uptest"},
        )
        assert r.status_code == 201, r.text
        ws_id = r.json()["id"]
        h = {"X-Tenant-Id": "tenant-upload", "X-Workspace-Id": ws_id}

        r = await c.post("/api/v1/datasets", json={"name": "demo-upload"}, headers=h)
        assert r.status_code == 201, r.text
        ds_id = r.json()["id"]

        csv_body = b"order_id,customer_id,total\n1,42,9.95\n2,42,12.50\n3,7,7.00\n"
        r = await c.post(
            f"/api/v1/datasets/{ds_id}/files",
            files={"file": ("orders.csv", io.BytesIO(csv_body), "text/csv")},
            headers=h,
        )
        assert r.status_code == 201, r.text
        body = r.json()
        assert "file_id" in body
        assert len(body["tables"]) == 1
        tbl = body["tables"][0]
        assert tbl["n_columns"] == 3
        table_id = tbl["table_id"]

        # Step 2: list tables on dataset
        r = await c.get(f"/api/v1/datasets/{ds_id}/tables", headers=h)
        assert r.status_code == 200, r.text
        items = r.json()["items"]
        assert len(items) >= 1
        found = next((t for t in items if str(t["id"]) == table_id), None)
        assert found is not None, f"table {table_id} not in {items}"
        assert found["current_snapshot_id"] is not None

        # Step 3: get single table detail
        r = await c.get(f"/api/v1/tables/{table_id}", headers=h)
        assert r.status_code == 200, r.text
        detail = r.json()
        assert detail["n_columns"] == 3
        # description is NULL at this stage (DescribeAgent ships Phase E)
        assert detail.get("description") is None

        # Step 4: re-upload with an extra column
        csv_v2 = b"order_id,customer_id,total,status\n1,42,9.95,shipped\n2,42,12.50,pending\n"
        r = await c.put(
            f"/api/v1/datasets/{ds_id}/tables/{table_id}:upload",
            files={"file": ("orders.csv", io.BytesIO(csv_v2), "text/csv")},
            headers=h,
        )
        assert r.status_code == 201, r.text
        v2_body = r.json()
        snap2_id = v2_body["snapshot_id"]

        # Step 5: list snapshots
        r = await c.get(f"/api/v1/tables/{table_id}/snapshots", headers=h)
        assert r.status_code == 200, r.text
        snaps = r.json()["items"]
        assert len(snaps) == 2

        # current_snapshot_id should point to the newer one
        r = await c.get(f"/api/v1/tables/{table_id}", headers=h)
        assert r.status_code == 200, r.text
        assert str(r.json()["current_snapshot_id"]) == snap2_id

        # Step 6: list schema changes
        r = await c.get(f"/api/v1/tables/{table_id}/changes", headers=h)
        assert r.status_code == 200, r.text
        changes = r.json()["items"]
        added = [ch for ch in changes if ch["change"] == "ADDED"]
        assert any(ch["column_name"] == "status" for ch in added), (
            f"expected ADDED:status in {changes}"
        )
