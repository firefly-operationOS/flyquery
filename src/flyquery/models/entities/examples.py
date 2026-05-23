# Copyright 2026 Firefly Software Solutions Inc
"""flyquery examples entity."""

from __future__ import annotations

import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import BigInteger, CheckConstraint, String, text
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP, UUID
from sqlalchemy.orm import Mapped, mapped_column

from flyquery.models.entities import Base


class Example(Base):
    __tablename__ = "flyquery_examples"
    __table_args__ = (
        CheckConstraint("source IN ('USER_CURATED','AGENT_LEARNED')", name="ck_examples_source"),
        CheckConstraint("quality IN ('PROPOSED','APPROVED','REJECTED')", name="ck_examples_quality"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    tenant_id: Mapped[str] = mapped_column(String, nullable=False)
    workspace_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    dataset_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    question: Mapped[str] = mapped_column(String, nullable=False)
    generated_sql: Mapped[str] = mapped_column(String, nullable=False)
    normalised_sql: Mapped[str] = mapped_column(String, nullable=False)
    source: Mapped[str] = mapped_column(String, nullable=False)
    quality: Mapped[str] = mapped_column(String, nullable=False, server_default=text("'PROPOSED'"))
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1536), nullable=True)
    citations_json: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    created_by: Mapped[str] = mapped_column(String, nullable=False)
    last_used_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    usage_count: Mapped[int] = mapped_column(BigInteger, nullable=False, server_default=text("0"))
