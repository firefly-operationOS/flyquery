# Copyright 2026 Firefly Software Solutions Inc
"""Wire DTOs for ingest job lifecycle endpoints."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Job kinds + statuses (mirrors DB CHECK constraints)
# ---------------------------------------------------------------------------

JobKind = Literal["PARSE_AND_INGEST", "REPARSE", "SAMPLE_REFRESH", "DESCRIBE_PASS", "RELATION_PASS"]
JobStatus = Literal["PENDING", "RUNNING", "SUCCEEDED", "FAILED", "CANCELLED"]

# Non-PARSE_AND_INGEST kinds that can be started via POST /ingest-jobs
# (PARSE_AND_INGEST is always started by /datasets/{id}/files)
_STARTABLE_KINDS: frozenset[str] = frozenset({"REPARSE", "SAMPLE_REFRESH", "DESCRIBE_PASS", "RELATION_PASS"})


class IngestJobCreate(BaseModel):
    """Request body for POST /api/v1/ingest-jobs."""

    dataset_id: uuid.UUID
    table_id: uuid.UUID | None = None
    file_id: uuid.UUID | None = None
    job_kind: JobKind
    request_json: dict | None = None

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
