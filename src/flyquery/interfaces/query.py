# Copyright 2026 Firefly Software Solutions Inc
"""Query pipeline wire DTOs (Pydantic v2).

Defines the request/response shapes for the /query, /query:explain,
/query:validate, and /query/stream endpoints.
"""

from __future__ import annotations

import uuid
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class QueryRequest(BaseModel):
    """Request body for POST /api/v1/query and /query:explain, /query:validate."""

    model_config = ConfigDict(populate_by_name=True)

    dataset_id: uuid.UUID
    question: str = Field(min_length=1, max_length=4096)
    conversation_id: uuid.UUID | None = None


class ClarificationFrame(BaseModel):
    """Emitted when grounding confidence is below the threshold and missing_info is set."""

    questions: list[str]
    reasons: list[str] = Field(default_factory=list)


class AnswerResponse(BaseModel):
    """Response from POST /api/v1/query (sync)."""

    query_id: uuid.UUID
    sql: str | None
    execution_status: Literal["OK", "REFINED_OK", "FAILED", "REJECTED_BY_FIREWALL"] | None
    preview: list[dict[str, Any]] | None
    row_count: int | None
    truncated: bool = False
    elapsed_ms: int | None
    chart_hint: Literal["line", "bar", "table", "pie", "none"] | None = None
    explanation: str | None = None
    clarification: ClarificationFrame | None = None
    grounded_summary: dict | None = None
    snapshot_pins: dict[str, str] = Field(default_factory=dict)


class ExplainResponse(BaseModel):
    """Response from POST /api/v1/query:explain — Grounding + Generation only."""

    sql: str | None
    reasoning: str | None
    confidence: float | None
    grounded_summary: dict | None = None
    clarification: ClarificationFrame | None = None


class ValidateResponse(BaseModel):
    """Response from POST /api/v1/query:validate — includes AST + scope check."""

    sql: str | None
    ast_classification: str | None
    table_refs: list[str] = Field(default_factory=list)
    single_statement: bool = True
    scope_error: str | None = None
    clarification: ClarificationFrame | None = None
