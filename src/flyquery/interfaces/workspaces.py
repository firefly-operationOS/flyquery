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
