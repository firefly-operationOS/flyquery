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

"""Unit tests for ResultUploader."""

from __future__ import annotations

import uuid
from datetime import UTC

import pytest

from flyquery.core.services.execution.duckdb_executor import ExecutionResult
from flyquery.core.services.query.result_uploader import ResultUploader


class _FakeObjectStore:
    def __init__(self):
        self.uploads: list[dict] = []

    async def put(self, key, body, content_type, kms_key_uri=None):
        self.uploads.append({"key": key, "size": len(body), "content_type": content_type})
        from datetime import datetime

        from flyquery.core.services.storage.object_store import ObjectMeta

        return ObjectMeta(
            key=key,
            size_bytes=len(body),
            content_type=content_type,
            etag=None,
            last_modified=datetime.now(UTC),
        )


class _FakeQueryRepo:
    def __init__(self):
        self.upserted: list[dict] = []

    async def upsert_result(self, **kwargs):
        self.upserted.append(kwargs)


class _FakeSettings:
    result_preview_max_bytes = 131072
    result_ttl_hours = 24


@pytest.mark.asyncio
async def test_upload_stores_parquet_and_preview():
    """upload() writes the parquet to object store and records preview in repo."""
    store = _FakeObjectStore()
    repo = _FakeQueryRepo()
    uploader = ResultUploader(store, repo, _FakeSettings())

    result = ExecutionResult(
        rows=[{"region": "North", "revenue": 100}, {"region": "South", "revenue": 200}],
        columns=["region", "revenue"],
        row_count=2,
        truncated=False,
    )
    query_id = uuid.uuid4()

    out = await uploader.upload(
        query_id=query_id,
        result=result,
        tenant_id="ten-a",
        workspace_id=uuid.uuid4(),
        dataset_id=uuid.uuid4(),
    )

    assert out["result_object_key"] is not None
    assert out["result_byte_size"] > 0
    assert len(store.uploads) == 1
    assert store.uploads[0]["content_type"] == "application/x-parquet"
    assert len(repo.upserted) == 1
    assert repo.upserted[0]["result_preview_json"] == result.rows


@pytest.mark.asyncio
async def test_upload_empty_result_skips_parquet():
    """Empty result does not upload a parquet but still upserts the result row."""
    store = _FakeObjectStore()
    repo = _FakeQueryRepo()
    uploader = ResultUploader(store, repo, _FakeSettings())

    result = ExecutionResult(rows=[], columns=[], row_count=0, truncated=False)
    query_id = uuid.uuid4()

    out = await uploader.upload(
        query_id=query_id,
        result=result,
        tenant_id="ten-a",
        workspace_id=uuid.uuid4(),
        dataset_id=uuid.uuid4(),
    )

    assert out["result_object_key"] is None
    assert out["result_byte_size"] == 0
    assert store.uploads == []
    assert len(repo.upserted) == 1


@pytest.mark.asyncio
async def test_upload_preview_capped_by_max_bytes():
    """Preview JSON is truncated when it exceeds result_preview_max_bytes."""

    class _TinySettings:
        result_preview_max_bytes = 50  # very small to force truncation
        result_ttl_hours = 24

    store = _FakeObjectStore()
    repo = _FakeQueryRepo()
    uploader = ResultUploader(store, repo, _TinySettings())

    result = ExecutionResult(
        rows=[{"col": "a" * 20} for _ in range(10)],
        columns=["col"],
        row_count=10,
        truncated=False,
    )

    await uploader.upload(
        query_id=uuid.uuid4(),
        result=result,
        tenant_id="ten-a",
        workspace_id=uuid.uuid4(),
        dataset_id=uuid.uuid4(),
    )

    preview = repo.upserted[0]["result_preview_json"]
    # Preview must fit within the byte cap
    import json

    assert len(json.dumps(preview).encode()) <= _TinySettings.result_preview_max_bytes
