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

"""Query pipeline wire DTOs (Pydantic v2).

Defines the request/response shapes for the /query, /query:explain,
/query:validate, and /query/stream endpoints.
"""

from __future__ import annotations

import uuid
from datetime import datetime
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


# ---------------------------------------------------------------------------
# v1 history endpoints — GET /api/v1/queries, /queries/{id}, /queries/{id}/result
# ---------------------------------------------------------------------------


class QueryHistoryItem(BaseModel):
    """Compact row for `GET /api/v1/queries` (history list).

    Heavy JSONB columns (candidates, clarification, pii_findings) are
    omitted here so a 50-item page stays under a few KB; the detail
    endpoint exposes them via :class:`QueryDetailRead`.
    """

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: str
    workspace_id: uuid.UUID
    dataset_id: uuid.UUID | None = None
    question: str
    executed_sql: str | None = None
    ast_classification: str | None = None
    execution_status: str | None = None
    row_count: int | None = None
    elapsed_ms: int | None = None
    semantic_path_taken: str | None = None
    retries: int = 0
    clarification_emitted: bool = False
    created_at: datetime
    finalised_at: datetime | None = None


class QueryDetailRead(BaseModel):
    """Full single-query payload for `GET /api/v1/queries/{id}`.

    Includes every candidate proposal, the AST classification, every
    model identifier used (grounding / generation / critic / explainer),
    PII findings, clarification frame, and the final error envelope if
    any. JSONB columns are passed through as Python dicts / lists.
    """

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: str
    workspace_id: uuid.UUID
    dataset_id: uuid.UUID | None = None
    question: str
    prior_turn_ids: list[uuid.UUID] = Field(default_factory=list)
    table_id_snapshot_pins_json: dict[str, Any] | None = None
    semantic_path_taken: str | None = None
    candidates_json: list[Any] = Field(default_factory=list)
    chosen_candidate_index: int | None = None
    executed_sql: str | None = None
    ast_classification: str | None = None
    execution_engine: str = "duckdb"
    execution_status: str | None = None
    retries: int = 0
    row_count: int | None = None
    elapsed_ms: int | None = None
    cost_cents: float | int | None = None
    clarification_emitted: bool = False
    clarification_json: dict[str, Any] | None = None
    pii_findings_json: dict[str, Any] | None = None
    error_json: dict[str, Any] | None = None
    model_grounding: str | None = None
    model_generation: str | None = None
    model_critic: str | None = None
    model_explainer: str | None = None
    created_at: datetime
    finalised_at: datetime | None = None


class QueryResultRead(BaseModel):
    """Re-download envelope for `GET /api/v1/queries/{id}/result`.

    The preview is always inlined. ``parquet_presigned_url`` is set
    when the full Parquet is still available on the object store
    (i.e. ``ttl_expires_at`` hasn't elapsed). When the TTL is past
    the URL is ``None`` and the consumer must rerun the query.
    """

    query_id: uuid.UUID
    preview_json: Any
    parquet_presigned_url: str | None = None
    result_byte_size: int | None = None
    ttl_expires_at: datetime | None = None
