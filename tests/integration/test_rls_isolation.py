# Copyright 2026 Firefly Software Solutions Inc
"""RLS forces tenant + workspace isolation across every multi-tenant table."""

from __future__ import annotations

import os
import uuid

import pytest
import sqlalchemy as sa

MULTI_TENANT_TABLES = (
    "flyquery_datasets",
    "flyquery_files",
    "flyquery_tables",
    "flyquery_schema_snapshots",
    "flyquery_schema_changes",
    "flyquery_schema_objects",
    "flyquery_relations",
    "flyquery_semantic_metrics",
    "flyquery_semantic_dimensions",
    "flyquery_semantic_versions",
    "flyquery_glossary_terms",
    "flyquery_examples",
    "flyquery_queries",
    "flyquery_query_results",
    "flyquery_conversations",
    "flyquery_conversation_turns",
    "flyquery_audit_events",
    "flyquery_cost_events",
    "flyquery_ingest_jobs",
    "flyquery_ingest_events",
)


@pytest.fixture
def app_engine() -> sa.engine.Engine:
    url = os.environ["FLYQUERY_DATABASE_URL"].replace("+asyncpg", "+psycopg")
    return sa.create_engine(url)


def _seed_workspace(admin_url: str, tenant: str, workspace_slug: str) -> tuple[uuid.UUID, uuid.UUID]:
    eng = sa.create_engine(admin_url)
    with eng.begin() as conn:
        ws_id = conn.execute(
            sa.text("INSERT INTO flyquery_workspaces(tenant_id,slug,name) VALUES(:t,:s,:n) RETURNING id"),
            {"t": tenant, "s": workspace_slug, "n": workspace_slug},
        ).scalar_one()
        ds_id = conn.execute(
            sa.text(
                "INSERT INTO flyquery_datasets(tenant_id,workspace_id,name) VALUES(:t,:w,:n) RETURNING id"
            ),
            {"t": tenant, "w": ws_id, "n": "ds-1"},
        ).scalar_one()
    return ws_id, ds_id


@pytest.mark.integration
def test_app_role_sees_only_bound_tenant_workspace(app_engine: sa.engine.Engine) -> None:
    admin_url = os.environ["FLYQUERY_DATABASE_URL_ADMIN"]
    ws_a, ds_a = _seed_workspace(admin_url, "tenant-a", "wsA")
    ws_b, ds_b = _seed_workspace(admin_url, "tenant-b", "wsB")

    with app_engine.connect() as conn:
        conn.execute(sa.text("SET LOCAL app.tenant_id = 'tenant-a'"))
        conn.execute(sa.text(f"SET LOCAL app.workspace_id = '{ws_a}'"))
        rows = conn.execute(sa.text("SELECT id FROM flyquery_datasets")).fetchall()
        assert {r.id for r in rows} == {ds_a}, "tenant-a should not see tenant-b rows"

    with app_engine.connect() as conn:
        conn.execute(sa.text("SET LOCAL app.tenant_id = 'tenant-b'"))
        conn.execute(sa.text(f"SET LOCAL app.workspace_id = '{ws_b}'"))
        rows = conn.execute(sa.text("SELECT id FROM flyquery_datasets")).fetchall()
        assert {r.id for r in rows} == {ds_b}


@pytest.mark.integration
def test_rls_blocks_cross_workspace_insert(app_engine: sa.engine.Engine) -> None:
    admin_url = os.environ["FLYQUERY_DATABASE_URL_ADMIN"]
    ws_a, _ = _seed_workspace(admin_url, "tenant-a", "wsA-2")
    ws_b, _ = _seed_workspace(admin_url, "tenant-b", "wsB-2")

    with app_engine.connect() as conn:
        conn.execute(sa.text("SET LOCAL app.tenant_id = 'tenant-a'"))
        conn.execute(sa.text(f"SET LOCAL app.workspace_id = '{ws_a}'"))
        # USING implies WITH CHECK (memory: rls_using_implies_with_check)
        with pytest.raises(sa.exc.ProgrammingError):
            conn.execute(
                sa.text(
                    "INSERT INTO flyquery_datasets(tenant_id,workspace_id,name) "
                    "VALUES('tenant-b', :wb, 'cross-tenant-leak')"
                ),
                {"wb": ws_b},
            )


# ---------------------------------------------------------------------------
# Task 25 — RLS isolation end-to-end through workspace + dataset controllers
# ---------------------------------------------------------------------------


