# Copyright 2026 Firefly Software Solutions Inc
import pytest
from pathlib import Path
from flyquery.core.services.ingestion.readers.excel_reader import ExcelReader
from flyquery.core.services.ingestion.reader import TableExtractionRules

FIX = Path(__file__).parent / "fixtures"

# ---------------------------------------------------------------------------
# Merged-cell title row stripping
# ---------------------------------------------------------------------------


@pytest.mark.integration
@pytest.mark.asyncio
async def test_xlsx_merged_title_row_stripped(tmp_path):
    """A sheet with a single merged-cell title row above the header is skipped.

    titled_sheet.xlsx has one sheet 'Sales' whose first row is a merged cell
    containing the report title 'Q1 2026 Sales Report'. The heuristic in
    ExcelReader._materialise_sync must strip that row so the header lands on
    sale_id / product / amount / sale_date, not on the title string.
    """
    r = ExcelReader()
    tables = await r.enumerate_tables(str(FIX / "titled_sheet.xlsx"), TableExtractionRules())
    assert len(tables) == 1
    result = await r.materialise(
        str(FIX / "titled_sheet.xlsx"),
        tables[0],
        target_parquet_key=str(tmp_path / "sales.parquet"),
        workspace_locale="en-US",
        type_infer_sample_rows=4096,
    )
    col_names = {c.name for c in result.columns}
    assert "sale_id" in col_names, (
        f"title-row stripping failed: expected 'sale_id' in columns, got {col_names}"
    )
    assert "product" in col_names
    assert result.n_rows_actual == 5


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
