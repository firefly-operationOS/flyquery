# Copyright 2026 Firefly Software Solutions Inc
"""flyquery schema KB entities: schema_snapshots, schema_changes, schema_objects, relations."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, CheckConstraint, Float, Integer, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP, UUID
from sqlalchemy.orm import Mapped, mapped_column

from flyquery.models.entities import Base


class SchemaSnapshot(Base):
    __tablename__ = "flyquery_schema_snapshots"
    __table_args__ = (
        CheckConstraint("status IN ('PARTIAL','READY','FAILED')", name="ck_snapshots_status"),
        CheckConstraint(
            "triggered_by IN ('USER','AGENT','SCHEDULED','REPARSE')", name="ck_snapshots_trigger"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    tenant_id: Mapped[str] = mapped_column(String, nullable=False)
    workspace_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    dataset_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    table_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    taken_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    snapshot_hash: Mapped[str] = mapped_column(String, nullable=False)
    n_columns: Mapped[int] = mapped_column(Integer, nullable=False)
    n_rows_estimate: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    n_rows_actual: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    parquet_object_key: Mapped[str | None] = mapped_column(String, nullable=True)
    parquet_byte_size: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False, server_default=text("'PARTIAL'"))
    failure_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    triggered_by: Mapped[str] = mapped_column(String, nullable=False)
    created_by: Mapped[str] = mapped_column(String, nullable=False)


class SchemaChange(Base):
    __tablename__ = "flyquery_schema_changes"
    __table_args__ = (
        CheckConstraint(
            "change IN ('ADDED','REMOVED','TYPE_CHANGED','RENAMED','RENAMED_CANDIDATE')",
            name="ck_changes_kind",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    tenant_id: Mapped[str] = mapped_column(String, nullable=False)
    workspace_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    table_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    prev_snapshot_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    next_snapshot_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    column_name: Mapped[str] = mapped_column(String, nullable=False)
    change: Mapped[str] = mapped_column(String, nullable=False)
    before_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    after_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    llm_rationale: Mapped[str | None] = mapped_column(String, nullable=True)
    approved_by: Mapped[str | None] = mapped_column(String, nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )


class SchemaObject(Base):
    __tablename__ = "flyquery_schema_objects"
    __table_args__ = (
        CheckConstraint("kind IN ('TABLE','COLUMN')", name="ck_objects_kind"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    tenant_id: Mapped[str] = mapped_column(String, nullable=False)
    workspace_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    table_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    snapshot_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    kind: Mapped[str] = mapped_column(String, nullable=False)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    qualified_name: Mapped[str] = mapped_column(String, nullable=False)
    data_type: Mapped[str | None] = mapped_column(String, nullable=True)
    is_nullable: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    description_source: Mapped[str | None] = mapped_column(String, nullable=True)
    synonyms_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    pii_tag: Mapped[str | None] = mapped_column(String, nullable=True)
    pii_source: Mapped[str | None] = mapped_column(String, nullable=True)
    business_owner: Mapped[str | None] = mapped_column(String, nullable=True)
    governance_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    sample_values_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    sample_taken_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    profile_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # embedding and content_tsv columns are added in migration 0006 (pgvector extension)
    embedding_model: Mapped[str | None] = mapped_column(String, nullable=True)
    source_hash: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    last_changed_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )


class Relation(Base):
    __tablename__ = "flyquery_relations"
    __table_args__ = (
        CheckConstraint("kind IN ('HEURISTIC','AGENT_PROPOSED','MANUAL')", name="ck_relations_kind"),
        CheckConstraint("status IN ('PROPOSED','APPROVED','REJECTED')", name="ck_relations_status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    tenant_id: Mapped[str] = mapped_column(String, nullable=False)
    workspace_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    dataset_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    from_table_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    from_column_name: Mapped[str] = mapped_column(String, nullable=False)
    to_table_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    to_column_name: Mapped[str] = mapped_column(String, nullable=False)
    condition: Mapped[str | None] = mapped_column(String, nullable=True)
    kind: Mapped[str] = mapped_column(String, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, server_default=text("0.0"))
    reason: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False, server_default=text("'PROPOSED'"))
    approved_by: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
