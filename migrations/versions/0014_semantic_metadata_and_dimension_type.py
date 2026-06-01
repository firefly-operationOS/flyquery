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

"""semantic metadata_json + dimension_type

Adds the ``metadata_json`` column to semantic metrics + dimensions (stores
the metric/dimension ``meta`` block) and a first-class ``dimension_type``
(categorical|time) column to dimensions, so dimensions no longer borrow the
metrics-only ``metric_type`` enum. ``metric_type`` is left in place on the
dimensions table (with its DRAFT/SIMPLE defaults) for backward compatibility.

Revision ID: 0014_semantic_meta_dimtype
Revises: 0013_job_callbacks
"""
from __future__ import annotations

from alembic import op

revision = "0014_semantic_meta_dimtype"
down_revision = "0013_job_callbacks"


def upgrade() -> None:
    op.execute(
        "ALTER TABLE flyquery_semantic_metrics "
        "ADD COLUMN IF NOT EXISTS metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb"
    )
    op.execute(
        "ALTER TABLE flyquery_semantic_dimensions "
        "ADD COLUMN IF NOT EXISTS metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb"
    )
    op.execute(
        "ALTER TABLE flyquery_semantic_dimensions "
        "ADD COLUMN IF NOT EXISTS dimension_type TEXT NOT NULL DEFAULT 'categorical'"
    )
    op.execute(
        "ALTER TABLE flyquery_semantic_dimensions "
        "DROP CONSTRAINT IF EXISTS ck_flyquery_semantic_dimensions_dimtype"
    )
    op.execute(
        "ALTER TABLE flyquery_semantic_dimensions "
        "ADD CONSTRAINT ck_flyquery_semantic_dimensions_dimtype "
        "CHECK (dimension_type IN ('categorical','time'))"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE flyquery_semantic_dimensions "
        "DROP CONSTRAINT IF EXISTS ck_flyquery_semantic_dimensions_dimtype"
    )
    op.execute(
        "ALTER TABLE flyquery_semantic_dimensions DROP COLUMN IF EXISTS dimension_type"
    )
    op.execute(
        "ALTER TABLE flyquery_semantic_dimensions DROP COLUMN IF EXISTS metadata_json"
    )
    op.execute(
        "ALTER TABLE flyquery_semantic_metrics DROP COLUMN IF EXISTS metadata_json"
    )
