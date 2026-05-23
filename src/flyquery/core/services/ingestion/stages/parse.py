# Copyright 2026 Firefly Software Solutions Inc
"""Stage 2 — parse: decompress → reader → enumerate tables → materialise Parquet.

For each ProposedTable:
- Materialise to Parquet under flyquery/{tenant}/{ws}/{ds}/tables/{table_id}/v{n}.parquet
- Insert flyquery_tables row (or look up existing row for re-upload)
- Return list of ParsedTable instances
"""

from __future__ import annotations

import logging
import re
import tempfile
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from flyquery.core.services.ingestion.compression import decompress_to_temp
from flyquery.core.services.ingestion.reader import (
    MaterialiseResult,
    ProposedTable,
    TableExtractionRules,
)
from flyquery.core.services.ingestion.reader_factory import get_reader
from flyquery.core.services.storage.object_store import ObjectStore

logger = logging.getLogger(__name__)

_SAFE_NAME_RE = re.compile(r"[^A-Za-z0-9_]+")


def _sanitise_name(name: str) -> str:
    return _SAFE_NAME_RE.sub("_", name).strip("_") or "table"


@dataclass
class ParsedTable:
    table_id: uuid.UUID
    name: str
    qualified_name: str
    sheet_or_json_path: str | None
    parquet_key: str
    result: MaterialiseResult


async def run_parse(
    *,
    tenant_id: str,
    workspace_id: uuid.UUID,
    dataset_id: uuid.UUID,
    file_id: uuid.UUID,
    local_temp_path: str,
    file_format: str,
    compression: str,
    object_store: ObjectStore,
    session_factory: async_sessionmaker[AsyncSession],
    settings: Any,  # FlyquerySettings
    # When re-uploading into an existing table slot, pass the existing table_id.
    # When None, new table rows are inserted.
    existing_table_id: uuid.UUID | None = None,
    dataset_name: str = "dataset",
    workspace_locale: str = "en-US",
    original_filename: str | None = None,
) -> list[ParsedTable]:
    """Execute Stage 2: parse."""
    # 1. Decompress if needed
    if compression != "none":
        decompressed_path = await decompress_to_temp(local_temp_path, compression)
    else:
        decompressed_path = local_temp_path
    cleanup_decompressed = decompressed_path != local_temp_path

    try:
        reader = get_reader(file_format=file_format, compression="none")
        rules = TableExtractionRules()
        proposed = await reader.enumerate_tables(decompressed_path, rules)
        logger.info(
            "stage=parse format=%s tables_found=%d", file_format, len(proposed)
        )

        parsed: list[ParsedTable] = []

        # When re-uploading into an existing slot, we only materialise the
        # first proposed table into that slot (the schema diff is handled in
        # reconcile). Multi-table re-uploads are not yet supported (Phase F).
        for i, pt in enumerate(proposed):
            if existing_table_id is not None and i > 0:
                logger.warning(
                    "re-upload produced %d tables; only first mapped to existing slot %s",
                    len(proposed),
                    existing_table_id,
                )
                break

            if existing_table_id is not None:
                table_id = existing_table_id
            else:
                table_id = uuid.uuid4()

            # If there's only one table (CSV/TSV/single-sheet), prefer the
            # original filename stem so the table is named "orders" not a
            # temp path like "tmpXXXX".
            if original_filename and len(proposed) == 1:
                raw_name = Path(original_filename).stem
            else:
                raw_name = pt.name
            safe_name = _sanitise_name(raw_name)
            qualified_name = f"{_sanitise_name(dataset_name)}.{safe_name}"

            # Build the Parquet key: determine version number
            snap_version = await _next_version(
                table_id, tenant_id, workspace_id, session_factory
            )
            parquet_key = (
                f"flyquery/{tenant_id}/{workspace_id}/{dataset_id}/"
                f"tables/{table_id}/v{snap_version}.parquet"
            )

            # Materialise Parquet to a local temp path first, then upload
            local_parquet = tempfile.mktemp(suffix=".parquet")  # noqa: S306
            try:
                mat_result = await reader.materialise(
                    decompressed_path,
                    pt,
                    local_parquet,
                    workspace_locale=workspace_locale,
                    type_infer_sample_rows=settings.type_infer_sample_rows,
                    max_title_rows=settings.max_title_rows,
                )

                # Upload Parquet to object store
                parquet_bytes = Path(local_parquet).read_bytes()
                await object_store.put(
                    parquet_key, parquet_bytes, "application/octet-stream"
                )
            finally:
                Path(local_parquet).unlink(missing_ok=True)

            # Insert or verify flyquery_tables row
            if existing_table_id is None:
                await _insert_table(
                    table_id=table_id,
                    tenant_id=tenant_id,
                    workspace_id=workspace_id,
                    dataset_id=dataset_id,
                    source_file_id=file_id,
                    name=safe_name,
                    qualified_name=qualified_name,
                    sheet_or_json_path=pt.sheet_or_json_path,
                    session_factory=session_factory,
                )

            # Update source_file_id on existing table
            if existing_table_id is not None:
                await _update_table_file(table_id, file_id, session_factory)

            parsed.append(
                ParsedTable(
                    table_id=table_id,
                    name=safe_name,
                    qualified_name=qualified_name,
                    sheet_or_json_path=pt.sheet_or_json_path,
                    parquet_key=parquet_key,
                    result=mat_result,
                )
            )
            logger.info(
                "stage=parse table_id=%s name=%s rows=%d cols=%d parquet_key=%s",
                table_id,
                safe_name,
                mat_result.n_rows_actual,
                len(mat_result.columns),
                parquet_key,
            )

        return parsed

    finally:
        if cleanup_decompressed:
            Path(decompressed_path).unlink(missing_ok=True)


