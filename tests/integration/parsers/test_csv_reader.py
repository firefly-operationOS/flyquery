# Copyright 2026 Firefly Software Solutions Inc
import pytest
from pathlib import Path
from flyquery.core.services.ingestion.readers.csv_reader import CsvReader
from flyquery.core.services.ingestion.reader import TableExtractionRules

FIX = Path(__file__).parent / "fixtures"

# ---------------------------------------------------------------------------
# Type-accuracy tests
# ---------------------------------------------------------------------------


@pytest.mark.integration
@pytest.mark.asyncio
async def test_csv_type_inference_accuracy(tmp_path):
    """orders.csv columns map to correct DuckDB types, not generic VARCHAR."""
    r = CsvReader()
    tables = await r.enumerate_tables(str(FIX / "orders.csv"), TableExtractionRules())
    result = await r.materialise(
        str(FIX / "orders.csv"),
        tables[0],
        target_parquet_key=str(tmp_path / "orders_types.parquet"),
        workspace_locale="en-US",
        type_infer_sample_rows=4096,
    )
    by_name = {c.name: c.data_type for c in result.columns}
    assert by_name["order_id"] == "BIGINT", f"expected BIGINT, got {by_name['order_id']}"
    assert by_name["customer_id"] == "BIGINT", f"expected BIGINT, got {by_name['customer_id']}"
    assert by_name["total"] == "DOUBLE", f"expected DOUBLE, got {by_name['total']}"
    assert by_name["ordered_at"] == "DATE", f"expected DATE, got {by_name['ordered_at']}"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_csv_locale_date_en_gb(tmp_path):
    """en-GB locale dateformat hint causes DD/MM/YYYY dates to land as DATE, not VARCHAR."""
    r = CsvReader()
    tables = await r.enumerate_tables(str(FIX / "locale_dates_gb.csv"), TableExtractionRules())
    result = await r.materialise(
        str(FIX / "locale_dates_gb.csv"),
        tables[0],
        target_parquet_key=str(tmp_path / "locale_gb.parquet"),
        workspace_locale="en-GB",
        type_infer_sample_rows=4096,
    )
    by_name = {c.name: c.data_type for c in result.columns}
    assert by_name["event_date"] == "DATE", (
        f"en-GB locale should produce DATE for DD/MM/YYYY column, got {by_name['event_date']}"
    )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_csv_mixed_type_column_inferred_as_varchar(tmp_path):
    """A column with mixed int/float/text values must be inferred as VARCHAR, not a numeric type."""
    r = CsvReader()
    tables = await r.enumerate_tables(str(FIX / "mixed_types.csv"), TableExtractionRules())
    result = await r.materialise(
        str(FIX / "mixed_types.csv"),
        tables[0],
        target_parquet_key=str(tmp_path / "mixed_types.parquet"),
        workspace_locale="en-US",
        type_infer_sample_rows=4096,
    )
    by_name = {c.name: c.data_type for c in result.columns}
    assert by_name["mixed_col"] == "VARCHAR", (
        f"mixed int/float/text column must resolve to VARCHAR, got {by_name['mixed_col']}"
    )


# ---------------------------------------------------------------------------
# Delimiter-detection tests
# ---------------------------------------------------------------------------


@pytest.mark.integration
@pytest.mark.asyncio
async def test_csv_pipe_delimiter(tmp_path):
    """DuckDB auto-detect correctly handles pipe-delimited files."""
    r = CsvReader()
    tables = await r.enumerate_tables(str(FIX / "pipe.csv"), TableExtractionRules())
    assert len(tables) == 1
    result = await r.materialise(
        str(FIX / "pipe.csv"),
        tables[0],
        target_parquet_key=str(tmp_path / "pipe.parquet"),
        workspace_locale="en-US",
        type_infer_sample_rows=4096,
    )
    assert result.n_rows_actual == 3
    col_names = {c.name for c in result.columns}
    assert {"sku", "name", "qty", "price"} == col_names


# ---------------------------------------------------------------------------
# Edge-case / graceful-error tests
# ---------------------------------------------------------------------------


@pytest.mark.integration
@pytest.mark.asyncio
async def test_csv_header_only_zero_rows(tmp_path):
    """A CSV with a header row but no data rows materialises with 0 rows and valid schema."""
    r = CsvReader()
    tables = await r.enumerate_tables(str(FIX / "header_only.csv"), TableExtractionRules())
    result = await r.materialise(
        str(FIX / "header_only.csv"),
        tables[0],
        target_parquet_key=str(tmp_path / "header_only.parquet"),
        workspace_locale="en-US",
        type_infer_sample_rows=4096,
    )
    assert result.n_rows_actual == 0
    assert len(result.columns) == 3


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
