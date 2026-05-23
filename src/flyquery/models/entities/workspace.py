# Copyright 2026 Firefly Software Solutions Inc
"""flyquery_workspaces entity."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Integer, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP, UUID
from sqlalchemy.orm import Mapped, mapped_column

from flyquery.models.entities import Base


class Workspace(Base):
    __tablename__ = "flyquery_workspaces"
    __table_args__ = (UniqueConstraint("tenant_id", "slug", name="uq_workspaces_tenant_slug"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    tenant_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    kms_key_uri: Mapped[str | None] = mapped_column(String, nullable=True)
    retention_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    allow_direct_sql: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    default_locale: Mapped[str] = mapped_column(String, nullable=False, server_default=text("'en-US'"))
    storage_used_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False, server_default=text("0"))
    status: Mapped[str] = mapped_column(String, nullable=False, server_default=text("'ACTIVE'"))
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
