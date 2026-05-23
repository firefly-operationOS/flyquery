"""Add unique constraint on flyquery_relations for UPSERT support.

Revision ID: 0009_relations_unique_constraint
Revises: 0008_purging_status
"""

from alembic import op

revision = "0009_relations_unique_constraint"
down_revision = "0008_purging_status"


def upgrade():
    op.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS uq_relations_pair
        ON flyquery_relations (from_table_id, from_column_name, to_table_id, to_column_name)
        """
    )


def downgrade():
    op.execute("DROP INDEX IF EXISTS uq_relations_pair")
