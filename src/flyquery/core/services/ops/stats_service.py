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

"""Workspace stats service: high-level usage counters.

Powers ``GET /api/v1/stats`` -- a small dashboard / billing-page
summary of how much storage + how many objects a workspace has.
Every count is a Postgres COUNT(*) over the canonical table; we
intentionally don't cache because the page is operator-traffic, not
hot-path.

Counts surfaced (all scoped to the calling tenant + workspace):
* ``storage_used_bytes``       -- from ``flyquery_workspaces``
* ``dataset_count``            -- non-ARCHIVED + non-PURGING datasets
* ``table_count``              -- ``is_active = true`` tables
* ``query_count_last_30d``     -- queries with ``created_at >= now() - 30d``
* ``token_count_last_30d``     -- sum of (input + output) tokens from cost_events
* ``ingest_job_count_pending`` -- jobs in PENDING / RUNNING
"""

from __future__ import annotations

import uuid

import sqlalchemy as sa
from pyfly.container import service as service_bean
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


@service_bean
class StatsService:
    """Aggregation reader over multiple workspace-scoped tables."""

    def __init__(self, session: async_sessionmaker[AsyncSession]) -> None:
        self._factory = session

    async def workspace_summary(
        self,
        *,
        tenant_id: str,
        workspace_id: uuid.UUID,
    ) -> dict[str, int]:
        """Return the canonical workspace summary as a flat int dict.

        One SELECT per metric is fine -- this endpoint is operator
        traffic, not hot-path, and bundling them via subselects would
        actually hurt explainability when debugging a divergent count.
        """
        async with self._factory() as s:
            storage_row = (
                await s.execute(
                    sa.text(
                        "SELECT COALESCE(storage_used_bytes, 0) AS n "
                        "FROM flyquery_workspaces "
                        "WHERE id = :ws AND tenant_id = :tenant"
                    ),
                    {"ws": workspace_id, "tenant": tenant_id},
                )
            ).scalar()
            dataset_count = (
                await s.execute(
                    sa.text(
                        "SELECT COUNT(*) AS n FROM flyquery_datasets "
                        "WHERE tenant_id = :tenant AND workspace_id = :ws "
                        "AND status NOT IN ('ARCHIVED', 'PURGING')"
                    ),
                    {"tenant": tenant_id, "ws": workspace_id},
                )
            ).scalar_one()
            table_count = (
                await s.execute(
                    sa.text(
                        "SELECT COUNT(*) AS n FROM flyquery_tables "
                        "WHERE tenant_id = :tenant AND workspace_id = :ws "
                        "AND is_active = true"
                    ),
                    {"tenant": tenant_id, "ws": workspace_id},
                )
            ).scalar_one()
            query_count_30d = (
                await s.execute(
                    sa.text(
                        "SELECT COUNT(*) AS n FROM flyquery_queries "
                        "WHERE tenant_id = :tenant AND workspace_id = :ws "
                        "AND created_at >= NOW() - INTERVAL '30 days'"
                    ),
                    {"tenant": tenant_id, "ws": workspace_id},
                )
            ).scalar_one()
            token_count_30d = (
                await s.execute(
                    sa.text(
                        "SELECT COALESCE(SUM(input_tokens + output_tokens), 0) AS n "
                        "FROM flyquery_cost_events "
                        "WHERE tenant_id = :tenant AND workspace_id = :ws "
                        "AND created_at >= NOW() - INTERVAL '30 days'"
                    ),
                    {"tenant": tenant_id, "ws": workspace_id},
                )
            ).scalar_one()
            ingest_pending = (
                await s.execute(
                    sa.text(
                        "SELECT COUNT(*) AS n FROM flyquery_ingest_jobs "
                        "WHERE tenant_id = :tenant AND workspace_id = :ws "
                        "AND status IN ('PENDING', 'RUNNING')"
                    ),
                    {"tenant": tenant_id, "ws": workspace_id},
                )
            ).scalar_one()

        return {
            "storage_used_bytes": int(storage_row or 0),
            "dataset_count": int(dataset_count or 0),
            "table_count": int(table_count or 0),
            "query_count_last_30d": int(query_count_30d or 0),
            "token_count_last_30d": int(token_count_30d or 0),
            "ingest_job_count_pending": int(ingest_pending or 0),
        }
