# Copyright 2026 Firefly Software Solutions Inc
"""flyquery_files entity."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import BigInteger, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP, UUID
from sqlalchemy.orm import Mapped, mapped_column

from flyquery.models.entities import Base


class File(Base):
    __tablename__ = "flyquery_files"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    workspace_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    dataset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("flyquery_datasets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    original_filename: Mapped[str] = mapped_column(String, nullable=False)
    file_format: Mapped[str] = mapped_column(String, nullable=False)
    compression: Mapped[str] = mapped_column(String, nullable=False, server_default=text("'none'"))
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    content_hash_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    object_store_key: Mapped[str] = mapped_column(String, nullable=False)
    table_extraction_rules_json: Mapped[dict] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    uploaded_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    uploaded_by: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, server_default=text("'RECEIVED'"))
    error_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
