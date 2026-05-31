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

"""Cost event service: per-LLM-call billing ledger.

Each LLM-bearing operation (Grounding, Generation, Critic, Explainer,
Describe, Column-name proposer, Relation proposer, Rename detector, ...)
records one row. The read side powers ``GET /api/v1/cost-events`` and
a future ``GET /api/v1/billing`` rollup; the write side is invoked from
the agent execution path with the token + model metadata returned by
fireflyframework-agentic's cost tracker.

Like :class:`AuditEventService`, writes are best-effort -- a failed cost
insert never breaks the business operation. Reconciliation runs
out-of-band against provider invoices.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from pyfly.container import service as service_bean

from flyquery.core.services.ops.cost_event_repository import CostEventRepository

logger = logging.getLogger(__name__)


@service_bean
class CostEventService:
    """Writer + paginated reader for ``flyquery_cost_events``."""

    def __init__(self, repository: CostEventRepository) -> None:
        self._repo = repository

    async def record(
        self,
        *,
        tenant_id: str,
        workspace_id: uuid.UUID,
        actor: str,
        operation: str,
        model: str | None = None,
        input_tokens: int = 0,
        output_tokens: int = 0,
        cost_cents: Decimal | float | int = 0,
        ingest_job_id: uuid.UUID | None = None,
        query_id: uuid.UUID | None = None,
        correlation_id: str | None = None,
    ) -> None:
        """Best-effort cost-event record. Never raises -- failures log only."""
        try:
            await self._repo.insert(
                tenant_id=tenant_id,
                workspace_id=workspace_id,
                actor=actor,
                operation=operation,
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost_cents=cost_cents,
                ingest_job_id=ingest_job_id,
                query_id=query_id,
                correlation_id=correlation_id,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "cost insert failed operation=%s model=%s err=%s",
                operation,
                model,
                exc,
            )

    async def list_filtered(
        self,
        *,
        tenant_id: str,
        workspace_id: uuid.UUID,
        actor: str | None = None,
        model: str | None = None,
        operation: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[dict[str, Any]], int]:
        """Filtered + paginated read. Returns ``(rows, total_unpaginated)``."""
        limit = max(1, min(1000, int(limit)))
        offset = max(0, int(offset))
        return await self._repo.list_filtered(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            actor=actor,
            model=model,
            operation=operation,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            offset=offset,
        )
