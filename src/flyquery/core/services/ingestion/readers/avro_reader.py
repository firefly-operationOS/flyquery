# Copyright 2026 Firefly Software Solutions Inc
"""Avro reader (fastavro → pyarrow → Parquet conversion)."""

from __future__ import annotations

import asyncio
from pathlib import Path

from flyquery.core.services.ingestion.reader import (
    ColumnSchema,
    MaterialiseResult,
    ProposedTable,
    TableExtractionRules,
)


class AvroReader:
    formats = ("avro",)

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
        import fastavro

        with open(source_path, "rb") as f:
            reader = fastavro.reader(f)
            schema = reader.writer_schema
        fields = schema.get("fields", [])
        n_cols = len(fields)
        # Row count requires full scan; estimate from file size.
        byte_size = Path(source_path).stat().st_size
        return [
            ProposedTable(
                name=Path(source_path).stem,
                sheet_or_json_path=None,
                n_columns=n_cols,
                n_rows_estimate=max(1, byte_size // 64),
            )
        ]

    @staticmethod
    def _materialise_sync(source_path: str, target_parquet_key: str) -> MaterialiseResult:
        import fastavro
        import pyarrow as pa
        import pyarrow.parquet as pq

        Path(target_parquet_key).parent.mkdir(parents=True, exist_ok=True)
        with open(source_path, "rb") as f:
            reader = fastavro.reader(f)
            records = list(reader)

        if not records:
            raise ValueError(f"Avro file {source_path!r} contains no records")

        tbl = pa.Table.from_pylist(records)
        pq.write_table(tbl, target_parquet_key, compression="snappy")

        schema = tbl.schema
        columns = tuple(
            ColumnSchema(
                name=schema.field(i).name,
                data_type=str(schema.field(i).type),
                is_nullable=schema.field(i).nullable,
                position=i,
            )
            for i in range(len(schema))
        )
        return MaterialiseResult(
            target_parquet_key=target_parquet_key,
            parquet_byte_size=Path(target_parquet_key).stat().st_size,
            n_rows_actual=len(records),
            columns=columns,
        )
