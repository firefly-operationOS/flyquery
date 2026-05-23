# Copyright 2026 Firefly Software Solutions Inc
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
