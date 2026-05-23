# Copyright 2026 Firefly Software Solutions Inc
"""JSON / JSONL reader with multi-table extraction."""

from __future__ import annotations

import asyncio
import json
import re
import tempfile
from pathlib import Path

from flyquery.core.services.ingestion.reader import (
    ColumnSchema,
    MaterialiseResult,
    ProposedTable,
    TableExtractionRules,
)


class JsonReader:
    formats = ("json", "jsonl")

    async def enumerate_tables(self, source_path: str, rules: TableExtractionRules) -> list[ProposedTable]:
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
            type_infer_sample_rows,
        )

    @staticmethod
    def _is_jsonl(source_path: str) -> bool:
        # JSONL has one JSON value per line; JSON has a single root.
        if source_path.lower().endswith(".jsonl") or source_path.lower().endswith(".ndjson"):
            return True
        # Cheap heuristic: read first 1KB, count lines that start with `{`
        with open(source_path, "rb") as f:
            head = f.read(1024).decode("utf-8", errors="replace")
        lines = [ln for ln in head.splitlines() if ln.strip()]
        return len(lines) > 1 and all(ln.lstrip().startswith("{") for ln in lines[:3])

    @staticmethod
    def _enumerate_sync(source_path: str, rules: TableExtractionRules) -> list[ProposedTable]:
        if JsonReader._is_jsonl(source_path):
            name = Path(source_path).stem
            return [
                ProposedTable(
                    name=re.sub(r"[^A-Za-z0-9_]+", "_", name) or "table",
                    sheet_or_json_path=None,
                    n_columns=0,  # filled at materialise
                    n_rows_estimate=0,
                )
            ]
        # Plain JSON: inspect the root.
        with open(source_path, encoding="utf-8") as f:
            doc = json.load(f)
        if isinstance(doc, list):
            return [
                ProposedTable(
                    name=Path(source_path).stem,
                    sheet_or_json_path=None,
                    n_columns=0,
                    n_rows_estimate=len(doc),
                )
            ]
        if isinstance(doc, dict):
            paths = set(rules.json_paths) if rules.json_paths else None
            out: list[ProposedTable] = []
            for k, v in doc.items():
                if not isinstance(v, list):
                    continue
                if paths is not None and k not in paths:
                    continue
                out.append(
                    ProposedTable(
                        name=re.sub(r"[^A-Za-z0-9_]+", "_", k) or "table",
                        sheet_or_json_path=k,
                        n_columns=0,
                        n_rows_estimate=len(v),
                    )
                )
            if not out:
                # Fall through: treat object as a single 1-row table
                out.append(
                    ProposedTable(
                        name=Path(source_path).stem,
                        sheet_or_json_path=None,
                        n_columns=len(doc),
                        n_rows_estimate=1,
                    )
                )
            return out
        raise ValueError(f"unsupported JSON root type: {type(doc).__name__}")

    @staticmethod
    def _materialise_sync(
        source_path: str,
        table: ProposedTable,
        target_parquet_key: str,
        type_infer_sample_rows: int,
    ) -> MaterialiseResult:
        import duckdb

        Path(target_parquet_key).parent.mkdir(parents=True, exist_ok=True)

        # If the table corresponds to a single JSON-path inside a top-level
        # object, extract that array to a temp JSONL.
        if table.sheet_or_json_path:
            with open(source_path, encoding="utf-8") as f:
                doc = json.load(f)
            arr = doc[table.sheet_or_json_path]
            with tempfile.NamedTemporaryFile(
                suffix=".jsonl", mode="w", delete=False, encoding="utf-8"
            ) as tmp:
                for row in arr:
                    tmp.write(json.dumps(row))
                    tmp.write("\n")
                tmp_path = tmp.name
            input_path = tmp_path
        else:
            input_path = source_path
            tmp_path = None

        try:
            conn = duckdb.connect()
            try:
                # DuckDB 1.5 requires literal paths in COPY … TO
                src = input_path.replace("'", "''")
                tgt = target_parquet_key.replace("'", "''")
                conn.execute(
                    f"COPY (SELECT * FROM read_json_auto('{src}', "
                    f"sample_size={type_infer_sample_rows}, "
                    f"format='auto')) "
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
            if tmp_path:
                Path(tmp_path).unlink(missing_ok=True)

        byte_size = Path(target_parquet_key).stat().st_size
        return MaterialiseResult(
            target_parquet_key=target_parquet_key,
            parquet_byte_size=byte_size,
            n_rows_actual=rows_ct,
            columns=columns,
        )
