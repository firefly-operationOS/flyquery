# Copyright 2026 Firefly Software Solutions Inc
import pytest
from pathlib import Path
from flyquery.core.services.ingestion.readers.parquet_reader import ParquetReader
from flyquery.core.services.ingestion.reader import TableExtractionRules

FIX = Path(__file__).parent / "fixtures"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_parquet_enumerates_and_materialises(tmp_path):
    r = ParquetReader()
    tables = await r.enumerate_tables(str(FIX / "tiny.parquet"), TableExtractionRules())
    assert len(tables) == 1
    assert tables[0].n_columns == 4
    assert tables[0].n_rows_estimate == 5

    result = await r.materialise(
        str(FIX / "tiny.parquet"),
        tables[0],
        target_parquet_key=str(tmp_path / "out.parquet"),
        workspace_locale="en-US",
        type_infer_sample_rows=4096,
    )
    assert result.n_rows_actual == 5
    col_names = {c.name for c in result.columns}
    assert {"a", "b", "c", "d"} == col_names
