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

"""Glossary wire DTOs (Pydantic v2)."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class GlossaryTermCreate(BaseModel):
    """Payload for creating a new glossary term."""

    model_config = ConfigDict(populate_by_name=True)

    term: str = Field(min_length=1, max_length=512)
    definition: str = Field(min_length=1)
    synonyms_json: list[str] = Field(default_factory=list, alias="synonyms")
    tags_json: list[str] = Field(default_factory=list, alias="tags")
    related_columns_json: list[str] = Field(default_factory=list, alias="related_columns")
    related_metrics_json: list[str] = Field(default_factory=list, alias="related_metrics")


class GlossaryTermUpdate(BaseModel):
    """Sparse-update payload for an existing glossary term."""

    model_config = ConfigDict(populate_by_name=True)

    definition: str | None = None
    synonyms_json: list[str] | None = Field(default=None, alias="synonyms")
    tags_json: list[str] | None = Field(default=None, alias="tags")
    related_columns_json: list[str] | None = Field(default=None, alias="related_columns")
    related_metrics_json: list[str] | None = Field(default=None, alias="related_metrics")


class GlossaryTermRead(BaseModel):
    """Full read representation of a flyquery_glossary_terms row."""

    id: uuid.UUID
    tenant_id: str
    workspace_id: uuid.UUID
    term: str
    definition: str
    synonyms_json: list[str]
    tags_json: list[str]
    related_columns_json: list[str]
    related_metrics_json: list[str]
    created_at: datetime
    updated_at: datetime
