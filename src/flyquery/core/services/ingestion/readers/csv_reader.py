# Copyright 2026 Firefly Software Solutions Inc
"""CSV / TSV reader (DuckDB-driven + encoding+delimiter sniffing)."""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from flyquery.core.services.ingestion.reader import (
    ColumnSchema,
    MaterialiseResult,
    ProposedTable,
    TableExtractionRules,
)

logger = logging.getLogger(__name__)


class CsvReader:
    formats = ("csv", "tsv")

    async def enumerate_tables(self, source_path: str, rules: TableExtractionRules) -> list[ProposedTable]:
        n_columns, n_rows_estimate = await asyncio.to_thread(self._head_columns_and_estimate, source_path)
        name = Path(source_path).stem  # sanitised in caller
        return [
            ProposedTable(
                name=name,
                sheet_or_json_path=None,
                n_columns=n_columns,
                n_rows_estimate=n_rows_estimate,
            )
        ]

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
            target_parquet_key,
            workspace_locale,
            type_infer_sample_rows,
        )

    @staticmethod
    def _head_columns_and_estimate(path: str) -> tuple[int, int]:
        """Sniff the dialect, count columns, estimate row count."""
        import duckdb

        # DuckDB auto_detect handles encoding (UTF-8 default; falls back) +
        # delimiter sniff.
        conn = duckdb.connect()
        try:
            cols = conn.execute(
                "SELECT count(*) FROM (DESCRIBE SELECT * FROM read_csv_auto(?, sample_size=4096))",
                [path],
            ).fetchone()[0]
            # Estimate via byte size; precise count happens during materialise.
            byte_size = Path(path).stat().st_size
            est = max(1, byte_size // 80)  # ~80 bytes per row rough guess
            return cols, est
        finally:
            conn.close()

    @staticmethod
    def _materialise_sync(
        source_path: str,
        target_parquet_key: str,
        workspace_locale: str,
        type_infer_sample_rows: int,
    ) -> MaterialiseResult:
        import duckdb

        Path(target_parquet_key).parent.mkdir(parents=True, exist_ok=True)
        conn = duckdb.connect()
        try:
            # Use DuckDB's read_csv_auto with locale-aware date format hint.
            # Note: DuckDB 1.5 requires literal path strings in COPY … TO;
            # positional ? params work for SELECT but not for COPY target.
            date_fmt = _date_format_for_locale(workspace_locale)
            opts = f"sample_size={type_infer_sample_rows}, auto_detect=true, ignore_errors=false"
            if date_fmt:
                opts += f", dateformat='{date_fmt}'"
            src = source_path.replace("'", "''")
            tgt = target_parquet_key.replace("'", "''")
            conn.execute(
                f"COPY (SELECT * FROM read_csv_auto('{src}', {opts})) "
                f"TO '{tgt}' (FORMAT PARQUET, COMPRESSION 'snappy')"
            )
            rows = conn.execute("SELECT count(*) FROM read_parquet(?)", [target_parquet_key]).fetchone()[0]
            schema = conn.execute(
                "SELECT * FROM (DESCRIBE SELECT * FROM read_parquet(?))", [target_parquet_key]
            ).fetchall()
            columns = tuple(
                ColumnSchema(
                    name=r[0],
                    data_type=r[1],
                    is_nullable=(r[2] == "YES"),
                    position=i,
                )
                for i, r in enumerate(schema)
            )
            byte_size = Path(target_parquet_key).stat().st_size
            return MaterialiseResult(
                target_parquet_key=target_parquet_key,
                parquet_byte_size=byte_size,
                n_rows_actual=rows,
                columns=columns,
            )
        finally:
            conn.close()


def _date_format_for_locale(locale: str) -> str | None:
    """Pick DuckDB's ``dateformat`` hint from a workspace locale.

    DuckDB auto-detect already handles ISO 8601 dates (``YYYY-MM-DD``) and
    US-style ``MM/DD/YYYY`` dates without an explicit hint. The only case where
    a hint is *required* is for DD/MM/YYYY European locales, because DuckDB's
    default ambiguity resolution prefers MM/DD interpretation when day ≤ 12
    (e.g. ``01/02/2026`` → Feb 1 without a hint, Jan 2 with ``%m/%d/%Y``).

    Applying ``%m/%d/%Y`` to a CSV that already contains ISO-format dates
    (``2026-01-15``) causes DuckDB to widen the column type from DATE to
    TIMESTAMP, which is a schema-quality regression. Since DuckDB handles
    both ISO and MM/DD/YYYY automatically, we only issue the DD/MM/YYYY hint
    for the locales where it is unambiguously needed.

    Locales with DD/MM/YYYY calendar convention:
    en-GB, fr (French), es (Spanish), de (German), it (Italian),
    pt (Portuguese), nl (Dutch), and most of the rest of the world.
    """
    if locale.startswith(("en-GB", "fr", "es", "de", "it", "pt", "nl")):
        return "%d/%m/%Y"
    return None
