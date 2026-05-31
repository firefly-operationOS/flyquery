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

FIX = Path(__file__).parent / "fixtures"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_avro_enumerates_and_materialises(tmp_path):
    from flyquery.core.services.ingestion.readers.avro_reader import AvroReader

    r = AvroReader()
    tables = await r.enumerate_tables(str(FIX / "tiny.avro"), TableExtractionRules())
    assert len(tables) == 1
    assert tables[0].n_columns == 3

    result = await r.materialise(
        str(FIX / "tiny.avro"),
        tables[0],
        target_parquet_key=str(tmp_path / "avro_out.parquet"),
        workspace_locale="en-US",
        type_infer_sample_rows=4096,
    )
    assert result.n_rows_actual == 3
    col_names = {c.name for c in result.columns}
    assert {"a", "b", "c"} == col_names


@pytest.mark.integration
@pytest.mark.asyncio
async def test_orc_enumerates_and_materialises(tmp_path):
    from flyquery.core.services.ingestion.readers.orc_reader import OrcReader

    r = OrcReader()
    tables = await r.enumerate_tables(str(FIX / "tiny.orc"), TableExtractionRules())
    assert len(tables) == 1
    assert tables[0].n_columns == 3

    result = await r.materialise(
        str(FIX / "tiny.orc"),
        tables[0],
        target_parquet_key=str(tmp_path / "orc_out.parquet"),
        workspace_locale="en-US",
        type_infer_sample_rows=4096,
    )
    assert result.n_rows_actual == 3
    col_names = {c.name for c in result.columns}
    assert {"a", "b", "c"} == col_names


@pytest.mark.integration
@pytest.mark.asyncio
async def test_feather_enumerates_and_materialises(tmp_path):
    from flyquery.core.services.ingestion.readers.arrow_reader import ArrowReader

    r = ArrowReader()
    tables = await r.enumerate_tables(str(FIX / "tiny.feather"), TableExtractionRules())
    assert len(tables) == 1
    assert tables[0].n_columns == 3

    result = await r.materialise(
        str(FIX / "tiny.feather"),
        tables[0],
        target_parquet_key=str(tmp_path / "feather_out.parquet"),
        workspace_locale="en-US",
        type_infer_sample_rows=4096,
    )
    assert result.n_rows_actual == 3
    col_names = {c.name for c in result.columns}
    assert {"a", "b", "c"} == col_names


@pytest.mark.integration
@pytest.mark.asyncio
async def test_arrow_ipc_enumerates_and_materialises(tmp_path):
    from flyquery.core.services.ingestion.readers.arrow_reader import ArrowReader

    r = ArrowReader()
    tables = await r.enumerate_tables(str(FIX / "tiny.arrow"), TableExtractionRules())
    assert len(tables) == 1

    result = await r.materialise(
        str(FIX / "tiny.arrow"),
        tables[0],
        target_parquet_key=str(tmp_path / "arrow_out.parquet"),
        workspace_locale="en-US",
        type_infer_sample_rows=4096,
    )
    assert result.n_rows_actual == 3
