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

"""Workspace stats REST controller (v1.0 -- new in 26.5.10).

``GET /api/v1/stats`` -- compact workspace summary (storage, counts).

Implementation lives in :class:`StatsService`. The endpoint is
operator traffic, not hot-path; we run a small set of COUNT(*)
queries on demand without caching.
"""

from __future__ import annotations

import uuid

from pyfly.container import rest_controller
from pyfly.web import get_mapping, request_mapping
from starlette.requests import Request

from flyquery.core.services.ops.stats_service import StatsService
from flyquery.interfaces.ops import WorkspaceStats
from flyquery.web.conventions import tenant_context_from_request


@rest_controller
@request_mapping("/api/v1/stats")
class StatsController:
    """REST adapter for the workspace summary."""

    def __init__(self, service: StatsService) -> None:
        self._service = service

    @get_mapping("")
    async def workspace_summary(
        self,
        http_request: Request,
    ) -> WorkspaceStats:
        """Return storage + counts for the caller's workspace."""
        ctx = tenant_context_from_request(http_request)
        ws = uuid.UUID(ctx.workspace_id) if isinstance(ctx.workspace_id, str) else ctx.workspace_id
        summary = await self._service.workspace_summary(
            tenant_id=ctx.tenant_id,
            workspace_id=ws,
        )
        return WorkspaceStats(**summary)


__all__ = ["StatsController"]
