"""add PURGING status

Revision ID: 0008_purging_status
Revises: 0007_rls
"""
from alembic import op

revision = "0008_purging_status"
down_revision = "0007_rls"


def upgrade():
    op.execute("ALTER TABLE flyquery_workspaces DROP CONSTRAINT IF EXISTS ck_workspaces_status")
    op.execute(
        "ALTER TABLE flyquery_workspaces ADD CONSTRAINT ck_workspaces_status "
        "CHECK (status IN ('ACTIVE','ARCHIVED','PURGING'))"
    )


def downgrade():
    op.execute("ALTER TABLE flyquery_workspaces DROP CONSTRAINT IF EXISTS ck_workspaces_status")
