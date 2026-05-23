# Copyright 2026 Firefly Software Solutions Inc
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