@pytest.mark.integration
@pytest.mark.asyncio
async def test_workspace_rls_isolation_through_controller() -> None:
    """POST /workspaces twice (different tenants) — GET with tenant-A headers must
    only return tenant-A's workspace, never tenant-B's."""
    from httpx import ASGITransport, AsyncClient

    from flyquery.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        r_a = await c.post(
            "/api/v1/workspaces",
            json={"slug": "rls-ws-a", "name": "RLS WS A"},
            headers={"X-Tenant-Id": "rls-tenant-a", "X-Workspace-Id": "00000000-0000-0000-0000-000000000010"},
        )
        assert r_a.status_code == 201, r_a.text
        ws_a_id = r_a.json()["id"]

        r_b = await c.post(
            "/api/v1/workspaces",
            json={"slug": "rls-ws-b", "name": "RLS WS B"},
            headers={"X-Tenant-Id": "rls-tenant-b", "X-Workspace-Id": "00000000-0000-0000-0000-000000000011"},
        )
        assert r_b.status_code == 201, r_b.text
        ws_b_id = r_b.json()["id"]

        # Tenant-A GET must only see their own workspace
        r = await c.get(
            "/api/v1/workspaces",
            headers={"X-Tenant-Id": "rls-tenant-a", "X-Workspace-Id": ws_a_id},
        )
        assert r.status_code == 200
        ids_for_a = {item["id"] for item in r.json()["items"]}
        assert ws_a_id in ids_for_a, "tenant-a must see own workspace"
        assert ws_b_id not in ids_for_a, "tenant-a must not see tenant-b workspace"

        # Tenant-B GET must only see their own workspace
        r = await c.get(
            "/api/v1/workspaces",
            headers={"X-Tenant-Id": "rls-tenant-b", "X-Workspace-Id": ws_b_id},
        )
        assert r.status_code == 200
        ids_for_b = {item["id"] for item in r.json()["items"]}
        assert ws_b_id in ids_for_b, "tenant-b must see own workspace"
        assert ws_a_id not in ids_for_b, "tenant-b must not see tenant-a workspace"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_dataset_rls_isolation_through_controller() -> None:
    """POST /datasets twice in different tenant workspaces — each tenant's GET must
    only return their own dataset."""
    from httpx import ASGITransport, AsyncClient

    from flyquery.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        # Create workspace + dataset for rls-tenant-c
        r = await c.post(
            "/api/v1/workspaces",
            json={"slug": "rls-ds-ws-c", "name": "RLS DS WS C"},
            headers={"X-Tenant-Id": "rls-tenant-c", "X-Workspace-Id": "00000000-0000-0000-0000-000000000020"},
        )
        assert r.status_code == 201, r.text
        ws_c_id = r.json()["id"]

        r = await c.post(
            "/api/v1/datasets",
            json={"name": "DS for C"},
            headers={"X-Tenant-Id": "rls-tenant-c", "X-Workspace-Id": ws_c_id},
        )
        assert r.status_code == 201, r.text
        ds_c_id = r.json()["id"]

        # Create workspace + dataset for rls-tenant-d
        r = await c.post(
            "/api/v1/workspaces",
            json={"slug": "rls-ds-ws-d", "name": "RLS DS WS D"},
            headers={"X-Tenant-Id": "rls-tenant-d", "X-Workspace-Id": "00000000-0000-0000-0000-000000000021"},
        )
        assert r.status_code == 201, r.text
        ws_d_id = r.json()["id"]

        r = await c.post(
            "/api/v1/datasets",
            json={"name": "DS for D"},
            headers={"X-Tenant-Id": "rls-tenant-d", "X-Workspace-Id": ws_d_id},
        )
        assert r.status_code == 201, r.text
        ds_d_id = r.json()["id"]

        # Tenant-C GET /datasets must only see their dataset
        r = await c.get(
            "/api/v1/datasets",
            headers={"X-Tenant-Id": "rls-tenant-c", "X-Workspace-Id": ws_c_id},
        )
        assert r.status_code == 200
        ids_for_c = {item["id"] for item in r.json()["items"]}
        assert ds_c_id in ids_for_c, "tenant-c must see own dataset"
        assert ds_d_id not in ids_for_c, "tenant-c must not see tenant-d dataset"

        # Tenant-D GET /datasets must only see their dataset
        r = await c.get(
            "/api/v1/datasets",
            headers={"X-Tenant-Id": "rls-tenant-d", "X-Workspace-Id": ws_d_id},
        )
        assert r.status_code == 200
        ids_for_d = {item["id"] for item in r.json()["items"]}
        assert ds_d_id in ids_for_d, "tenant-d must see own dataset"
        assert ds_c_id not in ids_for_d, "tenant-d must not see tenant-c dataset"
