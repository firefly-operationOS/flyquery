# Copyright 2026 Firefly Software Solutions Inc
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
        str(FIX / "events.jsonl"),
        tables[0],
        target_parquet_key=str(tmp_path / "events.parquet"),
        workspace_locale="en-US",
        type_infer_sample_rows=4096,
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
        str(FIX / "ragged.json"),
        tables[0],
        target_parquet_key=str(tmp_path / "ragged.parquet"),
        workspace_locale="en-US",
        type_infer_sample_rows=4096,
    )
    nullable = [c.is_nullable for c in result.columns]
    assert any(nullable), "ragged JSON should have at least one nullable column"
