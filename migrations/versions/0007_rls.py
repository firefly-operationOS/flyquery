"""RLS: role split (admin / app) + policies on every multi-tenant table

Revision ID: 0007_rls
Revises: 0006_vectors_and_indexes

NOTE: This migration provisions the flyquery_admin + flyquery_app roles
inside the local Postgres container. In production, ops creates the
roles via the deploy bootstrap and this migration is a no-op for the
role-creation step (idempotent CREATE ROLE IF NOT EXISTS via PL/pgSQL).
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0007_rls"
down_revision = "0006_vectors_and_indexes"


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


def upgrade() -> None:
    op.execute(
        """
        DO $$ BEGIN
            IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='flyquery_admin') THEN
                CREATE ROLE flyquery_admin LOGIN PASSWORD 'flyquery_admin' BYPASSRLS;
            END IF;
            IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='flyquery_app') THEN
                CREATE ROLE flyquery_app LOGIN PASSWORD 'flyquery_app' NOSUPERUSER;
            END IF;
        END $$;
        """
    )
    op.execute("GRANT ALL ON ALL TABLES IN SCHEMA public TO flyquery_admin")
    op.execute("GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO flyquery_admin")
    op.execute("GRANT USAGE ON SCHEMA public TO flyquery_app")
    op.execute(
        "GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO flyquery_app"
    )
    op.execute("GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO flyquery_app")

    # Workspaces policy (workspace bound to id)
    op.execute("ALTER TABLE flyquery_workspaces ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE flyquery_workspaces FORCE ROW LEVEL SECURITY")
    op.execute(
        """
        CREATE POLICY pol_workspaces ON flyquery_workspaces
            USING (tenant_id = current_setting('app.tenant_id', true)
                   AND id::text = current_setting('app.workspace_id', true))
        """
    )

    # Agent-tokens policy (tenant-only; workspace check is in code)
    op.execute("ALTER TABLE flyquery_agent_tokens ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE flyquery_agent_tokens FORCE ROW LEVEL SECURITY")
    op.execute(
        """
        CREATE POLICY pol_agent_tokens ON flyquery_agent_tokens
            USING (tenant_id = current_setting('app.tenant_id', true))
        """
    )

    # Standard policy on every multi-tenant table
    for tbl in MULTI_TENANT_TABLES:
        op.execute(f"ALTER TABLE {tbl} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {tbl} FORCE ROW LEVEL SECURITY")
        op.execute(
            f"""
            CREATE POLICY pol_{tbl[len('flyquery_'):]} ON {tbl}
                USING (tenant_id = current_setting('app.tenant_id', true)
                       AND workspace_id::text = current_setting('app.workspace_id', true))
            """
        )


def downgrade() -> None:
    for tbl in MULTI_TENANT_TABLES:
        op.execute(f"DROP POLICY IF EXISTS pol_{tbl[len('flyquery_'):]} ON {tbl}")
        op.execute(f"ALTER TABLE {tbl} NO FORCE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {tbl} DISABLE ROW LEVEL SECURITY")
    op.execute("DROP POLICY IF EXISTS pol_agent_tokens ON flyquery_agent_tokens")
    op.execute("ALTER TABLE flyquery_agent_tokens NO FORCE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE flyquery_agent_tokens DISABLE ROW LEVEL SECURITY")
    op.execute("DROP POLICY IF EXISTS pol_workspaces ON flyquery_workspaces")
    op.execute("ALTER TABLE flyquery_workspaces NO FORCE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE flyquery_workspaces DISABLE ROW LEVEL SECURITY")
    op.execute("REVOKE ALL ON ALL TABLES IN SCHEMA public FROM flyquery_app")
    # Don't DROP ROLE here -- production deploys own the role lifecycle.
