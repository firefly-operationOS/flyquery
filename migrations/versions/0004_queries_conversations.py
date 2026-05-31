# Copyright 2024-2026 Firefly Software Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""queries + conversations

Revision ID: 0004_queries_conversations
Revises: 0003_semantic_examples
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, NUMERIC, TIMESTAMP, UUID

revision = "0004_queries_conversations"
down_revision = "0003_semantic_examples"


def upgrade() -> None:
    op.create_table(
        "flyquery_queries",
        sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", sa.Text, nullable=False),
        sa.Column("workspace_id", UUID(as_uuid=True), nullable=False),
        sa.Column(
            "dataset_id",
            UUID(as_uuid=True),
            sa.ForeignKey("flyquery_datasets.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("question", sa.Text, nullable=False),
        sa.Column("prior_turn_ids", ARRAY(UUID(as_uuid=True)), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("table_id_snapshot_pins_json", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("semantic_path_taken", sa.Text, nullable=True),
        sa.Column("candidates_json", JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("chosen_candidate_index", sa.Integer, nullable=True),
        sa.Column("executed_sql", sa.Text, nullable=True),
        sa.Column("ast_classification", sa.Text, nullable=True),
        sa.Column("execution_engine", sa.Text, nullable=False, server_default=sa.text("'duckdb'")),
        sa.Column("execution_status", sa.Text, nullable=True),
        sa.Column("retries", sa.Integer, nullable=False, server_default=sa.text("0")),
        sa.Column("row_count", sa.Integer, nullable=True),
        sa.Column("elapsed_ms", sa.Integer, nullable=True),
        sa.Column("cost_cents", NUMERIC, nullable=False, server_default=sa.text("0")),
        sa.Column("clarification_emitted", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("clarification_json", JSONB, nullable=True),
        sa.Column("pii_findings_json", JSONB, nullable=True),
        sa.Column("error_json", JSONB, nullable=True),
        sa.Column("model_grounding", sa.Text, nullable=True),
        sa.Column("model_generation", sa.Text, nullable=True),
        sa.Column("model_critic", sa.Text, nullable=True),
        sa.Column("model_explainer", sa.Text, nullable=True),
        sa.Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("finalised_at", TIMESTAMP(timezone=True), nullable=True),
        sa.CheckConstraint(
            "semantic_path_taken IS NULL OR semantic_path_taken IN ('SEMANTIC_LAYER','SYNTHESIS','HYBRID')",
            name="ck_queries_semantic_path",
        ),
        sa.CheckConstraint(
            "execution_status IS NULL OR execution_status IN ('OK','REFINED_OK','FAILED','REJECTED_BY_FIREWALL')",
            name="ck_queries_status",
        ),
        sa.CheckConstraint(
            "ast_classification IS NULL OR ast_classification IN ('SELECT','INSERT','UPDATE','DELETE','DDL')",
            name="ck_queries_ast",
        ),
    )
    op.create_index("ix_queries_tenant_workspace", "flyquery_queries", ["tenant_id", "workspace_id"])

    op.create_table(
        "flyquery_query_results",
        sa.Column(
            "query_id",
            UUID(as_uuid=True),
            sa.ForeignKey("flyquery_queries.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("tenant_id", sa.Text, nullable=False),
        sa.Column("workspace_id", UUID(as_uuid=True), nullable=False),
        sa.Column("result_preview_json", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("result_object_key", sa.Text, nullable=True),
        sa.Column("result_byte_size", sa.BigInteger, nullable=True),
        sa.Column("ttl_expires_at", TIMESTAMP(timezone=True), nullable=True),
    )

    op.create_table(
        "flyquery_conversations",
        sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", sa.Text, nullable=False),
        sa.Column("workspace_id", UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.Text, nullable=True),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("actor", sa.Text, nullable=False),
        sa.Column("model", sa.Text, nullable=True),
        sa.Column("metadata_json", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "flyquery_conversation_turns",
        sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", sa.Text, nullable=False),
        sa.Column("workspace_id", UUID(as_uuid=True), nullable=False),
        sa.Column(
            "conversation_id",
            UUID(as_uuid=True),
            sa.ForeignKey("flyquery_conversations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("turn_index", sa.Integer, nullable=False),
        sa.Column("question", sa.Text, nullable=False),
        sa.Column("executed_sql", sa.Text, nullable=True),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("table_qnames_json", JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("snapshot_pins_json", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("citations_json", JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("no_answer", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("elapsed_ms", sa.Integer, nullable=True),
        sa.Column("model", sa.Text, nullable=True),
        sa.Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("conversation_id", "turn_index", name="uq_turns_conversation_index"),
    )


def downgrade() -> None:
    op.drop_table("flyquery_conversation_turns")
    op.drop_table("flyquery_conversations")
    op.drop_table("flyquery_query_results")
    op.drop_table("flyquery_queries")
