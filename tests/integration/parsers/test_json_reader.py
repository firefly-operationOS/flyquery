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
from flyquery.core.services.ingestion.readers.json_reader import JsonReader

FIX = Path(__file__).parent / "fixtures"

# ---------------------------------------------------------------------------
# JSON array-root
# ---------------------------------------------------------------------------


@pytest.mark.integration
@pytest.mark.asyncio
async def test_json_array_root_single_table(tmp_path):
    """A top-level JSON array maps to a single table with correct schema."""
    r = JsonReader()
    tables = await r.enumerate_tables(str(FIX / "array_root.json"), TableExtractionRules())
    assert len(tables) == 1
    result = await r.materialise(
        str(FIX / "array_root.json"),
        tables[0],
        target_parquet_key=str(tmp_path / "array_root.parquet"),
        workspace_locale="en-US",
        type_infer_sample_rows=4096,
    )
    assert result.n_rows_actual == 3
    col_names = {c.name for c in result.columns}
    assert {"user_id", "name", "score"} == col_names


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
