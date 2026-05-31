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

"""flyquery query + conversation entities."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, Boolean, CheckConstraint, Integer, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, NUMERIC, TIMESTAMP, UUID
from sqlalchemy.orm import Mapped, mapped_column

from flyquery.models.entities import Base


class Query(Base):
    __tablename__ = "flyquery_queries"
    __table_args__ = (
        CheckConstraint(
            "semantic_path_taken IS NULL OR semantic_path_taken IN ('SEMANTIC_LAYER','SYNTHESIS','HYBRID')",
            name="ck_queries_semantic_path",
        ),
        CheckConstraint(
            "execution_status IS NULL OR "
            "execution_status IN ('OK','REFINED_OK','FAILED','REJECTED_BY_FIREWALL')",
            name="ck_queries_status",
        ),
        CheckConstraint(
            "ast_classification IS NULL OR "
            "ast_classification IN ('SELECT','INSERT','UPDATE','DELETE','DDL','UNKNOWN')",
            name="ck_queries_ast",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    tenant_id: Mapped[str] = mapped_column(String, nullable=False)
    workspace_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    dataset_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    question: Mapped[str] = mapped_column(String, nullable=False)
    prior_turn_ids: Mapped[list[uuid.UUID]] = mapped_column(
        ARRAY(UUID(as_uuid=True)), nullable=False, server_default=text("'{}'")
    )
    table_id_snapshot_pins_json: Mapped[dict] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    semantic_path_taken: Mapped[str | None] = mapped_column(String, nullable=True)
    candidates_json: Mapped[list] = mapped_column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))
    chosen_candidate_index: Mapped[int | None] = mapped_column(Integer, nullable=True)
    executed_sql: Mapped[str | None] = mapped_column(String, nullable=True)
    ast_classification: Mapped[str | None] = mapped_column(String, nullable=True)
    execution_engine: Mapped[str] = mapped_column(String, nullable=False, server_default=text("'duckdb'"))
    execution_status: Mapped[str | None] = mapped_column(String, nullable=True)
    retries: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    row_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    elapsed_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cost_cents: Mapped[Decimal] = mapped_column(NUMERIC, nullable=False, server_default=text("0"))
    clarification_emitted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    clarification_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    pii_findings_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    error_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    model_grounding: Mapped[str | None] = mapped_column(String, nullable=True)
    model_generation: Mapped[str | None] = mapped_column(String, nullable=True)
    model_critic: Mapped[str | None] = mapped_column(String, nullable=True)
    model_explainer: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    finalised_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)


class QueryResult(Base):
    __tablename__ = "flyquery_query_results"

    query_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String, nullable=False)
    workspace_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    result_preview_json: Mapped[dict] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    result_object_key: Mapped[str | None] = mapped_column(String, nullable=True)
    result_byte_size: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    ttl_expires_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)


class Conversation(Base):
    __tablename__ = "flyquery_conversations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    tenant_id: Mapped[str] = mapped_column(String, nullable=False)
    workspace_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    title: Mapped[str | None] = mapped_column(String, nullable=True)
    summary: Mapped[str | None] = mapped_column(String, nullable=True)
    actor: Mapped[str] = mapped_column(String, nullable=False)
    model: Mapped[str | None] = mapped_column(String, nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )


class ConversationTurn(Base):
    __tablename__ = "flyquery_conversation_turns"
    __table_args__ = (UniqueConstraint("conversation_id", "turn_index", name="uq_turns_conversation_index"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    tenant_id: Mapped[str] = mapped_column(String, nullable=False)
    workspace_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    conversation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    turn_index: Mapped[int] = mapped_column(Integer, nullable=False)
    question: Mapped[str] = mapped_column(String, nullable=False)
    executed_sql: Mapped[str | None] = mapped_column(String, nullable=True)
    summary: Mapped[str | None] = mapped_column(String, nullable=True)
    table_qnames_json: Mapped[list] = mapped_column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))
    snapshot_pins_json: Mapped[dict] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    citations_json: Mapped[list] = mapped_column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))
    no_answer: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    elapsed_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    model: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
