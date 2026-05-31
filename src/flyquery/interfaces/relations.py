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

"""Wire DTOs for relations endpoints.

Relations represent column-level FK-style links between tables in a
dataset (e.g. ``orders.customer_id`` -> ``customers.id``). They're
seeded by the heuristic-based ``relations`` ingestion stage + the
``relation_proposer`` agent, then triaged by an operator via
``POST /relations/{id}:approve`` or ``:reject``.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class RelationRead(BaseModel):
    """One relation row, joined with its from/to table names for the API edge."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    dataset_id: uuid.UUID
    from_table_id: uuid.UUID
    from_table_name: str | None = None
    from_column_name: str
    to_table_id: uuid.UUID
    to_table_name: str | None = None
    to_column_name: str
    kind: str
    confidence: float | Decimal
    reason: str | None = None
    status: str
    approved_by: str | None = None
    created_at: datetime
    updated_at: datetime | None = None


class RelationApprovalRead(BaseModel):
    """Compact response from POST /relations/{id}:approve."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: str
    approved_by: str
    updated_at: datetime


class RelationRejectionRead(BaseModel):
    """Compact response from POST /relations/{id}:reject."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: str
    updated_at: datetime


__all__ = ["RelationRead", "RelationApprovalRead", "RelationRejectionRead"]
