# Copyright 2024-2026 Firefly Software Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pathlib import Path

import pytest

from flyquery.core.services.ingestion.reader import TableExtractionRules
from flyquery.core.services.ingestion.readers.parquet_reader import ParquetReader

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
