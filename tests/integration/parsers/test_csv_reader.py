# Copyright 2026 Firefly Software Solutions Inc
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
