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

"""SQL execute wire DTOs (Pydantic v2).

Defines the request/response shapes for the /sql:execute and
/sql:execute/stream endpoints.
"""

from __future__ import annotations

import uuid
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class SqlExecuteRequest(BaseModel):
    """Request body for POST /api/v1/sql:execute."""

    model_config = ConfigDict(populate_by_name=True)

    dataset_id: uuid.UUID
    sql: str = Field(min_length=1, max_length=65536)


class SqlExecuteResponse(BaseModel):
    """Response from POST /api/v1/sql:execute (sync)."""

    query_id: uuid.UUID
    sql: str
    ast_classification: str
    execution_status: Literal["OK", "FAILED", "REJECTED_BY_FIREWALL"]
    preview: list[dict[str, Any]] | None
    row_count: int | None
    truncated: bool = False
    elapsed_ms: int | None
