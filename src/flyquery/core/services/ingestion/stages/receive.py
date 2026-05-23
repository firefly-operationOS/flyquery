# Copyright 2026 Firefly Software Solutions Inc
"""Stage 1 — receive: hash + caps + format detect + write file row.

Responsibilities:
- Compute SHA-256 content hash of the uploaded bytes
- Enforce per-file and workspace quota caps
- Detect (format, compression) from filename + magic bytes
- Insert the flyquery_files row (status='RECEIVED')
- Return the created file ID and detected (format, compression)
"""

from __future__ import annotations

import hashlib
import logging
import os
import tempfile
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from flyquery.core.services.ingestion.caps import (
    enforce_upload_cap,
)
from flyquery.core.services.ingestion.format_detect import detect_format
from flyquery.core.services.storage.object_store import ObjectStore

logger = logging.getLogger(__name__)


@dataclass
class ReceiveResult:
    file_id: uuid.UUID
    file_format: str
    compression: str
    content_hash_sha256: str
    size_bytes: int
    object_store_key: str
    # Temp file on local FS holding the raw upload (available during this request)
    local_temp_path: str


async def run_receive(
    *,
    tenant_id: str,
    workspace_id: uuid.UUID,
    dataset_id: uuid.UUID,
    filename: str,
    file_bytes: bytes,
    actor: str,
    object_store: ObjectStore,
    session_factory: async_sessionmaker[AsyncSession],
    settings: Any,  # FlyquerySettings
    workspace_storage_used_bytes: int,
) -> ReceiveResult:
    """Execute Stage 1: receive."""
    size_bytes = len(file_bytes)

    # --- 1. Caps check ---
    enforce_upload_cap(size_bytes, workspace_storage_used_bytes, settings)

    # --- 2. Content hash ---
    content_hash = hashlib.sha256(file_bytes).hexdigest()

    # --- 3. Format detect ---
    head = file_bytes[:512]
    file_format, compression = detect_format(filename, head)

    # --- 4. Assign file_id + build storage key ---
    file_id = uuid.uuid4()
    ext = _pick_ext(filename, file_format, compression)
    object_store_key = f"flyquery/{tenant_id}/{workspace_id}/{dataset_id}/files/{file_id}{ext}"

    # --- 5. Store in object store ---
    content_type = _content_type(file_format)
    await object_store.put(object_store_key, file_bytes, content_type)

    # --- 6. Write local temp copy for pipeline stages (avoids re-downloading) ---
    fd, local_temp_path = tempfile.mkstemp(suffix=ext)
    try:
        os.write(fd, file_bytes)
    finally:
        os.close(fd)

    # --- 7. Insert flyquery_files row ---
    async with session_factory() as s, s.begin():
        await s.execute(
            sa.text(
                """
                INSERT INTO flyquery_files (
                    id, tenant_id, workspace_id, dataset_id,
                    original_filename, file_format, compression,
                    size_bytes, content_hash_sha256, object_store_key,
                    uploaded_by, status
                ) VALUES (
                    :id, :tenant_id, :workspace_id, :dataset_id,
                    :original_filename, :file_format, :compression,
                    :size_bytes, :content_hash_sha256, :object_store_key,
                    :uploaded_by, 'RECEIVED'
                )
                """
            ),
            {
                "id": file_id,
                "tenant_id": tenant_id,
                "workspace_id": workspace_id,
                "dataset_id": dataset_id,
                "original_filename": filename,
                "file_format": file_format,
                "compression": compression,
                "size_bytes": size_bytes,
                "content_hash_sha256": content_hash,
                "object_store_key": object_store_key,
                "uploaded_by": actor,
            },
        )

    logger.info(
        "stage=receive file_id=%s format=%s compression=%s size=%d",
        file_id,
        file_format,
        compression,
        size_bytes,
    )
    return ReceiveResult(
        file_id=file_id,
        file_format=file_format,
        compression=compression,
        content_hash_sha256=content_hash,
        size_bytes=size_bytes,
        object_store_key=object_store_key,
        local_temp_path=local_temp_path,
    )


def _pick_ext(filename: str, file_format: str, compression: str) -> str:
    """Preserve the original extension for object-store readability."""
    suffix = Path(filename).suffix or f".{file_format}"
    if compression != "none":
        suffix = f"{suffix}.{compression}"
    return suffix


_CONTENT_TYPES: dict[str, str] = {
    "csv": "text/csv",
    "tsv": "text/tab-separated-values",
    "json": "application/json",
    "jsonl": "application/x-ndjson",
    "parquet": "application/octet-stream",
    "avro": "application/octet-stream",
    "orc": "application/octet-stream",
    "arrow": "application/octet-stream",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "xls": "application/vnd.ms-excel",
    "ods": "application/vnd.oasis.opendocument.spreadsheet",
}


def _content_type(file_format: str) -> str:
    return _CONTENT_TYPES.get(file_format, "application/octet-stream")
