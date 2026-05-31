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

"""Examples wire DTOs (Pydantic v2)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ExampleCreate(BaseModel):
    """Payload for creating a new example (question + SQL pair)."""

    model_config = ConfigDict(populate_by_name=True)

    question: str = Field(min_length=1, max_length=4096)
    generated_sql: str = Field(min_length=1)
    dataset_id: uuid.UUID | None = None
    citations_json: dict = Field(default_factory=dict)


class ExampleUpdate(BaseModel):
    """Sparse-update payload for an existing example."""

    question: str | None = None
    generated_sql: str | None = None


class ExampleRead(BaseModel):
    """Full read representation of a flyquery_examples row."""

    id: uuid.UUID
    tenant_id: str
    workspace_id: uuid.UUID
    dataset_id: uuid.UUID | None
    question: str
    generated_sql: str
    normalised_sql: str
    source: Literal["USER_CURATED", "AGENT_LEARNED"]
    quality: Literal["PROPOSED", "APPROVED", "REJECTED"]
    citations_json: dict
    created_at: datetime
    created_by: str
    last_used_at: datetime | None
    usage_count: int
