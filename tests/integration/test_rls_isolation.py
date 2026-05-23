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
            sa.text(
                "INSERT INTO flyquery_workspaces(tenant_id,slug,name) "
                "VALUES(:t,:s,:n) RETURNING id"
            ),
            {"t": tenant, "s": workspace_slug, "n": workspace_slug},
        ).scalar_one()
        ds_id = conn.execute(
            sa.text(
                "INSERT INTO flyquery_datasets(tenant_id,workspace_id,name) "
                "VALUES(:t,:w,:n) RETURNING id"
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