async def _next_version(
    table_id: uuid.UUID,
    tenant_id: str,
    workspace_id: uuid.UUID,
    session_factory: async_sessionmaker[AsyncSession],
) -> int:
    """Return the next snapshot version number (1-based)."""
    async with session_factory() as s:
        result = await s.execute(
            sa.text(
                "SELECT count(*) FROM flyquery_schema_snapshots "
                "WHERE table_id = :tid AND tenant_id = :tenant"
            ),
            {"tid": table_id, "tenant": tenant_id},
        )
        count = result.scalar_one()
        return count + 1


async def _insert_table(
    *,
    table_id: uuid.UUID,
    tenant_id: str,
    workspace_id: uuid.UUID,
    dataset_id: uuid.UUID,
    source_file_id: uuid.UUID,
    name: str,
    qualified_name: str,
    sheet_or_json_path: str | None,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as s, s.begin():
        await s.execute(
            sa.text(
                """
                INSERT INTO flyquery_tables (
                    id, tenant_id, workspace_id, dataset_id,
                    source_file_id, name, qualified_name,
                    sheet_or_json_path, kind
                ) VALUES (
                    :id, :tenant_id, :workspace_id, :dataset_id,
                    :source_file_id, :name, :qualified_name,
                    :sheet_or_json_path, 'UPLOADED'
                )
                ON CONFLICT (dataset_id, name) DO NOTHING
                """
            ),
            {
                "id": table_id,
                "tenant_id": tenant_id,
                "workspace_id": workspace_id,
                "dataset_id": dataset_id,
                "source_file_id": source_file_id,
                "name": name,
                "qualified_name": qualified_name,
                "sheet_or_json_path": sheet_or_json_path,
            },
        )


async def _update_table_file(
    table_id: uuid.UUID,
    file_id: uuid.UUID,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as s, s.begin():
        await s.execute(
            sa.text(
                "UPDATE flyquery_tables SET source_file_id = :fid, updated_at = now() "
                "WHERE id = :tid"
            ),
            {"fid": file_id, "tid": table_id},
        )
