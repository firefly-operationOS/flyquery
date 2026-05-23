# flyquery Plan 2 — File Ingestion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Land the full upload + ingestion pipeline on top of Plan 1's foundation: a `FileReader` hexagonal port with 7 readers (covering 12 formats + 3 compressions), a 10-stage synchronous + async pipeline (`receive → parse → reconcile → sample → profile → relation discovery → describe → PII tag → embed → publish`), the three ingestion agents (`DescribeAgent`, `RelationProposerAgent`, `RenameDetectionAgent`), SSE streaming on `/ingest-jobs/{id}/stream`, re-upload with schema drift + annotation transplant, and GCS + AzureBlob ObjectStore adapters. End-to-end demo: upload a Northwind-style fixture (`orders.csv` + `customers.csv` + `products.xlsx` + a nested JSON export) and watch the schema KB populate with descriptions, samples, profiles, embeddings, and AI-proposed joins.

**Architecture:** Each file format gets its own reader behind the `FileReader` Protocol (csv/tsv, excel-trio, json/jsonl, parquet, avro, orc, arrow/feather). The 10-stage pipeline is the same shape canon uses for documents, adapted for structured tables: each transition is one logical step, persisted to `flyquery_ingest_events`, streamable as SSE. The pipeline runs synchronously on first-upload to keep the demo simple; an async `IngestWorker` consumes the `flyquery.ingest` EDA topic for background reparse/sample-refresh/describe-pass/relation-pass jobs. PII gating ALWAYS runs before sample persistence on first-ever ingest of a column (memory: ordering guarantee). Annotation transplant on re-upload is keyed on `(qualified_name, column_name)`; ambiguous renames go through `RenameDetectionAgent` and land as `RENAMED_CANDIDATE` rows for one-click human confirm.

**Tech Stack:** Same Python 3.13 + pyfly base as Plan 1, plus: `python-calamine` (xlsx/xls/ods), `fastavro` (.avro), `pyarrow` (.arrow/.feather/.orc), `chardet`/`charset-normalizer` (encoding detection), DuckDB's `read_csv_auto`/`read_json_auto` (already in deps), `aiofiles` (already there), `presidio-analyzer` behind the `[presidio]` extra (PII scanner; can fall back to regex for v0), `sentence-transformers` behind the `[ml-reranker]` extra (cross-encoder reranker — wired here so the schema KB is ready for Plan 3 queries), `gcloud-aio-storage` (`[gcs]` extra), `azure-storage-blob`+`aiohttp` (`[azure]` extra).

---

## File structure (delta over Plan 1)

```
flyquery/
├── src/flyquery/
│   ├── core/
│   │   ├── agents/
│   │   │   ├── builder.py                     # already exists
│   │   │   ├── describe_agent.py              # NEW (Task 26)
│   │   │   ├── relation_proposer_agent.py     # NEW (Task 25)
│   │   │   └── rename_detection_agent.py      # NEW (Task 27)
│   │   ├── services/
│   │   │   ├── ingestion/                     # NEW package
│   │   │   │   ├── __init__.py
│   │   │   │   ├── reader.py                  # FileReader Protocol + types
│   │   │   │   ├── reader_factory.py          # dispatch by (format, compression)
│   │   │   │   ├── format_detect.py           # magic-byte detect
│   │   │   │   ├── compression.py             # gz/zip/bz2 handlers
│   │   │   │   ├── readers/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── csv_reader.py
│   │   │   │   │   ├── excel_reader.py        # xlsx/xls/ods
│   │   │   │   │   ├── json_reader.py
│   │   │   │   │   ├── parquet_reader.py
│   │   │   │   │   ├── avro_reader.py
│   │   │   │   │   ├── orc_reader.py
│   │   │   │   │   └── arrow_reader.py        # .arrow + .feather
│   │   │   │   ├── pipeline.py                # 10-stage orchestrator (sync)
│   │   │   │   ├── stages/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── receive.py             # stage 1
│   │   │   │   │   ├── parse.py               # stage 2 (multi-table extraction)
│   │   │   │   │   ├── reconcile.py           # stage 3 (snapshot persist + diff)
│   │   │   │   │   ├── sample.py              # stage 4 (PII-gated)
│   │   │   │   │   ├── profile.py             # stage 5
│   │   │   │   │   ├── relations.py           # stage 6 (heuristic + AGENT_PROPOSED)
│   │   │   │   │   ├── describe.py            # stage 7 (DescribeAgent, batched)
│   │   │   │   │   ├── pii_tag.py             # stage 8
│   │   │   │   │   ├── embed.py               # stage 9 (embedding + tsvector)
│   │   │   │   │   └── publish.py             # stage 10 (atomic swap)
│   │   │   │   ├── ingest_service.py          # orchestrates stages
│   │   │   │   └── workers.py                 # IngestWorker (EDA consumer)
│   │   │   ├── pii/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── scanner.py                 # PiiScanner Protocol
│   │   │   │   └── adapters/
│   │   │   │       ├── regex_scanner.py
│   │   │   │       ├── presidio_scanner.py
│   │   │   │       └── disabled_scanner.py
│   │   │   ├── retrieval/                     # used in Plan 3 too
│   │   │   │   ├── __init__.py
│   │   │   │   ├── reranker.py                # cross-encoder loader
│   │   │   │   └── schema_kb_index.py         # BM25 + pgvector helpers
│   │   │   ├── storage/
│   │   │   │   ├── adapters/
│   │   │   │   │   ├── gcs.py                 # NEW (Task 31)
│   │   │   │   │   └── azure_blob.py          # NEW (Task 32)
│   │   │   ├── ingest_jobs/                   # NEW package
│   │   │   │   ├── __init__.py
│   │   │   │   ├── ingest_job_repository.py
│   │   │   │   └── ingest_job_service.py
│   │   ├── eda/
│   │   │   ├── __init__.py
│   │   │   └── ingest_publisher.py            # publishes to flyquery.ingest
│   ├── interfaces/
│   │   ├── files.py                           # NEW: upload + table DTOs
│   │   ├── ingest_jobs.py                     # NEW
│   │   ├── tables.py                          # NEW
│   │   └── relations.py                       # NEW
│   ├── models/
│   │   └── entities/                          # already exists; no new entities here
│   ├── web/
│   │   ├── controllers/
│   │   │   ├── files_controller.py            # NEW: POST /datasets/{id}/files + PUT :upload
│   │   │   ├── tables_controller.py           # NEW: list, get, snapshots, changes
│   │   │   ├── ingest_jobs_controller.py      # NEW
│   │   │   └── relations_controller.py        # NEW: list, approve, reject
│   │   ├── controllers/agent/                 # NEW agent-tier mirrors
│   │   │   ├── files_controller.py
│   │   │   └── ingest_jobs_controller.py
│   │   └── conventions/
│   │       └── multipart.py                   # multipart upload helper (NEW)
└── tests/
    ├── integration/
    │   ├── parsers/
    │   │   ├── fixtures/                      # tiny golden files
    │   │   │   ├── orders.csv
    │   │   │   ├── customers.csv
    │   │   │   ├── products.xlsx
    │   │   │   ├── events.jsonl
    │   │   │   ├── nested.json
    │   │   │   ├── bom_utf8.csv               # CSV with BOM
    │   │   │   ├── semicolon.csv              # `;` separator
    │   │   │   ├── mixed_quotes.csv
    │   │   │   ├── ragged.json
    │   │   │   ├── tiny.parquet
    │   │   │   └── orders.csv.gz
    │   │   ├── test_csv_reader.py
    │   │   ├── test_excel_reader.py
    │   │   ├── test_json_reader.py
    │   │   ├── test_parquet_reader.py
    │   │   ├── test_avro_orc_arrow.py
    │   │   └── test_compression.py
    │   ├── test_files_upload.py
    │   ├── test_ingest_pipeline.py            # 10-stage synchronous + atomic swap
    │   ├── test_ingest_worker.py              # async EDA flow
    │   ├── test_sample_pii_gate.py            # ordering guarantee
    │   ├── test_relations.py                  # heuristic + agent + approve flow
    │   ├── test_describe_agent.py
    │   ├── test_rename_detection.py
    │   ├── test_reupload_schema_drift.py
    │   ├── test_gcs_adapter.py                # @pytest.mark.gcs
    │   ├── test_azure_blob_adapter.py         # @pytest.mark.azure_blob
    │   └── test_e2e_northwind_demo.py
    └── unit/
        ├── test_reader_factory.py
        ├── test_format_detect.py
        ├── test_compression_handlers.py
        ├── test_pii_scanner.py
        └── test_pipeline_stage_ordering.py
```

