# Copyright 2026 Firefly Software Solutions Inc
"""Dataset wire DTOs (Pydantic v2)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class DatasetCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    drift_policy: Literal["AUTO", "MANUAL"] = "AUTO"
    default_locale: str | None = None
    ingest_policy_json: dict = Field(default_factory=dict)
    metadata_json: dict = Field(default_factory=dict)


class DatasetUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    drift_policy: Literal["AUTO", "MANUAL"] | None = None
    default_locale: str | None = None
    ingest_policy_json: dict | None = None
    metadata_json: dict | None = None


class DatasetRead(BaseModel):
    id: uuid.UUID
    tenant_id: str
    workspace_id: uuid.UUID
    name: str
    description: str | None
    drift_policy: Literal["AUTO", "MANUAL"]
    default_locale: str | None
    ingest_policy_json: dict
    status: Literal["ACTIVE", "ARCHIVED"]
    created_at: datetime
    updated_at: datetime
    metadata_json: dict
