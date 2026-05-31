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

"""ResultUploader — uploads query results to object storage.

Full flow:
1. Build a preview list (at most ``result_preview_max_bytes`` of JSON).
2. Serialise the full result as a Parquet file (snappy compressed) using pyarrow.
3. Upload the Parquet to ``flyquery/{tenant_id}/{workspace_id}/{dataset_id}/results/{query_id}.parquet``
   via the injected ``ObjectStore``.
4. Upsert the ``flyquery_query_results`` row via ``QueryRepository`` with the preview
   JSON, object key, and byte size.

If the result has no rows (empty result or FAILED execution), step 2-3 are skipped
and the row is still upserted with ``result_object_key=None``.
"""

from __future__ import annotations

import io
import json
import uuid

from flyquery.core.services.execution.duckdb_executor import ExecutionResult

_PREVIEW_ROW_LIMIT = 100  # max rows stored in the preview JSON field


class ResultUploader:
    """Uploads a query result to object storage and persists metadata.

    :param object_store: ObjectStore port (LocalFs, S3, GCS, …)
    :param query_repo: QueryRepository
    :param settings: FlyquerySettings — reads ``result_preview_max_bytes``
        and ``result_ttl_hours``
    """

    def __init__(self, object_store, query_repo, settings) -> None:
        self._store = object_store
        self._query_repo = query_repo
        self._settings = settings

    async def upload(
        self,
        *,
        query_id: uuid.UUID,
        result: ExecutionResult,
        tenant_id: str,
        workspace_id: uuid.UUID,
        dataset_id: uuid.UUID,
    ) -> dict:
        """Upload ``result`` and persist preview + object key.

        :param query_id: UUID of the parent query
        :param result: :class:`ExecutionResult` from DuckDBExecutor
        :param tenant_id: tenant identifier
        :param workspace_id: workspace UUID
        :param dataset_id: dataset UUID
        :return: dict with ``result_object_key`` and ``result_byte_size``
        """
        result_object_key: str | None = None
        result_byte_size: int = 0

        if result.rows:
            # Build Parquet in memory
            parquet_bytes = _rows_to_parquet(result.rows)
            result_byte_size = len(parquet_bytes)

            # Key layout: flyquery/{tenant}/{workspace}/{dataset}/results/{query_id}.parquet
            key = f"flyquery/{tenant_id}/{workspace_id}/{dataset_id}/results/{query_id}.parquet"
            await self._store.put(key, parquet_bytes, content_type="application/x-parquet")
            result_object_key = key

        # Build preview (capped at result_preview_max_bytes)
        preview_rows = result.rows[:_PREVIEW_ROW_LIMIT]
        preview_json_str = json.dumps(preview_rows)
        max_bytes: int = self._settings.result_preview_max_bytes
        if len(preview_json_str.encode()) > max_bytes:
            # Walk rows back until it fits
            while preview_rows and len(json.dumps(preview_rows).encode()) > max_bytes:
                preview_rows = preview_rows[:-1]

        await self._query_repo.upsert_result(
            query_id=query_id,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            result_preview_json=preview_rows,
            result_object_key=result_object_key,
            result_byte_size=result_byte_size if result_object_key else None,
            ttl_hours=self._settings.result_ttl_hours,
        )

        return {
            "result_object_key": result_object_key,
            "result_byte_size": result_byte_size,
        }


def _rows_to_parquet(rows: list[dict]) -> bytes:
    """Serialise a list of dicts to a snappy-compressed Parquet byte string."""
    import pyarrow as pa
    import pyarrow.parquet as pq

    table = pa.Table.from_pylist(rows)
    buf = io.BytesIO()
    pq.write_table(table, buf, compression="snappy")
    return buf.getvalue()