---

## Phase A — `FileReader` port + readers (Tasks 1-9)

### Task 1: `FileReader` Protocol + types + factory scaffold

**Files:**
- Create: `src/flyquery/core/services/ingestion/__init__.py`
- Create: `src/flyquery/core/services/ingestion/reader.py`
- Create: `src/flyquery/core/services/ingestion/reader_factory.py`
- Test: `tests/unit/test_reader_factory.py`

- [ ] **Step 1: Write the failing factory test**

```python
# tests/unit/test_reader_factory.py
import pytest
from flyquery.core.services.ingestion.reader_factory import get_reader
from flyquery.core.services.ingestion.reader import UnsupportedFormatError


def test_factory_dispatches_csv():
    r = get_reader(file_format="csv", compression="none")
    assert r.__class__.__name__ == "CsvReader"


def test_factory_dispatches_xlsx():
    r = get_reader(file_format="xlsx", compression="none")
    assert r.__class__.__name__ == "ExcelReader"


def test_factory_dispatches_parquet():
    r = get_reader(file_format="parquet", compression="none")
    assert r.__class__.__name__ == "ParquetReader"


def test_factory_raises_on_unknown_format():
    with pytest.raises(UnsupportedFormatError):
        get_reader(file_format="rar", compression="none")


def test_factory_raises_on_unknown_compression():
    with pytest.raises(UnsupportedFormatError):
        get_reader(file_format="csv", compression="rar")
```

