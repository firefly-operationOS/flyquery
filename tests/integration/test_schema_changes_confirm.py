# Copyright 2026 Firefly Software Solutions Inc
"""Integration tests for POST /api/v1/schema-changes/{id}:confirm.

Covers:
- RENAMED_CANDIDATE row is flipped to RENAMED with approved_by / approved_at set
- Confirming a non-RENAMED_CANDIDATE row is rejected (422 / 400)
- Confirming a non-existent row returns 404
"""

from __future__ import annotations

import io
import uuid

import pytest
from httpx import ASGITransport, AsyncClient


def _make_client():
    from flyquery.main import app

    return AsyncClient(transport=ASGITransport(app=app), base_url="http://t")


async def _setup_workspace_and_dataset(c, tenant: str, slug: str):
    r = await c.post(
        "/api/v1/workspaces",
        json={"slug": slug, "name": slug},
        headers={"X-Tenant-Id": tenant, "X-Workspace-Id": slug},
    )
    ws_id = r.json()["id"]
    h = {"X-Tenant-Id": tenant, "X-Workspace-Id": ws_id}
    r = await c.post("/api/v1/datasets", json={"name": "confirm-test"}, headers=h)
    ds_id = r.json()["id"]
    return ws_id, ds_id, h


async def _induce_renamed_candidate(c, h, ds_id: str) -> tuple[str, str]:
    """Upload two CSVs where two columns of the same type are removed/added
    (ambiguous rename) so reconcile writes a RENAMED_CANDIDATE row.
    Returns (table_id, change_id).
    """
    # v1: two INTEGER columns — a and b
    csv_v1 = b"x,a,b\n1,10,20\n2,11,21\n"
    r = await c.post(
        f"/api/v1/datasets/{ds_id}/files",
        files={"file": ("ambig.csv", io.BytesIO(csv_v1), "text/csv")},
        headers=h,
    )
    assert r.status_code == 201, r.text
    table_id = r.json()["tables"][0]["table_id"]

    # v2: same x, but a renamed to c and b renamed to d (both INTEGER → ambiguous)
    csv_v2 = b"x,c,d\n1,10,20\n2,11,21\n"
    r = await c.put(
        f"/api/v1/datasets/{ds_id}/tables/{table_id}:upload",
        files={"file": ("ambig.csv", io.BytesIO(csv_v2), "text/csv")},
        headers=h,
    )
    assert r.status_code == 201, r.text

    # Find the RENAMED_CANDIDATE change
    r = await c.get(f"/api/v1/tables/{table_id}/changes", headers=h)
    changes = r.json()["items"]
    candidates = [ch for ch in changes if ch["change"] == "RENAMED_CANDIDATE"]
    assert candidates, f"expected at least one RENAMED_CANDIDATE in {changes}"
    return table_id, candidates[0]["id"]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_rename_candidate_confirm_flips_to_renamed(started_app) -> None:  # noqa: ANN001
    """Happy path: confirm a RENAMED_CANDIDATE → change becomes RENAMED."""
    async with _make_client() as c:
        ws_id, ds_id, h = await _setup_workspace_and_dataset(c, "t-confirm", "ws-confirm")
        _table_id, change_id = await _induce_renamed_candidate(c, h, ds_id)

        r = await c.post(f"/api/v1/schema-changes/{change_id}:confirm", headers=h)
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["change"] == "RENAMED"
        assert body["approved_by"] is not None
        assert body["approved_at"] is not None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_confirm_non_candidate_returns_400(started_app) -> None:  # noqa: ANN001
    """Confirming an ADDED change (not RENAMED_CANDIDATE) must return 400/422."""
    async with _make_client() as c:
        ws_id, ds_id, h = await _setup_workspace_and_dataset(c, "t-conf400", "ws-conf400")

        # First upload only — then add a column
        csv_v1 = b"id,name\n1,Alice\n"
        r = await c.post(
            f"/api/v1/datasets/{ds_id}/files",
            files={"file": ("t.csv", io.BytesIO(csv_v1), "text/csv")},
            headers=h,
        )
        assert r.status_code == 201, r.text
        table_id = r.json()["tables"][0]["table_id"]

        csv_v2 = b"id,name,extra\n1,Alice,foo\n"
        r = await c.put(
            f"/api/v1/datasets/{ds_id}/tables/{table_id}:upload",
            files={"file": ("t.csv", io.BytesIO(csv_v2), "text/csv")},
            headers=h,
        )
        assert r.status_code == 201, r.text

        r = await c.get(f"/api/v1/tables/{table_id}/changes", headers=h)
        added_changes = [ch for ch in r.json()["items"] if ch["change"] == "ADDED"]
        assert added_changes

        change_id = added_changes[0]["id"]
        r = await c.post(f"/api/v1/schema-changes/{change_id}:confirm", headers=h)
        assert r.status_code in {400, 422}, f"expected 400/422 got {r.status_code}: {r.text}"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_confirm_nonexistent_change_returns_404(started_app) -> None:  # noqa: ANN001
    """Confirming a non-existent change_id returns 404."""
    async with _make_client() as c:
        ws_id, ds_id, h = await _setup_workspace_and_dataset(c, "t-conf404", "ws-conf404")
        fake_id = str(uuid.uuid4())
        r = await c.post(f"/api/v1/schema-changes/{fake_id}:confirm", headers=h)
        assert r.status_code == 404, f"expected 404 got {r.status_code}: {r.text}"
