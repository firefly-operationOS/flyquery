# Copyright 2026 Firefly Software Solutions Inc
"""Workspace wire DTOs (Pydantic v2)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class WorkspaceCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    slug: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=200)
    kms_key_uri: str | None = None
    retention_days: int | None = Field(default=None, ge=1)
    allow_direct_sql: bool = False
    default_locale: str = "en-US"
    metadata_json: dict = Field(default_factory=dict)


class WorkspaceUpdate(BaseModel):
    name: str | None = None
    kms_key_uri: str | None = None
    retention_days: int | None = Field(default=None, ge=1)
    allow_direct_sql: bool | None = None
    default_locale: str | None = None
    metadata_json: dict | None = None


class WorkspaceRead(BaseModel):
    id: uuid.UUID
    tenant_id: str
    slug: str
    name: str
    kms_key_uri: str | None
    retention_days: int | None
    allow_direct_sql: bool
    default_locale: str
    storage_used_bytes: int
    status: Literal["ACTIVE", "ARCHIVED", "PURGING"]
    created_at: datetime
    updated_at: datetime
    metadata_json: dict
