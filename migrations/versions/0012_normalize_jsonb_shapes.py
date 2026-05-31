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

"""schema_objects: normalize governance_json + synonyms_json shapes.

Revision ID: 0012_normalize_jsonb_shapes
Revises: 0011_ingest_jobs_created_at
Create Date: 2026-05-24

Past bugs left two non-canonical shapes in ``flyquery_schema_objects``:

* ``governance_json`` was sometimes stored as ``[null, {...}]`` --
  the fingerprint of a ``NULL || dict`` jsonb-concat (an early version
  of the describe stage did not ``COALESCE`` the existing value before
  merging the semantic-type dict in).
* ``synonyms_json`` was occasionally written as a ``{"synonyms": [...]}``
  envelope by the same path.

The Pydantic DTOs were widened to ``dict | list | None`` as a band-aid,
which leaks shape ambiguity into every downstream consumer. The
canonical contract -- enforced by the SQLAlchemy entity declarations
in ``models/entities/{semantic,table}.py`` -- is:

* ``synonyms_json`` is a JSON array of strings.
* ``governance_json`` is a JSON object.

This migration heals every row that violates that contract, so the
DTOs can tighten back down to ``list[str]`` and ``dict[str, Any]``
without breaking ``GET /tables/{id}/objects`` for legacy data.

The producer-side fix (reconcile + describe stages) is in
``flyquery.core.services.storage.jsonb_normalize`` -- applied before
every insert / merge -- so no new rows can drift to a wrong shape.
"""

from __future__ import annotations

from alembic import op

# revision identifiers
revision = "0012_normalize_jsonb_shapes"
down_revision = "0011_ingest_jobs_created_at"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # governance_json: array -> rightmost dict element, or {} if none.
    op.execute(
        """
        UPDATE flyquery_schema_objects
        SET governance_json = COALESCE(
            (
                SELECT elt
                FROM jsonb_array_elements(governance_json)
                     WITH ORDINALITY AS t(elt, ord)
                WHERE jsonb_typeof(elt) = 'object'
                ORDER BY ord DESC
                LIMIT 1
            ),
            '{}'::jsonb
        )
        WHERE governance_json IS NOT NULL
          AND jsonb_typeof(governance_json) = 'array'
        """
    )

    # synonyms_json: object envelope -> unwrap to inner array, or [].
    op.execute(
        """
        UPDATE flyquery_schema_objects
        SET synonyms_json = COALESCE(
            CASE
                WHEN jsonb_typeof(synonyms_json -> 'synonyms') = 'array'
                THEN synonyms_json -> 'synonyms'
                ELSE NULL
            END,
            '[]'::jsonb
        )
        WHERE synonyms_json IS NOT NULL
          AND jsonb_typeof(synonyms_json) = 'object'
        """
    )


def downgrade() -> None:
    # No-op: we cannot reconstruct the pre-bug shape from the canonical one,
    # and there is no reason a downgrade should re-introduce the wrong shape.
    pass
