# Copyright 2026 Firefly Software Solutions Inc
"""Integration test: annotation transplant across re-uploads (Task 30).

Verifies that HUMAN-set fields (description, description_source='HUMAN') on a
column survive a re-upload that adds an unrelated column.
"""

from __future__ import annotations

import io

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.integration
@pytest.mark.asyncio
async def test_reupload_preserves_human_annotations(started_app) -> None:  # noqa: ANN001
    """Upload orders.csv, set description on 'total' column, re-upload with
    extra column, verify description survives on the 'total' column.
    """
    from flyquery.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        h = {"X-Tenant-Id": "t-annotate", "X-Workspace-Id": "ws-annotate"}
        r = await c.post(
            "/api/v1/workspaces",
            json={"slug": "ws-annotate", "name": "Annotation Transplant"},
            headers=h,
        )
        assert r.status_code == 201, r.text
        ws_id = r.json()["id"]
        h = {"X-Tenant-Id": "t-annotate", "X-Workspace-Id": ws_id}

        r = await c.post("/api/v1/datasets", json={"name": "orders-ann"}, headers=h)
        ds_id = r.json()["id"]

        # Step 1: Upload orders.csv (3 columns: order_id, customer_id, total)
        csv_v1 = b"order_id,customer_id,total\n1,42,9.95\n2,42,12.50\n3,7,7.00\n"
        r = await c.post(
            f"/api/v1/datasets/{ds_id}/files",
            files={"file": ("orders.csv", io.BytesIO(csv_v1), "text/csv")},
            headers=h,
        )
        assert r.status_code == 201, r.text
        table_id = r.json()["tables"][0]["table_id"]

        # Step 2: Find the schema_object for the 'total' column
        r = await c.get(f"/api/v1/tables/{table_id}/objects", headers=h)
        assert r.status_code == 200, r.text
        objects = r.json()["items"]
        total_col = next(
            (o for o in objects if o["kind"] == "COLUMN" and o["qualified_name"].endswith(".total")),
            None,
        )
        assert total_col is not None, f"total column not found in objects: {objects}"
        total_col_id = total_col["id"]

        # Step 3: PUT description='customer purchase total' with description_source='HUMAN'
        r = await c.put(
            f"/api/v1/schema-objects/{total_col_id}",
            json={"description": "customer purchase total"},
            headers=h,
        )
        assert r.status_code == 200, r.text
        updated = r.json()
        assert updated["description"] == "customer purchase total"
        assert updated["description_source"] == "HUMAN"

        # Step 4: Re-upload orders.csv with an extra column 'status'
        csv_v2 = (
            b"order_id,customer_id,total,status\n1,42,9.95,shipped\n2,42,12.50,pending\n3,7,7.00,processing\n"
        )
        r = await c.put(
            f"/api/v1/datasets/{ds_id}/tables/{table_id}:upload",
            files={"file": ("orders.csv", io.BytesIO(csv_v2), "text/csv")},
            headers=h,
        )
        assert r.status_code == 201, r.text

        # Step 5: Verify the 'total' column in the NEW snapshot still has description
        r = await c.get(f"/api/v1/tables/{table_id}/objects", headers=h)
        assert r.status_code == 200, r.text
        new_objects = r.json()["items"]
        new_total = next(
            (o for o in new_objects if o["kind"] == "COLUMN" and o["qualified_name"].endswith(".total")),
            None,
        )
        assert new_total is not None, f"total column not found after re-upload: {new_objects}"
        assert new_total["description"] == "customer purchase total", (
            f"description lost after re-upload: {new_total}"
        )
        assert new_total["description_source"] == "HUMAN", f"description_source wrong: {new_total}"

        # Also verify that the new column 'status' was added (sanity)
        new_status = next(
            (o for o in new_objects if o["kind"] == "COLUMN" and o["qualified_name"].endswith(".status")),
            None,
        )
        assert new_status is not None, "status column should be present after re-upload"

        # And verify the ADDED change was recorded
        r = await c.get(f"/api/v1/tables/{table_id}/changes", headers=h)
        changes = r.json()["items"]
        assert any(ch["change"] == "ADDED" and ch["column_name"] == "status" for ch in changes), (
            f"expected ADDED:status in {changes}"
        )
