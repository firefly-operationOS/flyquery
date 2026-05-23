# Copyright 2026 Firefly Software Solutions Inc
"""XLSX / XLS / ODS reader (python-calamine)."""

from __future__ import annotations

import asyncio
import re
import tempfile
from pathlib import Path

from flyquery.core.services.ingestion.reader import (
    ColumnSchema,
    FileReader,
    MaterialiseResult,
    ProposedTable,
    TableExtractionRules,
)

_SHEET_NAME_RE = re.compile(r"[^A-Za-z0-9_]+")


class ExcelReader:
    formats = ("xlsx", "xls", "ods")

    async def enumerate_tables(
        self, source_path: str, rules: TableExtractionRules
    ) -> list[ProposedTable]:
        return await asyncio.to_thread(self._enumerate_sync, source_path, rules)

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
        return await asyncio.to_thread(
            self._materialise_sync,
            source_path,
            table,
            target_parquet_key,
            workspace_locale,
            type_infer_sample_rows,
            max_title_rows,
        )

    @staticmethod
    def _sanitise(name: str) -> str:
        return _SHEET_NAME_RE.sub("_", name).strip("_") or "sheet"

    @staticmethod
    def _enumerate_sync(source_path: str, rules: TableExtractionRules) -> list[ProposedTable]:
        from python_calamine import CalamineWorkbook

        wb = CalamineWorkbook.from_path(source_path)
        out: list[ProposedTable] = []
        allow = set(rules.sheet_allowlist) if rules.sheet_allowlist else None
        for name in wb.sheet_names:
            if allow is not None and name not in allow:
                continue
            sheet = wb.get_sheet_by_name(name)
            rows = sheet.to_python(skip_empty_area=True)
            if not rows:
                continue
            header = rows[0]
            n_cols = len(header)
            n_rows = max(0, len(rows) - 1)
            out.append(
                ProposedTable(
                    name=ExcelReader._sanitise(name),
                    sheet_or_json_path=name,
                    n_columns=n_cols,
                    n_rows_estimate=n_rows,
                )
            )
        return out

    @staticmethod
    def _materialise_sync(
        source_path: str,
        table: ProposedTable,
        target_parquet_key: str,
        workspace_locale: str,
        type_infer_sample_rows: int,
        max_title_rows: int,
    ) -> MaterialiseResult:
        # Strategy: extract the sheet to a temp CSV, then hand off to DuckDB
        # (so type inference + Parquet output is uniform across formats).
        import csv

        import duckdb
        from python_calamine import CalamineWorkbook

        Path(target_parquet_key).parent.mkdir(parents=True, exist_ok=True)
        wb = CalamineWorkbook.from_path(source_path)
        sheet = wb.get_sheet_by_name(table.sheet_or_json_path or table.name)
        rows = sheet.to_python(skip_empty_area=True)

        # Strip merged-cell title rows: heuristic = rows with a single non-empty
        # cell before the actual header.
        body_start = 0
        for i in range(min(max_title_rows, len(rows))):
            non_empty = sum(1 for c in rows[i] if c not in (None, ""))
            if non_empty <= 1:
                body_start = i + 1
            else:
                break

        if body_start >= len(rows):
            raise ValueError(f"sheet {table.sheet_or_json_path!r} has no usable rows")

        with tempfile.NamedTemporaryFile(
            suffix=".csv", mode="w", newline="", delete=False, encoding="utf-8"
        ) as tmp:
            writer = csv.writer(tmp)
            for r in rows[body_start:]:
                writer.writerow([str(c) if c is not None else "" for c in r])
            tmp_path = tmp.name

        try:
            conn = duckdb.connect()
            try:
                # DuckDB 1.5 requires literal paths in COPY … TO
                src = tmp_path.replace("'", "''")
                tgt = target_parquet_key.replace("'", "''")
                conn.execute(
                    f"COPY (SELECT * FROM read_csv_auto('{src}', "
                    f"sample_size={type_infer_sample_rows}, "
                    f"auto_detect=true, ignore_errors=false)) "
                    f"TO '{tgt}' (FORMAT PARQUET, COMPRESSION 'snappy')"
                )
                rows_ct = conn.execute(
                    "SELECT count(*) FROM read_parquet(?)", [target_parquet_key]
                ).fetchone()[0]
                schema = conn.execute(
                    "SELECT * FROM (DESCRIBE SELECT * FROM read_parquet(?))", [target_parquet_key]
                ).fetchall()
                columns = tuple(
                    ColumnSchema(name=r[0], data_type=r[1], is_nullable=(r[2] == "YES"), position=i)
                    for i, r in enumerate(schema)
                )
            finally:
                conn.close()
        finally:
            Path(tmp_path).unlink(missing_ok=True)

        byte_size = Path(target_parquet_key).stat().st_size
        return MaterialiseResult(
            target_parquet_key=target_parquet_key,
            parquet_byte_size=byte_size,
            n_rows_actual=rows_ct,
            columns=columns,
        )
