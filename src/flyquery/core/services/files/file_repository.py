# Copyright 2026 Firefly Software Solutions Inc
"""Async SQLAlchemy repository for flyquery_files.

Owns the two operations the rest of the ingestion path needs:

* :meth:`insert_received` -- called by Stage 1 (receive) of the
  ingestion pipeline once bytes are in object storage.
* :meth:`get`             -- called by the worker's PARSE_AND_INGEST /
  REPARSE handler to look up the canonical key + filename for a
  previously-received file.

The DB schema enforces ``UNIQUE(tenant_id, dataset_id,
content_hash_sha256)`` so a content-identical re-upload is detected
at the SQL layer; we let the duplicate-key error bubble up so the
caller can map it to a 409 if it wants (today the controller treats
it as a fresh insert and lets the constraint raise to the conventions
exception handler).
"""

from __future__ import annotations

import uuid
from typing import Any

import sqlalchemy as sa
from pyfly.container import repository
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


@repository
class FileRepository:
    """Repository over ``flyquery_files``."""

    def __init__(self, session: async_sessionmaker[AsyncSession]) -> None:
        self._factory = session

    async def insert_received(
        self,
        *,
        file_id: uuid.UUID,
        tenant_id: str,
        workspace_id: uuid.UUID,
        dataset_id: uuid.UUID,
        original_filename: str,
        file_format: str,
        compression: str,
        size_bytes: int,
        content_hash_sha256: str,
        object_store_key: str,
        uploaded_by: str,
    ) -> None:
        """Insert a new ``RECEIVED`` row.

        Status is hard-coded to ``RECEIVED`` because this method is the
        only writer that runs at Stage 1 -- later stages mutate the
        snapshot, not the file row.
        """
        async with self._factory() as s, s.begin():
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
                    "original_filename": original_filename,
                    "file_format": file_format,
                    "compression": compression,
                    "size_bytes": size_bytes,
                    "content_hash_sha256": content_hash_sha256,
                    "object_store_key": object_store_key,
                    "uploaded_by": uploaded_by,
                },
            )

    async def get(self, file_id: uuid.UUID | str) -> dict[str, Any] | None:
        """Return ``{id, original_filename, object_store_key}`` for a file row.

        Used by the worker's PARSE_AND_INGEST handler to recover the
        bytes + filename it needs for re-parse. Does not filter by
        tenant because the worker has cross-tenant privilege when
        consuming job rows -- the job row itself binds tenancy.
        """
        async with self._factory() as s:
            result = await s.execute(
                sa.text("SELECT id, original_filename, object_store_key FROM flyquery_files WHERE id = :id"),
                {"id": file_id},
            )
            row = result.mappings().one_or_none()
            return dict(row) if row else None
