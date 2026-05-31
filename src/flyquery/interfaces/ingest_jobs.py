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

"""Wire DTOs for ingest job lifecycle endpoints."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl, field_validator

# ---------------------------------------------------------------------------
# Job kinds + statuses (mirrors DB CHECK constraints)
# ---------------------------------------------------------------------------

JobKind = Literal["PARSE_AND_INGEST", "REPARSE", "SAMPLE_REFRESH", "DESCRIBE_PASS", "RELATION_PASS"]
JobStatus = Literal["PENDING", "RUNNING", "SUCCEEDED", "FAILED", "CANCELLED"]

# Non-PARSE_AND_INGEST kinds that can be started via POST /ingest-jobs
# (PARSE_AND_INGEST is always started by /datasets/{id}/files)
_STARTABLE_KINDS: frozenset[str] = frozenset({"REPARSE", "SAMPLE_REFRESH", "DESCRIBE_PASS", "RELATION_PASS"})


class CallbackConfig(BaseModel):
    """Webhook delivery target attached to an async ingest job.

    Set on job creation (``IngestJobCreate.callback`` or the
    ``callback_*`` query params on ``POST /datasets/{id}/files:async``).
    On every terminal status transition the worker writes one row to
    ``flyquery_callback_outbox``; the ``CallbackWorker`` POSTs the
    canonical :class:`IngestJobRead` to ``url`` with header
    ``X-Flyquery-Signature: sha256=<hmac>`` if ``secret`` is provided.

    Delivery is at-least-once with exponential backoff (5 attempts:
    0s, 30s, 5m, 1h, 6h). After the last failed attempt the row is
    marked ``DEAD`` and surfaced via ``GET /ingest-jobs/{id}/callbacks``.
    """

    url: HttpUrl
    secret: str | None = Field(
        default=None,
        description="Shared secret for HMAC-SHA256 over the request body.",
        min_length=8,
        max_length=512,
    )
    headers: dict[str, str] = Field(
        default_factory=dict,
        description="Extra HTTP headers merged onto every callback request.",
    )

    @field_validator("headers")
    @classmethod
    def _no_reserved_headers(cls, v: dict[str, str]) -> dict[str, str]:
        reserved = {
            "x-flyquery-signature",
            "x-flyquery-job-id",
            "x-flyquery-event",
            "content-type",
        }
        offending = {k for k in v if k.lower() in reserved}
        if offending:
            raise ValueError(f"reserved callback headers cannot be overridden: {sorted(offending)}")
        return v


class IngestJobCreate(BaseModel):
    """Request body for POST /api/v1/ingest-jobs."""

    dataset_id: uuid.UUID
    table_id: uuid.UUID | None = None
    file_id: uuid.UUID | None = None
    job_kind: JobKind
    request_json: dict | None = None
    callback: CallbackConfig | None = Field(
        default=None,
        description=(
            "Optional webhook delivered after the job reaches a terminal "
            "status (SUCCEEDED, FAILED, or CANCELLED). See "
            ":class:`CallbackConfig` for the at-least-once delivery contract."
        ),
    )

    def validate_startable(self) -> None:
        """Raise ValueError if job_kind is PARSE_AND_INGEST (not startable via this endpoint)."""
        if self.job_kind == "PARSE_AND_INGEST":
            raise ValueError(
                "PARSE_AND_INGEST jobs are started automatically by POST /datasets/{id}/files. "
                "Use REPARSE, SAMPLE_REFRESH, DESCRIBE_PASS, or RELATION_PASS here."
            )


class IngestJobRead(BaseModel):
    """Response for GET /api/v1/ingest-jobs/{id} and list items."""

    id: uuid.UUID
    tenant_id: str
    workspace_id: uuid.UUID
    dataset_id: uuid.UUID
    table_id: uuid.UUID | None
    file_id: uuid.UUID | None
    snapshot_id: uuid.UUID | None
    job_kind: str
    status: str
    attempts: int
    request_json: dict
    result_json: dict
    cost_cents: Decimal
    elapsed_ms: int | None
    started_at: datetime | None
    finished_at: datetime | None


class IngestJobListResponse(BaseModel):
    """Paginated list of ingest jobs."""

    items: list[IngestJobRead]
    total: int
    limit: int
    offset: int


class IngestEventRead(BaseModel):
    """One row from flyquery_ingest_events."""

    id: int
    ingest_job_id: uuid.UUID
    stage: str
    status: str
    message: str | None
    payload_json: dict
    created_at: datetime


class IngestEventListResponse(BaseModel):
    """Paginated event ledger for GET /ingest-jobs/{id}/events."""

    items: list[IngestEventRead]
    total: int
    limit: int
    offset: int


class CancelResponse(BaseModel):
    """Response for POST /ingest-jobs/{id}:cancel."""

    id: uuid.UUID
    status: str
    message: str


class CallbackDeliveryRead(BaseModel):
    """One row from flyquery_callback_outbox.

    Returned by ``GET /api/v1/ingest-jobs/{id}/callbacks`` so the
    caller can audit webhook delivery without inspecting the DB.
    """

    id: uuid.UUID
    ingest_job_id: uuid.UUID
    callback_url: str
    event_type: str
    status: Literal["PENDING", "DELIVERED", "FAILED", "DEAD"]
    attempts: int
    last_attempt_at: datetime | None
    last_status_code: int | None
    last_error: str | None
    next_attempt_at: datetime
    created_at: datetime
    finished_at: datetime | None


class CallbackDeliveryListResponse(BaseModel):
    """Paginated callback-delivery audit log."""

    items: list[CallbackDeliveryRead]
    total: int
    limit: int
    offset: int
