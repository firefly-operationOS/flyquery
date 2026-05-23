"""schema KB tables: snapshots, changes, schema_objects, relations

Revision ID: 0002_schema_kb
Revises: 0001_lifecycle
Create Date: 2026-05-23
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP, UUID

revision = "0002_schema_kb"
down_revision = "0001_lifecycle"


def upgrade() -> None:
    op.create_table(
        "flyquery_schema_snapshots",
        sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", sa.Text, nullable=False),
        sa.Column("workspace_id", UUID(as_uuid=True), nullable=False),
        sa.Column("dataset_id", UUID(as_uuid=True), nullable=False),
        sa.Column(
            "table_id",
            UUID(as_uuid=True),
            sa.ForeignKey("flyquery_tables.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("taken_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("snapshot_hash", sa.Text, nullable=False),
        sa.Column("n_columns", sa.Integer, nullable=False),
        sa.Column("n_rows_estimate", sa.BigInteger, nullable=True),
        sa.Column("n_rows_actual", sa.BigInteger, nullable=True),
        sa.Column("parquet_object_key", sa.Text, nullable=True),
        sa.Column("parquet_byte_size", sa.BigInteger, nullable=True),
        sa.Column("status", sa.Text, nullable=False, server_default=sa.text("'PARTIAL'")),
        sa.Column("failure_json", JSONB, nullable=True),
        sa.Column("triggered_by", sa.Text, nullable=False),
        sa.Column("created_by", sa.Text, nullable=False),
        sa.CheckConstraint("status IN ('PARTIAL','READY','FAILED')", name="ck_snapshots_status"),
        sa.CheckConstraint(
            "triggered_by IN ('USER','AGENT','SCHEDULED','REPARSE')", name="ck_snapshots_trigger"
        ),
    )
    op.create_index(
        "ix_snapshots_tenant_workspace", "flyquery_schema_snapshots", ["tenant_id", "workspace_id"]
    )
    op.create_index("ix_snapshots_table", "flyquery_schema_snapshots", ["table_id"])

    op.create_table(
        "flyquery_schema_changes",
        sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", sa.Text, nullable=False),
        sa.Column("workspace_id", UUID(as_uuid=True), nullable=False),
        sa.Column(
            "table_id",
            UUID(as_uuid=True),
            sa.ForeignKey("flyquery_tables.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "prev_snapshot_id",
            UUID(as_uuid=True),
            sa.ForeignKey("flyquery_schema_snapshots.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "next_snapshot_id",
            UUID(as_uuid=True),
            sa.ForeignKey("flyquery_schema_snapshots.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("column_name", sa.Text, nullable=False),
        sa.Column("change", sa.Text, nullable=False),
        sa.Column("before_json", JSONB, nullable=True),
        sa.Column("after_json", JSONB, nullable=True),
        sa.Column("llm_rationale", sa.Text, nullable=True),
        sa.Column("approved_by", sa.Text, nullable=True),
        sa.Column("approved_at", TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint(
            "change IN ('ADDED','REMOVED','TYPE_CHANGED','RENAMED','RENAMED_CANDIDATE')",
            name="ck_changes_kind",
        ),
    )
    op.create_index("ix_changes_table", "flyquery_schema_changes", ["table_id"])

    op.create_table(
        "flyquery_schema_objects",
        sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", sa.Text, nullable=False),
        sa.Column("workspace_id", UUID(as_uuid=True), nullable=False),
        sa.Column(
            "table_id",
            UUID(as_uuid=True),
            sa.ForeignKey("flyquery_tables.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "snapshot_id",
            UUID(as_uuid=True),
            sa.ForeignKey("flyquery_schema_snapshots.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("kind", sa.Text, nullable=False),
        sa.Column(
            "parent_id",
            UUID(as_uuid=True),
            sa.ForeignKey("flyquery_schema_objects.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("qualified_name", sa.Text, nullable=False),
        sa.Column("data_type", sa.Text, nullable=True),
        sa.Column("is_nullable", sa.Boolean, nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("description_source", sa.Text, nullable=True),
        sa.Column("synonyms_json", JSONB, nullable=True),
        sa.Column("pii_tag", sa.Text, nullable=True),
        sa.Column("pii_source", sa.Text, nullable=True),
        sa.Column("business_owner", sa.Text, nullable=True),
        sa.Column("governance_json", JSONB, nullable=True),
        sa.Column("sample_values_json", JSONB, nullable=True),
        sa.Column("sample_taken_at", TIMESTAMP(timezone=True), nullable=True),
        sa.Column("profile_json", JSONB, nullable=True),
        # embedding column is added in 0006 (pgvector extension is loaded there);
        # this migration only stores the embedding_model name slot.
        sa.Column("embedding_model", sa.Text, nullable=True),
        sa.Column("source_hash", sa.Text, nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        # content_tsv is added in 0006 alongside vector indexes.
        sa.Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("last_seen_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("last_changed_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("kind IN ('TABLE','COLUMN')", name="ck_objects_kind"),
    )
    op.create_index("ix_objects_table", "flyquery_schema_objects", ["table_id"])
    op.create_index("ix_objects_snapshot", "flyquery_schema_objects", ["snapshot_id"])

    op.create_table(
        "flyquery_relations",
        sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", sa.Text, nullable=False),
        sa.Column("workspace_id", UUID(as_uuid=True), nullable=False),
        sa.Column(
            "dataset_id",
            UUID(as_uuid=True),
            sa.ForeignKey("flyquery_datasets.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "from_table_id",
            UUID(as_uuid=True),
            sa.ForeignKey("flyquery_tables.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("from_column_name", sa.Text, nullable=False),
        sa.Column(
            "to_table_id",
            UUID(as_uuid=True),
            sa.ForeignKey("flyquery_tables.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("to_column_name", sa.Text, nullable=False),
        sa.Column("condition", sa.Text, nullable=True),
        sa.Column("kind", sa.Text, nullable=False),
        sa.Column("confidence", sa.Float, nullable=False, server_default=sa.text("0.0")),
        sa.Column("reason", sa.Text, nullable=True),
        sa.Column("status", sa.Text, nullable=False, server_default=sa.text("'PROPOSED'")),
        sa.Column("approved_by", sa.Text, nullable=True),
        sa.Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("kind IN ('HEURISTIC','AGENT_PROPOSED','MANUAL')", name="ck_relations_kind"),
        sa.CheckConstraint("status IN ('PROPOSED','APPROVED','REJECTED')", name="ck_relations_status"),
    )
    op.create_index("ix_relations_dataset", "flyquery_relations", ["dataset_id"])


def downgrade() -> None:
    op.drop_table("flyquery_relations")
    op.drop_table("flyquery_schema_objects")
    op.drop_table("flyquery_schema_changes")
    op.drop_table("flyquery_schema_snapshots")
