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


class AgentUsage(BaseModel):
    """LLM usage + cost for a single pipeline stage.

    Surfaced inside :class:`UsageSummary` so callers see exactly
    where the tokens went. ``cost_usd`` is computed by the
    fireflyframework-agentic cost tracker (per-model rate table).
    """

    agent: str  # "grounding" | "generation" | "critic" | "explainer" | ...
    model: str | None = None
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0
    latency_ms: float = 0.0
    calls: int = 0


class UsageSummary(BaseModel):
    """Aggregated cost + latency across the whole pipeline.

    Returned on every query / ingest response so clients can
    show consumption to end users and stream into a billing
    pipeline. The per-stage breakdown stays in ``by_agent`` for
    debugging.
    """

    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    total_latency_ms: float = 0.0
    by_agent: list[AgentUsage] = Field(default_factory=list)


class BatchQueryItem(BaseModel):
    """One question in a batch -- matches ``AnswerRequest`` minus headers."""

    question: str
    dataset_id: uuid.UUID
    conversation_id: uuid.UUID | None = None


class BatchQueryRequest(BaseModel):
    """Request body for ``POST /api/v1/query:batch``."""

    queries: list[BatchQueryItem]


class BatchQueryResultItem(BaseModel):
    """One outcome in a batch query response.

    Mirrors ``AnswerResponse`` for OK results; carries ``error`` +
    ``status="FAILED"`` on failure so the batch never aborts on one
    bad item.
    """

    index: int
    status: str  # "OK" | "FAILED"
    query_id: uuid.UUID | None = None
    sql: str | None = None
    execution_status: Literal["OK", "REFINED_OK", "FAILED", "REJECTED_BY_FIREWALL"] | None = None
    preview: list[dict[str, Any]] | None = None
    row_count: int | None = None
    elapsed_ms: int | None = None
    chart_hint: Literal["line", "bar", "table", "pie", "none"] | None = None
    explanation: str | None = None
    grounded_summary: dict | None = None
    error: str | None = None


class BatchQueryResponse(BaseModel):
    """Response from ``POST /api/v1/query:batch``."""

    results: list[BatchQueryResultItem]
    total_queries: int
    succeeded: int
    failed: int


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
    usage: UsageSummary | None = None


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
