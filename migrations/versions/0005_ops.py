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

"""ops tables: agent_tokens, audit, cost, ingest_jobs, ingest_events

Revision ID: 0005_ops
Revises: 0004_queries_conversations
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, NUMERIC, TIMESTAMP, UUID

revision = "0005_ops"
down_revision = "0004_queries_conversations"


def upgrade() -> None:
    op.create_table(
        "flyquery_agent_tokens",
        sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", sa.Text, nullable=False),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("prefix", sa.String(12), nullable=False, unique=True),
        sa.Column("secret_hash", sa.String(64), nullable=False),
        sa.Column("workspace_allowlist_json", JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("dataset_allowlist_json", JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("scopes_json", JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("rate_limit_rpm", sa.Integer, nullable=True),
        sa.Column("expires_at", TIMESTAMP(timezone=True), nullable=True),
        sa.Column("revoked_at", TIMESTAMP(timezone=True), nullable=True),
        sa.Column("last_used_at", TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_by", sa.Text, nullable=False),
    )
    op.create_index("ix_agent_tokens_tenant", "flyquery_agent_tokens", ["tenant_id"])

    op.create_table(
        "flyquery_audit_events",
        sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", sa.Text, nullable=False),
        sa.Column("workspace_id", UUID(as_uuid=True), nullable=False),
        sa.Column("actor", sa.Text, nullable=False),
        sa.Column("event_type", sa.Text, nullable=False),
        sa.Column("resource_kind", sa.Text, nullable=False),
        sa.Column("resource_id", sa.Text, nullable=True),
        sa.Column("correlation_id", sa.Text, nullable=True),
        sa.Column("payload_json", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_audit_tenant_workspace_at", "flyquery_audit_events", ["tenant_id", "workspace_id", "created_at"])

    op.create_table(
        "flyquery_cost_events",
        sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", sa.Text, nullable=False),
        sa.Column("workspace_id", UUID(as_uuid=True), nullable=False),
        sa.Column("actor", sa.Text, nullable=False),
        sa.Column("model", sa.Text, nullable=True),
        sa.Column("operation", sa.Text, nullable=False),
        sa.Column("input_tokens", sa.Integer, nullable=False, server_default=sa.text("0")),
        sa.Column("output_tokens", sa.Integer, nullable=False, server_default=sa.text("0")),
        sa.Column("cost_cents", NUMERIC, nullable=False, server_default=sa.text("0")),
        sa.Column("ingest_job_id", UUID(as_uuid=True), nullable=True),
        sa.Column("query_id", UUID(as_uuid=True), nullable=True),
        sa.Column("correlation_id", sa.Text, nullable=True),
        sa.Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_cost_tenant_workspace_at", "flyquery_cost_events", ["tenant_id", "workspace_id", "created_at"])

    op.create_table(
        "flyquery_ingest_jobs",
        sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tenant_id", sa.Text, nullable=False),
        sa.Column("workspace_id", UUID(as_uuid=True), nullable=False),
        sa.Column(
            "dataset_id",
            UUID(as_uuid=True),
            sa.ForeignKey("flyquery_datasets.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("table_id", UUID(as_uuid=True), nullable=True),
        sa.Column("file_id", UUID(as_uuid=True), nullable=True),
        sa.Column("snapshot_id", UUID(as_uuid=True), nullable=True),
        sa.Column("job_kind", sa.Text, nullable=False),
        sa.Column("request_json", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("result_json", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("status", sa.Text, nullable=False, server_default=sa.text("'PENDING'")),
        sa.Column("attempts", sa.Integer, nullable=False, server_default=sa.text("0")),
        sa.Column("started_at", TIMESTAMP(timezone=True), nullable=True),
        sa.Column("finished_at", TIMESTAMP(timezone=True), nullable=True),
        sa.Column("cost_cents", NUMERIC, nullable=False, server_default=sa.text("0")),
        sa.Column("elapsed_ms", sa.Integer, nullable=True),
        sa.CheckConstraint(
            "job_kind IN ('PARSE_AND_INGEST','REPARSE','SAMPLE_REFRESH','DESCRIBE_PASS','RELATION_PASS')",
            name="ck_jobs_kind",
        ),
        sa.CheckConstraint(
            "status IN ('PENDING','RUNNING','SUCCEEDED','FAILED','CANCELLED')", name="ck_jobs_status"
        ),
    )
    op.create_index("ix_jobs_tenant_workspace", "flyquery_ingest_jobs", ["tenant_id", "workspace_id"])

    op.create_table(
        "flyquery_ingest_events",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("tenant_id", sa.Text, nullable=False),
        sa.Column("workspace_id", UUID(as_uuid=True), nullable=False),
        sa.Column(
            "ingest_job_id",
            UUID(as_uuid=True),
            sa.ForeignKey("flyquery_ingest_jobs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("stage", sa.Text, nullable=False),
        sa.Column("status", sa.Text, nullable=False),
        sa.Column("message", sa.Text, nullable=True),
        sa.Column("payload_json", JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_events_job", "flyquery_ingest_events", ["ingest_job_id"])


def downgrade() -> None:
    op.drop_table("flyquery_ingest_events")
    op.drop_table("flyquery_ingest_jobs")
    op.drop_table("flyquery_cost_events")
    op.drop_table("flyquery_audit_events")
    op.drop_table("flyquery_agent_tokens")
