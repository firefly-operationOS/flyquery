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

"""Arrow / Feather reader (pyarrow IPC → Parquet conversion)."""

from __future__ import annotations

import asyncio
from pathlib import Path

from flyquery.core.services.ingestion.reader import (
    ColumnSchema,
    MaterialiseResult,
    ProposedTable,
    TableExtractionRules,
)

# File extensions handled by this reader.
_FEATHER_EXTS = frozenset({".feather"})
_ARROW_EXTS = frozenset({".arrow"})


class ArrowReader:
    formats = ("arrow", "feather")

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
    def _read_table(source_path: str):
        """Read a Feather v2 or Arrow IPC stream file into a pyarrow Table."""
        import pyarrow.feather as feather
        import pyarrow.ipc as ipc

        ext = Path(source_path).suffix.lower()
        if ext in _FEATHER_EXTS:
            return feather.read_table(source_path)
        # .arrow — try IPC stream first, fall back to feather
        try:
            with open(source_path, "rb") as f:
                reader = ipc.open_stream(f)
                return reader.read_all()
        except Exception:
            # Some .arrow files are written as Feather v2
            return feather.read_table(source_path)

    @staticmethod
    def _enumerate_sync(source_path: str) -> list[ProposedTable]:
        tbl = ArrowReader._read_table(source_path)
        return [
            ProposedTable(
                name=Path(source_path).stem,
                sheet_or_json_path=None,
                n_columns=tbl.num_columns,
                n_rows_estimate=tbl.num_rows,
            )
        ]

    @staticmethod
    def _materialise_sync(source_path: str, target_parquet_key: str) -> MaterialiseResult:
        import pyarrow.parquet as pq

        Path(target_parquet_key).parent.mkdir(parents=True, exist_ok=True)
        tbl = ArrowReader._read_table(source_path)
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
            n_rows_actual=tbl.num_rows,
            columns=columns,
        )
