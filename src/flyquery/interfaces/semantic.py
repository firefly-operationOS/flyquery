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

"""Semantic-layer wire DTOs (Pydantic v2)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class SemanticMetricCreate(BaseModel):
    """Payload for creating a new semantic metric."""

    model_config = ConfigDict(populate_by_name=True)

    dataset_id: uuid.UUID
    name: str = Field(min_length=1, max_length=256)
    label: str | None = None
    description: str | None = None
    definition_yaml: str = Field(min_length=1)
    metric_type: Literal["SIMPLE", "RATIO", "DERIVED", "CUMULATIVE"] = "SIMPLE"


class SemanticMetricUpdate(BaseModel):
    """Sparse-update payload for an existing semantic metric."""

    label: str | None = None
    description: str | None = None
    definition_yaml: str | None = None
    metric_type: Literal["SIMPLE", "RATIO", "DERIVED", "CUMULATIVE"] | None = None


class SemanticMetricRead(BaseModel):
    """Full read representation of a flyquery_semantic_metrics row."""

    id: uuid.UUID
    tenant_id: str
    workspace_id: uuid.UUID
    dataset_id: uuid.UUID
    name: str
    label: str | None
    description: str | None
    definition_yaml: str
    compiled_sql_template: str | None
    metric_type: Literal["SIMPLE", "RATIO", "DERIVED", "CUMULATIVE"]
    status: Literal["DRAFT", "PUBLISHED", "RETIRED"]
    current_version: int
    created_at: datetime
    updated_at: datetime


class SemanticVersionRead(BaseModel):
    """Read representation of a flyquery_semantic_versions row."""

    id: uuid.UUID
    tenant_id: str
    workspace_id: uuid.UUID
    kind: str
    parent_id: uuid.UUID
    version: int
    definition_yaml: str
    compiled_sql_template: str | None
    created_by: str
    created_at: datetime


# ---------------------------------------------------------------------------
# Dimensions DTOs  (flyquery_semantic_dimensions — same schema as metrics)
# ---------------------------------------------------------------------------


class SemanticDimensionCreate(BaseModel):
    """Payload for creating a new semantic dimension."""

    model_config = ConfigDict(populate_by_name=True)

    dataset_id: uuid.UUID
    name: str = Field(min_length=1, max_length=256)
    label: str | None = None
    description: str | None = None
    definition_yaml: str = Field(min_length=1)
    metric_type: Literal["SIMPLE", "RATIO", "DERIVED", "CUMULATIVE"] = "SIMPLE"


class SemanticDimensionUpdate(BaseModel):
    """Sparse-update payload for an existing semantic dimension."""

    label: str | None = None
    description: str | None = None
    definition_yaml: str | None = None
    metric_type: Literal["SIMPLE", "RATIO", "DERIVED", "CUMULATIVE"] | None = None


class SemanticDimensionRead(BaseModel):
    """Full read representation of a flyquery_semantic_dimensions row."""

    id: uuid.UUID
    tenant_id: str
    workspace_id: uuid.UUID
    dataset_id: uuid.UUID
    name: str
    label: str | None
    description: str | None
    definition_yaml: str
    compiled_sql_template: str | None
    metric_type: Literal["SIMPLE", "RATIO", "DERIVED", "CUMULATIVE"]
    status: Literal["DRAFT", "PUBLISHED", "RETIRED"]
    current_version: int
    created_at: datetime
    updated_at: datetime
