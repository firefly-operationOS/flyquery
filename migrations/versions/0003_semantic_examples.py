"""semantic layer + examples

Revision ID: 0003_semantic_examples
Revises: 0002_schema_kb
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP, UUID

revision = "0003_semantic_examples"
down_revision = "0002_schema_kb"


def upgrade() -> None:
    for tbl in ("flyquery_semantic_metrics", "flyquery_semantic_dimensions"):
        op.create_table(
            tbl,
            sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
            sa.Column("tenant_id", sa.Text, nullable=False),
            sa.Column("workspace_id", UUID(as_uuid=True), nullable=False),
            sa.Column(
                "dataset_id",
                UUID(as_uuid=True),
                sa.ForeignKey("flyquery_datasets.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("name", sa.Text, nullable=False),
            sa.Column("label", sa.Text, nullable=True),
            sa.Column("description", sa.Text, nullable=True),
            sa.Column("definition_yaml", sa.Text, nullable=False),
            sa.Column("compiled_sql_template", sa.Text, nullable=True),
            sa.Column("metric_type", sa.Text, nullable=False, server_default=sa.text("'SIMPLE'")),
            sa.Column("status", sa.Text, nullable=False, server_default=sa.text("'DRAFT'")),
            sa.Column("current_version", sa.Integer, nullable=False, server_default=sa.text("1")),
            sa.Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
            sa.Column("updated_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
            sa.UniqueConstraint("dataset_id", "name", name=f"uq_{tbl}_dataset_name"),
            sa.CheckConstraint(
                "metric_type IN ('SIMPLE','RATIO','DERIVED','CUMULATIVE')",
                name=f"ck_{tbl}_type",
            ),
            sa.CheckConstraint(
                "status IN ('DRAFT','PUBLISHED','RETIRED')", name=f"ck_{tbl}_status"
            ),
        )

    op.create_table(
        "flyquery_semantic_versions",
        sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", sa.Text, nullable=False),
        sa.Column("workspace_id", UUID(as_uuid=True), nullable=False),
        sa.Column("kind", sa.Text, nullable=False),  # 'metric' | 'dimension'
        sa.Column("parent_id", UUID(as_uuid=True), nullable=False),  # FK polymorphic; enforced in code
        sa.Column("version", sa.Integer, nullable=False),
        sa.Column("definition_yaml", sa.Text, nullable=False),
        sa.Column("compiled_sql_template", sa.Text, nullable=True),
        sa.Column("created_by", sa.Text, nullable=False),
        sa.Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("kind", "parent_id", "version", name="uq_versions_kind_parent_version"),
    )

    op.create_table(
        "flyquery_glossary_terms",
        sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", sa.Text, nullable=False),
        sa.Column("workspace_id", UUID(as_uuid=True), nullable=False),
        sa.Column("term", sa.Text, nullable=False),
        sa.Column("definition", sa.Text, nullable=False),
        sa.Column("synonyms_json", JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("tags_json", JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("related_columns_json", JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("related_metrics_json", JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("workspace_id", "term", name="uq_glossary_workspace_term"),
    )

    op.create_table(
        "flyquery_examples",
        sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", sa.Text, nullable=False),
        sa.Column("workspace_id", UUID(as_uuid=True), nullable=False),
        sa.Column(
            "dataset_id",
            UUID(as_uuid=True),
            sa.ForeignKey("flyquery_datasets.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("question", sa.Text, nullable=False),
        sa.Column("generated_sql", sa.Text, nullable=False),
        sa.Column("normalised_sql", sa.Text, nullable=False),
        sa.Column("source", sa.Text, nullable=False),
        sa.Column("quality", sa.Text, nullable=False, server_default=sa.text("'PROPOSED'")),
        # vector column added in 0006 alongside other pgvector columns.
        sa.Column("citations_json", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_by", sa.Text, nullable=False),
        sa.Column("last_used_at", TIMESTAMP(timezone=True), nullable=True),
        sa.Column("usage_count", sa.BigInteger, nullable=False, server_default=sa.text("0")),
        sa.CheckConstraint(
            "source IN ('USER_CURATED','AGENT_LEARNED')", name="ck_examples_source"
        ),
        sa.CheckConstraint(
            "quality IN ('PROPOSED','APPROVED','REJECTED')", name="ck_examples_quality"
        ),
    )
    op.create_index("ix_examples_dataset", "flyquery_examples", ["dataset_id"])


def downgrade() -> None:
    op.drop_table("flyquery_examples")
    op.drop_table("flyquery_glossary_terms")
    op.drop_table("flyquery_semantic_versions")
    op.drop_table("flyquery_semantic_dimensions")
    op.drop_table("flyquery_semantic_metrics")