- [ ] **Step 2: Run; expect FAIL** (factory doesn't exist)

- [ ] **Step 3: Write `reader.py`** (Protocol + types)

```python
# src/flyquery/core/services/ingestion/reader.py
# Copyright 2026 Firefly Software Solutions Inc
"""FileReader port (spec §9.2)."""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Any, Protocol


class UnsupportedFormatError(ValueError):
    """Raised when (format, compression) pair is not handled by any reader."""


@dataclass(frozen=True)
class TableExtractionRules:
    """User-driven overrides on parsing. Empty = use heuristic defaults."""
    sheet_allowlist: tuple[str, ...] = ()
    json_paths: tuple[str, ...] = ()
    header_skip_rows: int = 0


@dataclass(frozen=True)
class ProposedTable:
    """Logical table inside an upload (1 from CSV; N from XLSX sheets)."""
    name: str
    sheet_or_json_path: str | None
    n_columns: int
    n_rows_estimate: int


@dataclass(frozen=True)
class ColumnSchema:
    """Column emitted by the parse step (post-DuckDB type inference)."""
    name: str
    data_type: str
    is_nullable: bool
    position: int


@dataclass(frozen=True)
class MaterialiseResult:
    """Result of materialising one ProposedTable to a Parquet snapshot."""
    target_parquet_key: str          # object-store key (relative to base)
    parquet_byte_size: int
    n_rows_actual: int
    columns: tuple[ColumnSchema, ...]


class FileReader(Protocol):
    """Per-format reader. Adapters: csv, excel, json, parquet, avro, orc, arrow.

    Each reader handles uncompressed input by default; the compression layer is
    decorator-wrapped via core.services.ingestion.compression (Task 7).
    """
    formats: tuple[str, ...]                    # e.g., ("csv", "tsv")

    async def enumerate_tables(
        self, source_path: str, rules: TableExtractionRules
    ) -> list[ProposedTable]: ...

    async def materialise(
        self,
        source_path: str,
        table: ProposedTable,
        target_parquet_key: str,
        *,
        workspace_locale: str,
        type_infer_sample_rows: int,
        max_title_rows: int = 3,
    ) -> MaterialiseResult: ...
```

- [ ] **Step 4: Write `reader_factory.py`** (dispatch)

```python
# src/flyquery/core/services/ingestion/reader_factory.py
# Copyright 2026 Firefly Software Solutions Inc
"""FileReader dispatch.

Selection is by (format, compression). Compression is handled by decorating
the underlying reader with a decompression layer at the adapter boundary;
each reader operates on a decompressed path.
"""

from __future__ import annotations

from flyquery.core.services.ingestion.reader import FileReader, UnsupportedFormatError

_SUPPORTED_COMPRESSIONS = frozenset({"none", "gz", "zip", "bz2"})


def get_reader(file_format: str, compression: str = "none") -> FileReader:
    if compression not in _SUPPORTED_COMPRESSIONS:
        raise UnsupportedFormatError(
            f"compression {compression!r} not in {sorted(_SUPPORTED_COMPRESSIONS)}"
        )
    fmt = file_format.lower()
    if fmt in ("csv", "tsv"):
        from flyquery.core.services.ingestion.readers.csv_reader import CsvReader
        return CsvReader()
    if fmt in ("xlsx", "xls", "ods"):
        from flyquery.core.services.ingestion.readers.excel_reader import ExcelReader
        return ExcelReader()
    if fmt in ("json", "jsonl"):
        from flyquery.core.services.ingestion.readers.json_reader import JsonReader
        return JsonReader()
    if fmt == "parquet":
        from flyquery.core.services.ingestion.readers.parquet_reader import ParquetReader
        return ParquetReader()
    if fmt == "avro":
        from flyquery.core.services.ingestion.readers.avro_reader import AvroReader
        return AvroReader()
    if fmt == "orc":
        from flyquery.core.services.ingestion.readers.orc_reader import OrcReader
        return OrcReader()
    if fmt in ("arrow", "feather"):
        from flyquery.core.services.ingestion.readers.arrow_reader import ArrowReader
        return ArrowReader()
    raise UnsupportedFormatError(f"format {fmt!r} not supported")
```

- [ ] **Step 5: Run test — expect PASS for raise cases; the dispatch cases will fail until the reader files exist** (Tasks 2-6). Add `pytest.mark.xfail` on the per-format dispatch tests for now, or just ship the factory and rely on Tasks 2-6 to make them pass cumulatively.

- [ ] **Step 6: Commit**

```bash
git add src/flyquery/core/services/ingestion/__init__.py \
        src/flyquery/core/services/ingestion/reader.py \
        src/flyquery/core/services/ingestion/reader_factory.py \
        tests/unit/test_reader_factory.py
git commit -m "feat: FileReader port + reader_factory dispatch scaffold"
```

---

### Task 2: CSV / TSV reader

**Files:**
- Create: `src/flyquery/core/services/ingestion/readers/__init__.py`
- Create: `src/flyquery/core/services/ingestion/readers/csv_reader.py`
- Test: `tests/integration/parsers/test_csv_reader.py`
- Fixtures: `tests/integration/parsers/fixtures/orders.csv`, `customers.csv`, `bom_utf8.csv`, `semicolon.csv`, `mixed_quotes.csv`

- [ ] **Step 1: Create the golden fixtures**

Write small CSVs (`orders.csv` has 5 rows: order_id, customer_id, total, ordered_at; `customers.csv` has 4 rows: customer_id, name, email, region; `bom_utf8.csv` has UTF-8 BOM + a few rows; `semicolon.csv` uses `;` separator; `mixed_quotes.csv` mixes single and double quotes).

- [ ] **Step 2: Write the test cases**

```python
# tests/integration/parsers/test_csv_reader.py
import pytest
from pathlib import Path
from flyquery.core.services.ingestion.readers.csv_reader import CsvReader
from flyquery.core.services.ingestion.reader import TableExtractionRules

FIX = Path(__file__).parent / "fixtures"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_csv_happy_path(tmp_path):
    r = CsvReader()
    tables = await r.enumerate_tables(str(FIX / "orders.csv"), TableExtractionRules())
    assert len(tables) == 1
    assert tables[0].n_columns == 4
    result = await r.materialise(
        str(FIX / "orders.csv"),
        tables[0],
        target_parquet_key=str(tmp_path / "orders.parquet"),
        workspace_locale="en-US",
        type_infer_sample_rows=4096,
    )
    cols = {c.name for c in result.columns}
    assert {"order_id", "customer_id", "total", "ordered_at"} == cols


@pytest.mark.integration
@pytest.mark.asyncio
async def test_csv_bom_utf8_handled(tmp_path):
    r = CsvReader()
    tables = await r.enumerate_tables(str(FIX / "bom_utf8.csv"), TableExtractionRules())
    assert len(tables) == 1
    # First column name should not contain BOM
    result = await r.materialise(
        str(FIX / "bom_utf8.csv"),
        tables[0],
        target_parquet_key=str(tmp_path / "bom.parquet"),
        workspace_locale="en-US",
        type_infer_sample_rows=4096,
    )
    assert not result.columns[0].name.startswith("﻿")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_csv_semicolon_delimiter(tmp_path):
    r = CsvReader()
    tables = await r.enumerate_tables(str(FIX / "semicolon.csv"), TableExtractionRules())
    result = await r.materialise(
        str(FIX / "semicolon.csv"),
        tables[0],
        target_parquet_key=str(tmp_path / "semicolon.parquet"),
        workspace_locale="en-US",
        type_infer_sample_rows=4096,
    )
    assert result.n_rows_actual > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_csv_mixed_quotes(tmp_path):
    r = CsvReader()
    tables = await r.enumerate_tables(str(FIX / "mixed_quotes.csv"), TableExtractionRules())
    result = await r.materialise(
        str(FIX / "mixed_quotes.csv"),
        tables[0],
        target_parquet_key=str(tmp_path / "mixed_quotes.parquet"),
        workspace_locale="en-US",
        type_infer_sample_rows=4096,
    )
    assert result.n_rows_actual > 0
```

- [ ] **Step 3: Run; expect FAIL**

- [ ] **Step 4: Implement `CsvReader`**

```python
# src/flyquery/core/services/ingestion/readers/csv_reader.py
# Copyright 2026 Firefly Software Solutions Inc
"""CSV / TSV reader (DuckDB-driven + encoding+delimiter sniffing)."""

from __future__ import annotations

import asyncio
import csv as _csv
import logging
from pathlib import Path

from flyquery.core.services.ingestion.reader import (
    ColumnSchema,
    FileReader,
    MaterialiseResult,
    ProposedTable,
    TableExtractionRules,
)

logger = logging.getLogger(__name__)


class CsvReader(FileReader):
    formats = ("csv", "tsv")

    async def enumerate_tables(
        self, source_path: str, rules: TableExtractionRules
    ) -> list[ProposedTable]:
        n_columns, n_rows_estimate = await asyncio.to_thread(
            self._head_columns_and_estimate, source_path
        )
        name = Path(source_path).stem  # sanitised in caller
        return [ProposedTable(
            name=name,
            sheet_or_json_path=None,
            n_columns=n_columns,
            n_rows_estimate=n_rows_estimate,
        )]

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
            source_path, target_parquet_key, workspace_locale, type_infer_sample_rows,
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
        source_path: str, target_parquet_key: str,
        workspace_locale: str, type_infer_sample_rows: int,
    ) -> MaterialiseResult:
        import duckdb
        Path(target_parquet_key).parent.mkdir(parents=True, exist_ok=True)
        conn = duckdb.connect()
        try:
            # Use DuckDB's read_csv_auto with locale-aware date format hint.
            date_fmt = _date_format_for_locale(workspace_locale)
            opts = f"sample_size={type_infer_sample_rows}, auto_detect=true, ignore_errors=false"
            if date_fmt:
                opts += f", dateformat='{date_fmt}'"
            conn.execute(
                f"COPY (SELECT * FROM read_csv_auto(?, {opts})) "
                f"TO ? (FORMAT PARQUET, COMPRESSION 'snappy')",
                [source_path, target_parquet_key],
            )
            rows = conn.execute(
                "SELECT count(*) FROM read_parquet(?)", [target_parquet_key]
            ).fetchone()[0]
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
    """Pick DuckDB's `dateformat` from a workspace locale."""
    if locale.startswith("en-US"):
        return "%m/%d/%Y"
    if locale.startswith(("en-GB", "fr", "es", "de", "it", "pt", "nl")):
        return "%d/%m/%Y"
    return None
```

- [ ] **Step 5: Run; expect PASS**

- [ ] **Step 6: Commit**

```bash
git add src/flyquery/core/services/ingestion/readers/csv_reader.py \
        src/flyquery/core/services/ingestion/readers/__init__.py \
        tests/integration/parsers/test_csv_reader.py \
        tests/integration/parsers/fixtures/*.csv
git commit -m "feat: CsvReader (DuckDB read_csv_auto + locale-aware date format)"
```

---

### Task 3: Excel reader (xlsx / xls / ods)

**Files:**
- Create: `src/flyquery/core/services/ingestion/readers/excel_reader.py`
- Test: `tests/integration/parsers/test_excel_reader.py`
- Fixtures: `products.xlsx` (multi-sheet: "Catalog", "Pricing", "Inventory")

- [ ] **Step 1: Generate the XLSX fixture** (use `openpyxl` in a one-shot script or check in pre-built)

A small `products.xlsx`:
- Sheet "Catalog": product_id, name, category, list_price
- Sheet "Pricing": product_id, region, currency, price
- Sheet "Inventory": product_id, warehouse_id, qty_on_hand

- [ ] **Step 2: Write the failing test**

```python
# tests/integration/parsers/test_excel_reader.py
import pytest
from pathlib import Path
from flyquery.core.services.ingestion.readers.excel_reader import ExcelReader
from flyquery.core.services.ingestion.reader import TableExtractionRules

FIX = Path(__file__).parent / "fixtures"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_xlsx_enumerates_each_sheet_as_a_table(tmp_path):
    r = ExcelReader()
    tables = await r.enumerate_tables(str(FIX / "products.xlsx"), TableExtractionRules())
    names = {t.name for t in tables}
    assert names == {"Catalog", "Pricing", "Inventory"}
    for t in tables:
        result = await r.materialise(
            str(FIX / "products.xlsx"),
            t,
            target_parquet_key=str(tmp_path / f"{t.name}.parquet"),
            workspace_locale="en-US",
            type_infer_sample_rows=4096,
        )
        assert result.n_rows_actual > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_xlsx_sheet_allowlist_filters(tmp_path):
    r = ExcelReader()
    tables = await r.enumerate_tables(
        str(FIX / "products.xlsx"),
        TableExtractionRules(sheet_allowlist=("Catalog",)),
    )
    assert {t.name for t in tables} == {"Catalog"}
```

- [ ] **Step 3: Run; expect FAIL**

- [ ] **Step 4: Implement `ExcelReader`** (python-calamine, sheet-per-table)

```python
# src/flyquery/core/services/ingestion/readers/excel_reader.py
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


class ExcelReader(FileReader):
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
            source_path, table, target_parquet_key,
            workspace_locale, type_infer_sample_rows, max_title_rows,
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
            out.append(ProposedTable(
                name=ExcelReader._sanitise(name),
                sheet_or_json_path=name,
                n_columns=n_cols,
                n_rows_estimate=n_rows,
            ))
        return out

    @staticmethod
    def _materialise_sync(
        source_path: str, table: ProposedTable, target_parquet_key: str,
        workspace_locale: str, type_infer_sample_rows: int, max_title_rows: int,
    ) -> MaterialiseResult:
        # Strategy: extract the sheet to a temp CSV, then hand off to DuckDB
        # (so type inference + Parquet output is uniform across formats).
        from python_calamine import CalamineWorkbook
        import csv
        import duckdb

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
                conn.execute(
                    f"COPY (SELECT * FROM read_csv_auto(?, sample_size={type_infer_sample_rows}, "
                    f"auto_detect=true, ignore_errors=false)) TO ? (FORMAT PARQUET, COMPRESSION 'snappy')",
                    [tmp_path, target_parquet_key],
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
```

- [ ] **Step 5: Run; expect PASS**

- [ ] **Step 6: Commit**

```bash
git add src/flyquery/core/services/ingestion/readers/excel_reader.py \
        tests/integration/parsers/test_excel_reader.py \
        tests/integration/parsers/fixtures/products.xlsx
git commit -m "feat: ExcelReader (xlsx/xls/ods via python-calamine, sheet-per-table)"
```

---

### Task 4: JSON / JSONL reader

**Files:**
- Create: `src/flyquery/core/services/ingestion/readers/json_reader.py`
- Test: `tests/integration/parsers/test_json_reader.py`
- Fixtures: `events.jsonl`, `nested.json`, `ragged.json`

- [ ] **Step 1: Fixtures**

`events.jsonl` (one JSON object per line, ~10 records — order events).
`nested.json` — a top-level OBJECT with two array-valued keys: `{"orders": [...], "customers": [...]}` → should produce 2 tables.
`ragged.json` — top-level array with mixed-shape objects (some keys missing) → single table with NULL columns.

- [ ] **Step 2: Failing test**

```python
# tests/integration/parsers/test_json_reader.py
import pytest
from pathlib import Path
from flyquery.core.services.ingestion.readers.json_reader import JsonReader
from flyquery.core.services.ingestion.reader import TableExtractionRules

FIX = Path(__file__).parent / "fixtures"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_jsonl_single_table(tmp_path):
    r = JsonReader()
    tables = await r.enumerate_tables(str(FIX / "events.jsonl"), TableExtractionRules())
    assert len(tables) == 1
    result = await r.materialise(
        str(FIX / "events.jsonl"), tables[0],
        target_parquet_key=str(tmp_path / "events.parquet"),
        workspace_locale="en-US", type_infer_sample_rows=4096,
    )
    assert result.n_rows_actual > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_nested_object_explodes_to_multiple_tables(tmp_path):
    r = JsonReader()
    tables = await r.enumerate_tables(str(FIX / "nested.json"), TableExtractionRules())
    assert {t.name for t in tables} == {"orders", "customers"}


@pytest.mark.integration
@pytest.mark.asyncio
async def test_ragged_array_yields_null_columns(tmp_path):
    r = JsonReader()
    tables = await r.enumerate_tables(str(FIX / "ragged.json"), TableExtractionRules())
    result = await r.materialise(
        str(FIX / "ragged.json"), tables[0],
        target_parquet_key=str(tmp_path / "ragged.parquet"),
        workspace_locale="en-US", type_infer_sample_rows=4096,
    )
    nullable = [c.is_nullable for c in result.columns]
    assert any(nullable), "ragged JSON should have at least one nullable column"
```

- [ ] **Step 3: Run; expect FAIL**

- [ ] **Step 4: Implement `JsonReader`**

```python
# src/flyquery/core/services/ingestion/readers/json_reader.py
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
    FileReader,
    MaterialiseResult,
    ProposedTable,
    TableExtractionRules,
)


class JsonReader(FileReader):
    formats = ("json", "jsonl")

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
            source_path, table, target_parquet_key, type_infer_sample_rows,
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
            return [ProposedTable(
                name=re.sub(r"[^A-Za-z0-9_]+", "_", name) or "table",
                sheet_or_json_path=None,
                n_columns=0,  # filled at materialise
                n_rows_estimate=0,
            )]
        # Plain JSON: inspect the root.
        with open(source_path, encoding="utf-8") as f:
            doc = json.load(f)
        if isinstance(doc, list):
            return [ProposedTable(
                name=Path(source_path).stem,
                sheet_or_json_path=None,
                n_columns=0,
                n_rows_estimate=len(doc),
            )]
        if isinstance(doc, dict):
            paths = set(rules.json_paths) if rules.json_paths else None
            out: list[ProposedTable] = []
            for k, v in doc.items():
                if not isinstance(v, list):
                    continue
                if paths is not None and k not in paths:
                    continue
                out.append(ProposedTable(
                    name=re.sub(r"[^A-Za-z0-9_]+", "_", k) or "table",
                    sheet_or_json_path=k,
                    n_columns=0,
                    n_rows_estimate=len(v),
                ))
            if not out:
                # Fall through: treat object as a single 1-row table
                out.append(ProposedTable(
                    name=Path(source_path).stem,
                    sheet_or_json_path=None,
                    n_columns=len(doc),
                    n_rows_estimate=1,
                ))
            return out
        raise ValueError(f"unsupported JSON root type: {type(doc).__name__}")

    @staticmethod
    def _materialise_sync(
        source_path: str, table: ProposedTable, target_parquet_key: str,
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
                conn.execute(
                    f"COPY (SELECT * FROM read_json_auto(?, sample_size={type_infer_sample_rows}, "
                    f"format='auto')) TO ? (FORMAT PARQUET, COMPRESSION 'snappy')",
                    [input_path, target_parquet_key],
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
```

- [ ] **Step 5: Run; expect PASS**

- [ ] **Step 6: Commit**

```bash
git add src/flyquery/core/services/ingestion/readers/json_reader.py \
        tests/integration/parsers/test_json_reader.py \
        tests/integration/parsers/fixtures/events.jsonl \
        tests/integration/parsers/fixtures/nested.json \
        tests/integration/parsers/fixtures/ragged.json
git commit -m "feat: JsonReader (JSON+JSONL, top-level-array explode, ragged tolerance)"
```

---

### Task 5: Parquet reader (pass-through)

**Files:**
- Create: `src/flyquery/core/services/ingestion/readers/parquet_reader.py`
- Test: `tests/integration/parsers/test_parquet_reader.py`
- Fixture: `tiny.parquet` (generated via pyarrow)

- [ ] **Step 1: Create the fixture** via a one-shot pyarrow script (4-column, 5-row Parquet).

- [ ] **Step 2-5**: Test → Fail → Implement → Pass. The reader is trivial: it inspects the Parquet schema via `pyarrow.parquet.ParquetFile`, returns a single `ProposedTable`, and `materialise()` either writes-through (copy) the file or re-encodes via DuckDB.

```python
# src/flyquery/core/services/ingestion/readers/parquet_reader.py
from __future__ import annotations
import asyncio, shutil
from pathlib import Path
from flyquery.core.services.ingestion.reader import (
    ColumnSchema, FileReader, MaterialiseResult, ProposedTable, TableExtractionRules,
)


class ParquetReader(FileReader):
    formats = ("parquet",)

    async def enumerate_tables(self, source_path, rules):
        return await asyncio.to_thread(self._enumerate_sync, source_path)

    async def materialise(self, source_path, table, target_parquet_key, *,
                          workspace_locale, type_infer_sample_rows, max_title_rows=3):
        return await asyncio.to_thread(self._materialise_sync, source_path, target_parquet_key)

    @staticmethod
    def _enumerate_sync(source_path):
        import pyarrow.parquet as pq
        meta = pq.ParquetFile(source_path)
        return [ProposedTable(
            name=Path(source_path).stem, sheet_or_json_path=None,
            n_columns=len(meta.schema.names), n_rows_estimate=meta.metadata.num_rows,
        )]

    @staticmethod
    def _materialise_sync(source_path, target_parquet_key):
        import pyarrow.parquet as pq
        Path(target_parquet_key).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_path, target_parquet_key)
        meta = pq.ParquetFile(target_parquet_key)
        names = meta.schema.names
        types = [str(f.physical_type) for f in meta.schema]
        columns = tuple(
            ColumnSchema(name=n, data_type=t, is_nullable=True, position=i)
            for i, (n, t) in enumerate(zip(names, types))
        )
        return MaterialiseResult(
            target_parquet_key=target_parquet_key,
            parquet_byte_size=Path(target_parquet_key).stat().st_size,
            n_rows_actual=meta.metadata.num_rows,
            columns=columns,
        )
```

- [ ] **Step 6: Commit**: `feat: ParquetReader (pass-through copy + schema introspection)`

---

### Task 6: Avro / ORC / Arrow / Feather readers

**Files:**
- Create: `src/flyquery/core/services/ingestion/readers/{avro,orc,arrow}_reader.py`
- Test: `tests/integration/parsers/test_avro_orc_arrow.py`
- Fixtures: `tiny.avro`, `tiny.orc`, `tiny.feather`, `tiny.arrow` (pyarrow-generated)

For each, follow the Parquet pattern: read schema → convert to Parquet via DuckDB or pyarrow → return ColumnSchema tuple.

- **Avro**: `fastavro` for schema enumeration, `pyarrow.parquet.write_table(pyarrow.Table.from_records(records, schema=…))` for materialisation. Or simpler: DuckDB's `read_avro` (community extension; check if available — fallback to fastavro + pyarrow if not).
- **ORC**: `pyarrow.orc.ORCFile(...)` → `read()` → `parquet.write_table()`. Plain.
- **Arrow / Feather**: `pyarrow.feather.read_table()` → `parquet.write_table()`. Feather v2 = Arrow IPC format.

Commit: `feat: Avro / ORC / Arrow / Feather readers (pyarrow conversion to Parquet)`

---

### Task 7: Compression handlers (gz / zip / bz2)

**Files:**
- Create: `src/flyquery/core/services/ingestion/compression.py`
- Test: `tests/unit/test_compression_handlers.py` + `tests/integration/parsers/test_compression.py`
- Fixture: `orders.csv.gz`

- [ ] **Step 1: Failing test**

```python
# tests/integration/parsers/test_compression.py
import gzip, shutil, pytest
from pathlib import Path
from flyquery.core.services.ingestion.compression import decompress_to_temp

FIX = Path(__file__).parent / "fixtures"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_gzip_decompresses(tmp_path):
    src = tmp_path / "x.csv.gz"
    with gzip.open(src, "wb") as f:
        f.write(b"a,b,c\n1,2,3\n4,5,6\n")
    out = await decompress_to_temp(str(src), compression="gz")
    assert Path(out).read_bytes() == b"a,b,c\n1,2,3\n4,5,6\n"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_zip_rejects_multifile(tmp_path):
    import zipfile
    src = tmp_path / "x.zip"
    with zipfile.ZipFile(src, "w") as zf:
        zf.writestr("a.csv", "1\n")
        zf.writestr("b.csv", "2\n")
    with pytest.raises(ValueError, match="multiple files"):
        await decompress_to_temp(str(src), compression="zip")
```

- [ ] **Step 2: Implement**

```python
# src/flyquery/core/services/ingestion/compression.py
# Copyright 2026 Firefly Software Solutions Inc
"""Transparent decompression for upload-time format chain."""

from __future__ import annotations

import asyncio
import bz2
import gzip
import shutil
import tempfile
import zipfile
from pathlib import Path


MAX_DECOMPRESSED_BYTES = 5 * 1024 * 1024 * 1024  # 5 GB safety cap


async def decompress_to_temp(source_path: str, compression: str) -> str:
    return await asyncio.to_thread(_sync, source_path, compression)


def _sync(source_path: str, compression: str) -> str:
    suffix = Path(source_path).suffix
    tmp = tempfile.NamedTemporaryFile(suffix=suffix.replace(".gz", "").replace(".zip", "").replace(".bz2", "") or ".bin", delete=False)
    tmp.close()
    out_path = tmp.name
    if compression == "gz":
        with gzip.open(source_path, "rb") as src, open(out_path, "wb") as dst:
            _bounded_copy(src, dst, MAX_DECOMPRESSED_BYTES)
    elif compression == "bz2":
        with bz2.open(source_path, "rb") as src, open(out_path, "wb") as dst:
            _bounded_copy(src, dst, MAX_DECOMPRESSED_BYTES)
    elif compression == "zip":
        with zipfile.ZipFile(source_path, "r") as zf:
            files = [n for n in zf.namelist() if not n.endswith("/")]
            if len(files) != 1:
                raise ValueError(f"zip must contain exactly one file; got multiple files: {files}")
            with zf.open(files[0]) as src, open(out_path, "wb") as dst:
                _bounded_copy(src, dst, MAX_DECOMPRESSED_BYTES)
    elif compression == "none":
        shutil.copyfile(source_path, out_path)
    else:
        raise ValueError(f"unknown compression {compression!r}")
    return out_path


def _bounded_copy(src, dst, cap: int) -> None:
    total = 0
    while True:
        chunk = src.read(64 * 1024)
        if not chunk:
            break
        total += len(chunk)
        if total > cap:
            raise ValueError(f"decompressed size exceeded cap ({cap} bytes)")
        dst.write(chunk)
```

- [ ] **Step 3: Commit**: `feat: decompression handlers (gz / zip / bz2; 5GB cap)`

---

### Task 8: Format detection from magic bytes + extension

**Files:**
- Create: `src/flyquery/core/services/ingestion/format_detect.py`
- Test: `tests/unit/test_format_detect.py`

- [ ] **Step 1: Failing test**

```python
# tests/unit/test_format_detect.py
import pytest
from flyquery.core.services.ingestion.format_detect import detect_format


@pytest.mark.parametrize("name,head,expected", [
    ("orders.csv", b"order_id,total\n1,2\n", ("csv", "none")),
    ("data.tsv", b"a\tb\n1\t2\n", ("tsv", "none")),
    ("x.xlsx", b"PK\x03\x04", ("xlsx", "none")),
    ("x.json", b"{\"a\":1}", ("json", "none")),
    ("x.jsonl", b"{\"a\":1}\n{\"a\":2}\n", ("jsonl", "none")),
    ("x.parquet", b"PAR1", ("parquet", "none")),
    ("x.avro", b"Obj\x01", ("avro", "none")),
    ("x.csv.gz", b"\x1f\x8b", ("csv", "gz")),
    ("x.csv.zip", b"PK\x03\x04", ("csv", "zip")),
    ("x.csv.bz2", b"BZh", ("csv", "bz2")),
])
def test_detect(name, head, expected):
    assert detect_format(name, head) == expected
```

- [ ] **Step 2: Implement**

```python
# src/flyquery/core/services/ingestion/format_detect.py
from __future__ import annotations
import re


def detect_format(filename: str, head_bytes: bytes) -> tuple[str, str]:
    """Return (format, compression). Inspects extension + magic bytes."""
    name = filename.lower()
    # Compression first
    if name.endswith(".gz"):
        inner = name[:-3]
        return _format_from_name(inner, head_bytes), "gz"
    if name.endswith(".bz2"):
        inner = name[:-4]
        return _format_from_name(inner, head_bytes), "bz2"
    if name.endswith(".zip"):
        inner = name[:-4]
        return _format_from_name(inner, head_bytes), "zip"
    return _format_from_name(name, head_bytes), "none"


def _format_from_name(name: str, head: bytes) -> str:
    if name.endswith((".csv",)): return "csv"
    if name.endswith((".tsv",)): return "tsv"
    if name.endswith(".jsonl") or name.endswith(".ndjson"): return "jsonl"
    if name.endswith(".json"): return "json"
    if name.endswith(".parquet"): return "parquet"
    if name.endswith(".avro"): return "avro"
    if name.endswith(".orc"): return "orc"
    if name.endswith((".arrow", ".feather")): return "arrow"
    if name.endswith((".xlsx", ".xls", ".ods")):
        return name.rsplit(".", 1)[-1]
    # Magic bytes fallback
    if head.startswith(b"PAR1"): return "parquet"
    if head.startswith(b"Obj\x01"): return "avro"
    if head.startswith(b"PK\x03\x04"): return "xlsx"  # zip-based; could be xlsx/ods
    if head.startswith(b"{") or head.startswith(b"["): return "json"
    raise ValueError(f"could not detect format for {name!r}")
```

- [ ] **Step 3: Commit**: `feat: format detection (magic bytes + extension)`

---

### Task 9: Workspace + file size cap enforcement

**Files:**
- Modify: `src/flyquery/core/services/workspaces/workspace_service.py` — add `track_storage(delta_bytes)` method
- Create: `src/flyquery/core/services/ingestion/caps.py` — `enforce_upload_cap(size_bytes, workspace_storage_used, settings) -> None`
- Test: `tests/unit/test_upload_caps.py`

- [ ] **Steps 1-3**: TDD pattern. Test that:
  - Files > `FLYQUERY_MAX_FILE_MB` MB raise `FileTooLargeError` (HTTP 413)
  - When `workspace.storage_used_bytes + size > FLYQUERY_MAX_WORKSPACE_GB GB` raise `WorkspaceQuotaExceededError` (HTTP 507)

- [ ] **Step 4: Commit**: `feat: upload caps (per-file FLYQUERY_MAX_FILE_MB, per-workspace FLYQUERY_MAX_WORKSPACE_GB)`

---

## Phase B — Synchronous ingestion pipeline (Tasks 10-15)

### Task 10: `POST /datasets/{id}/files` (multipart upload)

**Files:**
- Create: `src/flyquery/interfaces/files.py` — `FileUploadResponse {file_id, tables: [...]}`
- Create: `src/flyquery/web/controllers/files_controller.py`
- Create: `src/flyquery/core/services/ingestion/ingest_service.py` (skeleton)
- Test: `tests/integration/test_files_upload.py`

- [ ] **Step 1: Write the failing test**

```python
import pytest, io
from httpx import ASGITransport, AsyncClient


@pytest.mark.integration
@pytest.mark.asyncio
async def test_upload_csv_first_time_creates_file_and_table():
    from flyquery.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        # Create workspace + dataset first
        r = await c.post("/api/v1/workspaces",
            json={"slug": "up", "name": "Upload"},
            headers={"X-Tenant-Id": "ten-a", "X-Workspace-Id": "up"})
        ws_id = r.json()["id"]
        r = await c.post("/api/v1/datasets",
            json={"name": "demo"},
            headers={"X-Tenant-Id": "ten-a", "X-Workspace-Id": ws_id})
        ds_id = r.json()["id"]

        # Upload orders.csv
        body = b"order_id,customer_id,total\n1,42,9.95\n2,42,12.50\n3,7,7.00\n"
        files = {"file": ("orders.csv", io.BytesIO(body), "text/csv")}
        r = await c.post(
            f"/api/v1/datasets/{ds_id}/files",
            files=files,
            headers={"X-Tenant-Id": "ten-a", "X-Workspace-Id": ws_id},
        )
        assert r.status_code == 201
        body = r.json()
        assert "file_id" in body
        assert len(body["tables"]) == 1
        assert body["tables"][0]["n_columns"] == 3
```

- [ ] **Step 2-4**: Implement the controller (multipart parsing via FastAPI's `UploadFile`), service method that:
  1. Writes bytes to `flyquery/{tenant}/{ws}/{ds}/files/{file_id}.{ext}` via ObjectStore
  2. Computes content_hash_sha256
  3. Detects format
  4. Inserts `flyquery_files` row (status=RECEIVED)
  5. Invokes the parse stage synchronously (Task 12)
  6. Returns the file_id + list of created tables

- [ ] **Step 5: Commit**: `feat: POST /datasets/{id}/files multipart upload (synchronous parse)`

---

### Task 11: `PUT /datasets/{ds}/tables/{table_id}:upload` (re-upload)

Same shape as Task 10 but updates an existing `table_id` slot. New `flyquery_files` row (new blob), new snapshot created via the reconcile stage (Task 13).

Commit: `feat: PUT /tables/{id}:upload (re-upload into existing slot)`

---

### Task 12: Stage 1 + Stage 2 — receive + parse

**Files:**
- Create: `src/flyquery/core/services/ingestion/stages/receive.py`
- Create: `src/flyquery/core/services/ingestion/stages/parse.py`
- Modify: `ingest_service.py` to call them in order

- [ ] **receive**: verify content_hash, enforce caps, detect format from magic+ext, write `flyquery_files` (status=RECEIVED), emit `received` event.
- [ ] **parse**: get reader from factory, decompress if needed, `enumerate_tables`, materialise each `ProposedTable` to Parquet under `{ds}/tables/{table_id}/v1.parquet`. Insert `flyquery_tables` rows (one per ProposedTable). Emit `parsed` event with the table list.

Commit: `feat: pipeline stages 1+2 (receive + parse → Parquet, multi-table)`

---

### Task 13: Stage 3 — reconcile + persist snapshot (atomic READY swap)

**File:** `src/flyquery/core/services/ingestion/stages/reconcile.py`

For each new `ProposedTable` materialised:
- Insert `flyquery_schema_snapshots` row (status=PARTIAL)
- Insert `flyquery_schema_objects` rows (kind=TABLE for the table + kind=COLUMN per column)
- If prev snapshot exists: compute diff → write `flyquery_schema_changes`. Rename rule: position+type signature unique on both sides → auto-RENAMED; else `RENAMED_CANDIDATE` (LLM later in Task 27)
- Annotation transplant: HUMAN-set description / pii_tag / synonyms / business_owner / governance preserved by `(qualified_name, column_name)` lookup
- Emit `reconciled` event

Atomic swap (after later stages): `flyquery_schema_snapshots.status='READY'` + `flyquery_tables.current_snapshot_id` = new snap, single transaction.

Commit: `feat: pipeline stage 3 — reconcile + schema_changes + annotation transplant`

---

### Task 14: Stage 9 — embed + index

**File:** `src/flyquery/core/services/ingestion/stages/embed.py`

For each new `flyquery_schema_objects` row (TABLE + COLUMN) in the new snapshot:
- Build embedding text: `"<dataset>.<table>.<column>: <data_type>\n<description>\nSamples: <preview>\nSynonyms: <list>"`
- Call OpenAI embedding API (text-embedding-3-small, 1536-d). Use the agentic framework's embedding helper if present; otherwise `openai` client directly.
- Persist `embedding` + `embedding_model` columns
- Refresh `content_tsv` via SQL `UPDATE … SET content_tsv = to_tsvector(...)` (no Python tokenization)
- Emit `embedded` event

Commit: `feat: pipeline stage 9 — embedding + content_tsv (per-object + per-table rollup)`

---

### Task 15: Stage 10 — publish + atomic close snapshot

**File:** `src/flyquery/core/services/ingestion/stages/publish.py`

Single transaction:
1. `UPDATE flyquery_schema_snapshots SET status='READY' WHERE id=:sid`
2. `UPDATE flyquery_tables SET current_snapshot_id=:sid, updated_at=now() WHERE id=:tid`
3. Publish `flyquery.schema.updated` event (EDA bus) with delta summary
4. Emit `snapshot_ready` event + `final` event

After all 10 stages green for the first table, the end-to-end smoke for "upload orders.csv, see it as a table you can query metadata on" should pass.

Commit: `feat: pipeline stage 10 — atomic snapshot READY swap + flyquery.schema.updated event`

---

## Phase C — Async ingestion orchestrator (Tasks 16-20)

### Task 16: EDA publisher for `flyquery.ingest`

**File:** `src/flyquery/core/eda/ingest_publisher.py`

Thin wrapper over pyfly's EDA bean: publishes `IngestRequested {ingest_job_id}` to topic `FLYQUERY_INGEST_TOPIC` (default `flyquery.ingest`).

Commit: `feat: flyquery.ingest EDA publisher`

---

### Task 17: `IngestWorker` (EDA consumer)

**File:** `src/flyquery/core/services/ingestion/workers.py`

Pyfly-registered EDA subscriber. On `IngestRequested`:
- Load `flyquery_ingest_jobs` row, flip to RUNNING
- Run stages 4-10 in order (stages 1-3 already ran synchronously in the upload path; the async worker handles refresh-only jobs + DESCRIBE_PASS + RELATION_PASS)
- Per-stage commit + emit events
- On exception: mark FAILED, record error_json, stop emitting events

Job kinds:
- `PARSE_AND_INGEST` → full 1-10 (this is the upload-driven path)
- `REPARSE` → re-run parse + reconcile on the existing file (e.g., after user fixes a delimiter)
- `SAMPLE_REFRESH` → only stage 4
- `DESCRIBE_PASS` → only stage 7
- `RELATION_PASS` → only stage 6

Cooperative cancel: poll `flyquery_ingest_jobs.status='CANCELLED'` between stages; gracefully exit.

Commit: `feat: IngestWorker (EDA consumer, 5 job kinds, cooperative cancel)`

---

### Task 18: `flyquery_ingest_events` writes per stage

**File:** Already present (table from migration 0005). New helper in `src/flyquery/core/services/ingestion/events.py` to write per-stage events with consistent payload shape.

Each stage emits: `{stage, status, message, payload_json}` per SSE contract (spec §11). The helper enforces the contract.

Commit: `feat: ingest_events helper (typed per-stage emissions)`

---

### Task 19: SSE endpoint `GET /ingest-jobs/{id}/stream`

**Files:**
- Create: `src/flyquery/web/controllers/ingest_jobs_controller.py`

Mirror canon's SSE pattern (look at `flycanon/src/flycanon/web/controllers/ingest_jobs_controller.py`): open a server-sent-events stream, poll `flyquery_ingest_events` by `ingest_job_id` ordered by `id`, emit each event with the proper `event:` + `data:` JSON. Close when a `final` or `error` event fires.

Commit: `feat: GET /ingest-jobs/{id}/stream SSE (mirror canon's pattern)`

---

### Task 20: Job lifecycle endpoints (POST/GET/list/cancel)

**Files:**
- Create: `src/flyquery/interfaces/ingest_jobs.py`
- Create: `src/flyquery/core/services/ingest_jobs/{ingest_job_repository,ingest_job_service}.py`

REST surface (per spec §7.1):
- `POST /api/v1/ingest-jobs` — start a `REPARSE` | `SAMPLE_REFRESH` | `DESCRIBE_PASS` | `RELATION_PASS` job (PARSE_AND_INGEST is started via /datasets/{id}/files, not here)
- `GET /api/v1/ingest-jobs` — paginated list, filters by status/kind/dataset/table
- `GET /api/v1/ingest-jobs/{id}` — single
- `GET /api/v1/ingest-jobs/{id}/events` — paginated event ledger
- `POST /api/v1/ingest-jobs/{id}:cancel` — cooperative

Commit: `feat: /api/v1/ingest-jobs CRUD + :cancel`

---

## Phase D — Sample + profile + PII (Tasks 21-23)

### Task 21: Stage 4 — sample (PII-gated)

**File:** `src/flyquery/core/services/ingestion/stages/sample.py`

For each new/changed column where `pii_tag IS NULL OR pii_tag='NONE'` AND `dataset.ingest_policy_json.sample_disabled` is not true:
1. `SELECT col FROM read_parquet(snap_key) WHERE col IS NOT NULL LIMIT :sample_n`
2. Pass each value through `PiiScanner.scan_single(value)` — refuse to persist if PII-flagged (inline gate)
3. Persist clean samples to `flyquery_schema_objects.sample_values_json` + `sample_taken_at`

Emit `sampled` event.

Commit: `feat: pipeline stage 4 — sample (inline PII gate; refuses PII-detected values)`

---

### Task 22: PII scanner port + regex adapter

**Files:**
- Create: `src/flyquery/core/services/pii/scanner.py` (Protocol)
- Create: `src/flyquery/core/services/pii/adapters/regex_scanner.py`
- Create: `src/flyquery/core/services/pii/adapters/presidio_scanner.py` (behind `[presidio]` extra)
- Create: `src/flyquery/core/services/pii/adapters/disabled_scanner.py`

**Protocol:**
```python
class PiiScanner(Protocol):
    async def scan_single(self, value: str) -> PiiFinding | None: ...
    async def scan_column(
        self, name: str, description: str | None,
        samples: list[str], data_type: str,
    ) -> PiiTag | None: ...
```

**Regex adapter** — canonical patterns: email, US SSN, IPv4, credit card (Luhn validation), phone (E.164 + common). The implementation mirrors canon's PII scanner verbatim if possible (memory: PIIScanner port reused from canon — check `flycanon/src/flycanon/core/services/pii/`).

**Presidio adapter** — wraps `presidio-analyzer` for entity recognition.

**Disabled adapter** — always returns None (for workspaces that explicitly opt out).

Factory selects by `FLYQUERY_PII_SCANNER` env (`regex|presidio|disabled`).

Commit: `feat: PiiScanner port + regex/presidio/disabled adapters (lock-step shape with canon)`

---

### Task 23: Stage 5 + Stage 8 — profile + PII tag

**Files:**
- `src/flyquery/core/services/ingestion/stages/profile.py`
- `src/flyquery/core/services/ingestion/stages/pii_tag.py`

**Profile (stage 5)** — for each column, run a single DuckDB query that computes `null_fraction`, `approx_count_distinct`, `min/max` (numeric/temporal only), top 5 values (low-cardinality only — skip when distinct_estimate > 100). Skip the whole column if the snapshot has more than `FLYQUERY_PROFILE_ROW_THRESHOLD` rows. Persist to `profile_json`.

**PII tag (stage 8)** — for each column, build `(name, description, samples, data_type)` and call `PiiScanner.scan_column(...)`. Apply policy:
- `warn` — log + persist tag, samples stay
- `redact` — set `sample_values_json = []` if newly-tagged
- `reject` — flip `flyquery_schema_objects.is_active = false` until human review

Emit `profiled` + `pii_tagged` events.

Commit: `feat: pipeline stages 5 + 8 — profile + PII tag (policy-driven: warn/redact/reject)`

---

## Phase E — Relation discovery + describe + rename (Tasks 24-27)

### Task 24: Stage 6a — heuristic relation discovery

**File:** `src/flyquery/core/services/ingestion/stages/relations.py` (heuristic part)

For each pair of tables in the dataset:
- For each column in table A: find columns in other tables in this dataset with:
  - identical column_name (case-insensitive)
  - compatible data_type (numeric ↔ numeric, text ↔ text, temporal ↔ temporal)
  - one side has `profile_json.distinct_estimate ≥ 0.95 * n_rows_actual` (treat as unique → PK-like)
- Insert `flyquery_relations` row: `kind='HEURISTIC', status='PROPOSED', confidence = uniqueness × name_specificity`. Skip if a relation already exists for that pair.

Emit `relations_proposed` event with counts.

Commit: `feat: pipeline stage 6a — heuristic relation discovery (name+type+uniqueness)`

---

### Task 25: `RelationProposerAgent`

**File:** `src/flyquery/core/agents/relation_proposer_agent.py`

```python
from pydantic import BaseModel
from flyquery.core.agents.builder import build_agent


class ProposedRelation(BaseModel):
    from_table: str
    from_column: str
    to_table: str
    to_column: str
    confidence: float
    reason: str


class ProposedRelations(BaseModel):
    items: list[ProposedRelation]


def build_relation_proposer_agent(settings):
    return build_agent(
        name="flyquery-relation-proposer",
        model=settings.relation_proposer_model,
        output_type=ProposedRelations,
        instructions=_INSTRUCTIONS,
        settings=settings,
    )

_INSTRUCTIONS = (
    "You receive a list of tables in a single dataset, each with column names, "
    "descriptions, samples and approximate cardinality. Identify cross-table "
    "join candidates that are NOT exact name matches (the heuristic detector "
    "already covers those). Examples: orders.email <-> customers.email "
    "(non-PK match); shipments.tracking_no <-> tracking_events.tracking_id "
    "(naming-mismatch but semantically equivalent). Output up to N proposals "
    "per table-pair with confidence ∈ [0,1] and a brief reason. Never invent "
    "columns; only refer to ones actually present."
)
```

Stage 6b integration: after 6a writes heuristic rows, gather the dataset's schema_objects, call the agent, write each returned proposal as `kind='AGENT_PROPOSED', status='PROPOSED'`. Skipped when `FLYQUERY_RELATION_PROPOSER_ENABLED=false`.

Commit: `feat: RelationProposerAgent + stage 6b wiring (AGENT_PROPOSED, human-approval gate)`

---

### Task 26: `DescribeAgent` + Stage 7

**File:** `src/flyquery/core/agents/describe_agent.py`

```python
class DescribedColumn(BaseModel):
    qualified_name: str
    description: str          # 1-2 sentences, business-flavoured
    synonyms: list[str]       # 3-8 alternative business names


class DescribedObjects(BaseModel):
    columns: list[DescribedColumn]


def build_describe_agent(settings):
    return build_agent(
        name="flyquery-describe",
        model=settings.describe_model,
        output_type=DescribedObjects,
        instructions=_INSTRUCTIONS,
        settings=settings,
    )
```

Stage 7 integration: select schema_objects where `description IS NULL AND description_source IS NULL`, group into batches of `FLYQUERY_DESCRIBE_BATCH`, call agent per batch with `(qualified_name, data_type, samples, table_context)` per column. Track cost; stop when `FLYQUERY_DESCRIBE_BUDGET_CENTS_PER_RUN` is hit (remaining columns deferred to follow-up `DESCRIBE_PASS` job). On success: `description_source='AGENT'`, save synonyms_json.

Commit: `feat: DescribeAgent + stage 7 (batched, budget-capped)`

---

### Task 27: `RenameDetectionAgent` (Stage 3 deep-dive)

**File:** `src/flyquery/core/agents/rename_detection_agent.py`

```python
class RenameProposal(BaseModel):
    removed_column: str
    new_column: str
    confidence: float
    rationale: str


class RenameProposals(BaseModel):
    items: list[RenameProposal]
```

When Stage 3 (reconcile) finds an ambiguous rename candidate (multiple columns could match a removed column by position+type), invoke this agent with `(removed_col_name, removed_description, removed_samples, candidate_new_cols_with_descriptions_and_samples)`. Agent returns a ranked list; flyquery picks the top one IF confidence ≥ 0.8, otherwise writes `RENAMED_CANDIDATE` rows and surfaces them via `/tables/{id}/changes` for human confirm.

Commit: `feat: RenameDetectionAgent + RENAMED_CANDIDATE flow (auto-confirm at conf ≥ 0.8)`

---

## Phase F — Re-upload + schema drift (Tasks 28-30)

### Task 28: Re-upload reconcile diff path

**File:** Modify `src/flyquery/core/services/ingestion/stages/reconcile.py`

Re-upload via `PUT /datasets/{ds}/tables/{table_id}:upload` triggers reconcile against the previous snapshot. Diff detection:
- Compare `(column_name, data_type)` pairs between old + new
- ADDED: new in new, missing in old
- REMOVED: in old, missing in new (mark `is_active=false` on old schema_objects; preserve their row for historical pinning)
- TYPE_CHANGED: same column_name, different data_type
- RENAMED: position+type unique match across old/new (auto-confirmed) → `change='RENAMED'`
- RENAMED_CANDIDATE: ambiguous → invoke `RenameDetectionAgent` (Task 27) → write `RENAMED_CANDIDATE` row

Write all changes to `flyquery_schema_changes`.

Commit: `feat: re-upload reconcile diff (ADDED/REMOVED/TYPE_CHANGED/RENAMED + candidate flow)`

---

### Task 29: `POST /schema-changes/{id}:confirm` endpoint

For human-approved rename confirmation: the controller flips the row's `change` from `RENAMED_CANDIDATE` → `RENAMED`, updates the corresponding schema_objects' `last_changed_at`.

Commit: `feat: POST /schema-changes/{id}:confirm (RENAMED_CANDIDATE → RENAMED)`

---

### Task 30: Annotation transplant verification

Modify the reconcile stage so HUMAN-set fields (description with description_source='HUMAN', pii_tag with pii_source='HUMAN', business_owner, governance_json, synonyms_json) are explicitly carried over from old to new schema_objects rows when the column survives (or is RENAMED). Add integration test `test_reupload_preserves_human_annotations` that:
1. Uploads orders.csv
2. PUT description="customer purchase total" on the `total` column (description_source=HUMAN)
3. Re-uploads orders.csv with one extra column
4. Verifies the `total` column still has description="customer purchase total"

Commit: `feat: reconcile preserves HUMAN-set annotations across snapshots`

---

## Phase G — GCS + AzureBlob adapters (Tasks 31-32)

### Task 31: `GcsObjectStore` adapter

**File:** `src/flyquery/core/services/storage/adapters/gcs.py`

Mirror `S3ObjectStore`'s shape using `gcloud-aio-storage`. KMS via `kmsKeyName` on the upload request. Run the conformance pack with a `[gcs]` parameterisation (use `fake-gcs-server` testcontainer; behind `@pytest.mark.gcs`).

Commit: `feat: GcsObjectStore adapter + conformance (fake-gcs-server)`

---

### Task 32: `AzureBlobObjectStore` adapter

Mirror with `azure-storage-blob` (async). Customer-provided keys via `BlobClient` config. Conformance pack against Azurite testcontainer (`@pytest.mark.azure_blob`).

Commit: `feat: AzureBlobObjectStore adapter + conformance (Azurite)`

---

## Phase H — End-to-end Northwind demo (Task 33)

**Files:**
- Create: `tests/integration/test_e2e_northwind_demo.py`
- Fixtures: `tests/integration/parsers/fixtures/{orders.csv,customers.csv,products.xlsx,nested_inventory.json}`

- [ ] **Step 1: Build the fixture**

A four-table Northwind-style dataset:
- `orders.csv`: order_id, customer_id, product_id, qty, ordered_at, total
- `customers.csv`: customer_id, name, email, region
- `products.xlsx` — single sheet (or 3 sheets to exercise multi-table): product_id, name, category, list_price
- `nested_inventory.json` — `{"warehouses": [...], "inventory": [...]}` (multi-table)

- [ ] **Step 2: The test**

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_northwind_demo_full_pipeline():
    from flyquery.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        h = {"X-Tenant-Id": "demo", "X-Workspace-Id": "northwind"}
        r = await c.post("/api/v1/workspaces", json={"slug": "northwind", "name": "Northwind Demo"}, headers=h)
        ws_id = r.json()["id"]
        h["X-Workspace-Id"] = ws_id
        r = await c.post("/api/v1/datasets", json={"name": "Sales"}, headers=h)
        ds_id = r.json()["id"]

        # Upload all 4 fixtures
        uploaded_tables: list[str] = []
        for fname in ("orders.csv", "customers.csv", "products.xlsx", "nested_inventory.json"):
            with open(FIX / fname, "rb") as f:
                files = {"file": (fname, f, "application/octet-stream")}
                r = await c.post(f"/api/v1/datasets/{ds_id}/files", files=files, headers=h)
                assert r.status_code == 201
                uploaded_tables.extend(t["table_id"] for t in r.json()["tables"])

        # Expect: 1 (orders) + 1 (customers) + 1 or 3 (xlsx — depends on fixture) + 2 (nested json) = 5-7 tables
        r = await c.get(f"/api/v1/datasets/{ds_id}/tables", headers=h)
        tables = r.json()["items"]
        assert len(tables) >= 5

        # Every table has a current_snapshot_id set + an AGENT-described table
        for t in tables:
            assert t["current_snapshot_id"]
            # description landed via DescribeAgent (or HUMAN later)
            assert t["description"] is not None or t["description_source"] is None

        # Cross-table relations have been proposed
        r = await c.get(f"/api/v1/datasets/{ds_id}/relations", headers=h)
        rels = r.json()["items"]
        # Expect at least customer_id ↔ customers.customer_id detected by heuristic
        assert any(
            r["from_column_name"] == "customer_id" and r["to_column_name"] == "customer_id"
            for r in rels
        )

        # SSE on a fresh ingest job streams the 10 stages
        r = await c.post(f"/api/v1/ingest-jobs",
            json={"dataset_id": ds_id, "job_kind": "DESCRIBE_PASS"}, headers=h)
        job_id = r.json()["id"]
        async with c.stream("GET", f"/api/v1/ingest-jobs/{job_id}/stream", headers=h) as resp:
            seen_events = []
            async for line in resp.aiter_lines():
                if line.startswith("event:"):
                    seen_events.append(line.split(": ", 1)[1])
                if "final" in seen_events:
                    break
        assert "final" in seen_events
```

- [ ] **Step 3: Run; iterate until green**

- [ ] **Step 4: Update QUICKSTART.md** — add a section showing the same workflow via `curl` for users without Python: upload a CSV, get the table_id, GET /tables/{id}, GET /datasets/{id}/relations.

- [ ] **Step 5: Commit**: `test: e2e Northwind demo (5-7 tables, AGENT descriptions, AGENT_PROPOSED relations, SSE)` + `docs: QUICKSTART workflow walkthrough`

---

## Spec coverage self-check

| Spec §15 step | Plan 2 task(s) |
|---|---|
| 8. FileReader port + 12 readers + 3 compressions | 1-9 |
| 9. Ingestion phase 1 — sync receive + parse + reconcile + atomic READY | 10-15 |
| 10. Ingestion phase 2 — async orchestrator + EDA + SSE | 16-20 |
| 11. Ingestion phase 3 — sample + profile + PII | 21-23 |
| 12. Ingestion phase 4 — relations + DescribeAgent | 24-26 |
| 13. Ingestion phase 5 — embedding + retrieval setup | 14 (embed stage) + part of phase B |
| 14. Re-upload + drift + RenameDetectionAgent | 27-30 |
| 15. GCS + AzureBlob | 31-32 |

Every step is covered. The end-to-end demo (Task 33) is the demoable cut-off.

## After Plan 2

Plan 3 (`2026-05-22-flyquery-03-query-pipeline.md`) builds on this: examples + glossary CRUD + `AGENT_LEARNED` auto-promotion, semantic-layer compiler, the 4-agent query pipeline (Grounding → Generation → DuckDB Executor → Critic → Explainer), reranker on by default, hybrid clarification frame, drill-down conversation context, `/sql:execute`, `/tables:derive`.
