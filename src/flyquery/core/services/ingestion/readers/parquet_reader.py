# Copyright 2026 Firefly Software Solutions Inc
"""Parquet reader (pass-through copy + schema introspection)."""

from __future__ import annotations

import asyncio
import shutil
from pathlib import Path

from flyquery.core.services.ingestion.reader import (
    ColumnSchema,
    MaterialiseResult,
    ProposedTable,
    TableExtractionRules,
)


class ParquetReader:
    formats = ("parquet",)

    async def enumerate_tables(self, source_path: str, rules: TableExtractionRules) -> list[ProposedTable]:
        return await asyncio.to_thread(self._enumerate_sync, source_path)

    async def materialise(
        self,
        source_path: str,
        table: ProposedTable,
        target_parquet_key: str,
        *,
        workspace_locale: str,
        type_infer_sample_rows: int,
        max_title_rows: int = 3,
    ) -> MaterialiseResult:
        return await asyncio.to_thread(self._materialise_sync, source_path, target_parquet_key)

    @staticmethod
    def _enumerate_sync(source_path: str) -> list[ProposedTable]:
        import pyarrow.parquet as pq

        meta = pq.ParquetFile(source_path)
        return [
            ProposedTable(
                name=Path(source_path).stem,
                sheet_or_json_path=None,
                n_columns=len(meta.schema.names),
                n_rows_estimate=meta.metadata.num_rows,
            )
        ]

    @staticmethod
    def _materialise_sync(source_path: str, target_parquet_key: str) -> MaterialiseResult:
        import pyarrow.parquet as pq

        Path(target_parquet_key).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_path, target_parquet_key)
        meta = pq.ParquetFile(target_parquet_key)
        names = meta.schema.names
        # Use logical type names from the Arrow schema for richer types
        arrow_schema = meta.schema_arrow
        columns = tuple(
            ColumnSchema(
                name=names[i],
                data_type=str(arrow_schema.field(names[i]).type),
                is_nullable=arrow_schema.field(names[i]).nullable,
                position=i,
            )
            for i in range(len(names))
        )
        return MaterialiseResult(
            target_parquet_key=target_parquet_key,
            parquet_byte_size=Path(target_parquet_key).stat().st_size,
            n_rows_actual=meta.metadata.num_rows,
            columns=columns,
        )
