"""lifecycle tables: workspaces, datasets, files, tables

Revision ID: 0001_lifecycle
Revises:
Create Date: 2026-05-23
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP, UUID

revision = "0001_lifecycle"
down_revision = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    op.create_table(
        "flyquery_workspaces",
        sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", sa.Text, nullable=False),
        sa.Column("slug", sa.Text, nullable=False),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("kms_key_uri", sa.Text, nullable=True),
        sa.Column("retention_days", sa.Integer, nullable=True),
        sa.Column("allow_direct_sql", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("default_locale", sa.Text, nullable=False, server_default=sa.text("'en-US'")),
        sa.Column("storage_used_bytes", sa.BigInteger, nullable=False, server_default=sa.text("0")),
        sa.Column("status", sa.Text, nullable=False, server_default=sa.text("'ACTIVE'")),
        sa.Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("metadata_json", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.UniqueConstraint("tenant_id", "slug", name="uq_workspaces_tenant_slug"),
    )
    op.create_index("ix_workspaces_tenant", "flyquery_workspaces", ["tenant_id"])

    op.create_table(
        "flyquery_datasets",
        sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", sa.Text, nullable=False),
        sa.Column(
            "workspace_id",
            UUID(as_uuid=True),
            sa.ForeignKey("flyquery_workspaces.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("drift_policy", sa.Text, nullable=False, server_default=sa.text("'AUTO'")),
        sa.Column("default_locale", sa.Text, nullable=True),
        sa.Column("ingest_policy_json", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("status", sa.Text, nullable=False, server_default=sa.text("'ACTIVE'")),
        sa.Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("metadata_json", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.UniqueConstraint("workspace_id", "name", name="uq_datasets_workspace_name"),
    )
    op.create_index("ix_datasets_tenant_workspace", "flyquery_datasets", ["tenant_id", "workspace_id"])

    op.create_table(
        "flyquery_files",
        sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", sa.Text, nullable=False),
        sa.Column("workspace_id", UUID(as_uuid=True), nullable=False),
        sa.Column(
            "dataset_id",
            UUID(as_uuid=True),
            sa.ForeignKey("flyquery_datasets.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("original_filename", sa.Text, nullable=False),
        sa.Column("file_format", sa.Text, nullable=False),
        sa.Column("compression", sa.Text, nullable=False, server_default=sa.text("'none'")),
        sa.Column("size_bytes", sa.BigInteger, nullable=False),
        sa.Column("content_hash_sha256", sa.String(64), nullable=False),
        sa.Column("object_store_key", sa.Text, nullable=False),
        sa.Column("table_extraction_rules_json", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("uploaded_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("uploaded_by", sa.Text, nullable=False),
        sa.Column("status", sa.Text, nullable=False, server_default=sa.text("'RECEIVED'")),
        sa.Column("error_json", JSONB, nullable=True),
        sa.CheckConstraint(
            "file_format IN ('csv','tsv','xlsx','xls','ods','json','jsonl','parquet','avro','orc','arrow','feather')",
            name="ck_files_format",
        ),
        sa.CheckConstraint(
            "compression IN ('none','gz','zip','bz2')", name="ck_files_compression"
        ),
        sa.CheckConstraint(
            "status IN ('RECEIVED','PARSED','FAILED','DELETED')", name="ck_files_status"
        ),
    )
    op.create_index("ix_files_tenant_workspace", "flyquery_files", ["tenant_id", "workspace_id"])
    op.create_index("ix_files_dataset", "flyquery_files", ["dataset_id"])

    op.create_table(
        "flyquery_tables",
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
            "source_file_id",
            UUID(as_uuid=True),
            sa.ForeignKey("flyquery_files.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("qualified_name", sa.Text, nullable=False),
        sa.Column("kind", sa.Text, nullable=False, server_default=sa.text("'UPLOADED'")),
        sa.Column("sheet_or_json_path", sa.Text, nullable=True),
        sa.Column("current_snapshot_id", UUID(as_uuid=True), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("description_source", sa.Text, nullable=True),
        sa.Column("business_owner", sa.Text, nullable=True),
        sa.Column("governance_json", JSONB, nullable=True),
        sa.Column("locale_override", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("archived_at", TIMESTAMP(timezone=True), nullable=True),
        sa.CheckConstraint("kind IN ('UPLOADED','DERIVED')", name="ck_tables_kind"),
        sa.UniqueConstraint("dataset_id", "name", name="uq_tables_dataset_name"),
    )
    op.create_index("ix_tables_tenant_workspace", "flyquery_tables", ["tenant_id", "workspace_id"])
    op.create_index("ix_tables_dataset", "flyquery_tables", ["dataset_id"])


def downgrade() -> None:
    op.drop_table("flyquery_tables")
    op.drop_table("flyquery_files")
    op.drop_table("flyquery_datasets")
    op.drop_table("flyquery_workspaces")
