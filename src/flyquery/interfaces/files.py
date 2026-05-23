# Copyright 2026 Firefly Software Solutions Inc
"""Wire DTOs for file upload + table responses."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


class SchemaObjectUpdate(BaseModel):
    """Request body for PUT /schema-objects/{id}."""

    description: str | None = None
    pii_tag: str | None = None
    business_owner: str | None = None
    governance_json: dict | None = None
    synonyms_json: list | None = None


class SchemaObjectRead(BaseModel):
    """Response for GET /schema-objects/{id} or PUT /schema-objects/{id}."""

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
    synonyms_json: list | None
    pii_tag: str | None
    pii_source: str | None
    business_owner: str | None
    governance_json: dict | None
    is_active: bool
    created_at: datetime
    last_changed_at: datetime


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
