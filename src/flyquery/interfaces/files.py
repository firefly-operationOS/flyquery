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

"""Wire DTOs for file upload + table responses."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, field_validator

from flyquery.core.services.storage.jsonb_normalize import (
    normalize_governance_json,
    normalize_synonyms_json,
)


class SchemaObjectUpdate(BaseModel):
    """Request body for PUT /schema-objects/{id}.

    ``synonyms_json`` is canonically ``list[str]``; ``governance_json``
    is canonically ``dict[str, Any]``. The validators coerce legacy
    shapes (a synonyms dict envelope, a governance array left behind
    by the ``NULL || dict`` jsonb-concat bug) so a malformed write
    payload still lands as the canonical shape.
    """

    description: str | None = None
    pii_tag: str | None = None
    business_owner: str | None = None
    governance_json: dict[str, Any] | None = None
    synonyms_json: list[str] | None = None

    @field_validator("synonyms_json", mode="before")
    @classmethod
    def _coerce_synonyms(cls, v: Any) -> list[str] | None:
        return None if v is None else normalize_synonyms_json(v)

    @field_validator("governance_json", mode="before")
    @classmethod
    def _coerce_governance(cls, v: Any) -> dict[str, Any] | None:
        return None if v is None else normalize_governance_json(v)


class SchemaObjectRead(BaseModel):
    """Response for GET /schema-objects/{id} or PUT /schema-objects/{id}.

    See :class:`SchemaObjectUpdate` for shape contract. Reads always
    return canonical shapes; the validators forgive a legacy row that
    has not yet been touched by migration 0012.
    """

    id: uuid.UUID
    tenant_id: str
    workspace_id: uuid.UUID
    table_id: uuid.UUID
    snapshot_id: uuid.UUID
    kind: str
    qualified_name: str
    data_type: str | None
    is_nullable: bool | None
    description: str | None
    description_source: str | None
    synonyms_json: list[str] = []
    pii_tag: str | None
    pii_source: str | None
    business_owner: str | None
    governance_json: dict[str, Any] = {}
    is_active: bool
    created_at: datetime
    last_changed_at: datetime

    @field_validator("synonyms_json", mode="before")
    @classmethod
    def _coerce_synonyms(cls, v: Any) -> list[str]:
        return normalize_synonyms_json(v)

    @field_validator("governance_json", mode="before")
    @classmethod
    def _coerce_governance(cls, v: Any) -> dict[str, Any]:
        return normalize_governance_json(v)


class TableSummary(BaseModel):
    """Summary of a table created/updated by an upload."""

    table_id: str
    name: str
    n_columns: int
    n_rows_estimate: int


class FileUploadResponse(BaseModel):
    """Response from POST /datasets/{id}/files."""

    file_id: str
    tables: list[TableSummary]


class AsyncFileUploadAccepted(BaseModel):
    """202 Accepted envelope from POST /datasets/{id}/files:async.

    The file *bytes* were stored synchronously (Stage 1: receive), so
    ``file_id`` is final and persists. Stages 2-10 of the pipeline
    (parse / reconcile / sample / profile / describe / embed / publish)
    run in the background under ``job_id`` -- poll
    ``GET /ingest-jobs/{job_id}`` or stream
    ``GET /ingest-jobs/{job_id}/stream`` for progress.

    Use this endpoint instead of the synchronous ``POST /files`` when
    the file is large enough (multi-MB) to risk timing out the HTTP
    request thread.
    """

    job_id: uuid.UUID
    file_id: uuid.UUID
    dataset_id: uuid.UUID
    status: str = "PENDING"


class BulkFileResult(BaseModel):
    """Per-file outcome from POST /datasets/{id}/files:bulk."""

    index: int
    original_filename: str
    status: str  # "OK" | "FAILED"
    file_id: str | None = None
    tables: list[TableSummary] = []
    error: str | None = None


class BulkFileUploadResponse(BaseModel):
    """Response from POST /datasets/{id}/files:bulk.

    Returns one ``results`` entry per uploaded file. Per-file failures
    do NOT abort the bulk -- the caller sees which files succeeded and
    which didn't, with the error message inline. Aggregate counts let
    a UI render "4/5 uploaded successfully" without scanning the list.
    """

    results: list[BulkFileResult]
    total_files: int
    succeeded: int
    failed: int


class ReuploadResponse(BaseModel):
    """Response from PUT /datasets/{ds}/tables/{id}:upload."""

    file_id: str
    snapshot_id: str
    n_columns: int
    n_rows_actual: int


class TableRead(BaseModel):
    """Response for GET /tables/{id}."""

    id: uuid.UUID
    tenant_id: str
    workspace_id: uuid.UUID
    dataset_id: uuid.UUID
    source_file_id: uuid.UUID | None
    name: str
    qualified_name: str
    kind: str
    sheet_or_json_path: str | None
    current_snapshot_id: uuid.UUID | None
    description: str | None
    description_source: str | None
    business_owner: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    # Computed from current snapshot
    n_columns: int | None = None


class SnapshotRead(BaseModel):
    """Response for GET /tables/{id}/snapshots items."""

    id: uuid.UUID
    table_id: uuid.UUID
    taken_at: datetime
    n_columns: int
    n_rows_actual: int | None
    n_rows_estimate: int | None
    parquet_byte_size: int | None
    status: str
    triggered_by: str


class SchemaChangeRead(BaseModel):
    """Response for GET /tables/{id}/changes items."""

    id: uuid.UUID
    table_id: uuid.UUID
    prev_snapshot_id: uuid.UUID | None
    next_snapshot_id: uuid.UUID
    column_name: str
    change: str
    before_json: dict | None
    after_json: dict | None
    llm_rationale: str | None
    approved_by: str | None = None
    approved_at: datetime | None = None
    created_at: datetime
