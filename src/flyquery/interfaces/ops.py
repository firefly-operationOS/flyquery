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

"""Wire DTOs for ops endpoints -- audit + cost event read surfaces.

Both event streams are append-only ledgers populated by service-layer
writes (see :class:`AuditEventService.record` and
:class:`CostEventService.record`). The read endpoints support filtering
by date range, actor, event type / model, and resource id; pagination
follows the same :class:`Paginated` envelope as every other list
endpoint.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class AuditEventRead(BaseModel):
    """Append-only audit ledger row."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: str
    workspace_id: uuid.UUID
    actor: str
    event_type: str
    resource_kind: str
    resource_id: str | None = None
    correlation_id: str | None = None
    payload_json: dict | None = None
    created_at: datetime


class CostEventRead(BaseModel):
    """Append-only LLM cost ledger row.

    ``cost_cents`` is a Decimal because partial cents are common at the
    per-call granularity (the cost tracker in fireflyframework-agentic
    rounds at aggregation time, not per row).
    """

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: str
    workspace_id: uuid.UUID
    actor: str
    model: str | None = None
    operation: str
    input_tokens: int
    output_tokens: int
    cost_cents: Decimal
    ingest_job_id: uuid.UUID | None = None
    query_id: uuid.UUID | None = None
    correlation_id: str | None = None
    created_at: datetime


class BillingBreakdownItem(BaseModel):
    """One bucket of the billing rollup -- day, week, or month."""

    model_config = ConfigDict(from_attributes=True)

    date: datetime
    ingest_cost_cents: Decimal
    query_cost_cents: Decimal
    other_cost_cents: Decimal
    total_cost_cents: Decimal


class BillingRollup(BaseModel):
    """Response from GET /api/v1/billing.

    ``period`` is the bucket granularity that was applied; ``date_from``
    and ``date_to`` echo the request bounds so consumers can render
    "showing X to Y" headers without keeping local state.
    """

    period: str
    date_from: datetime | None = None
    date_to: datetime | None = None
    total_cost_cents: Decimal
    breakdown: list[BillingBreakdownItem]


class WorkspaceStats(BaseModel):
    """Response from GET /api/v1/stats -- compact workspace summary."""

    storage_used_bytes: int
    dataset_count: int
    table_count: int
    query_count_last_30d: int
    token_count_last_30d: int
    ingest_job_count_pending: int


__all__ = [
    "AuditEventRead",
    "BillingBreakdownItem",
    "BillingRollup",
    "CostEventRead",
    "WorkspaceStats",
]
