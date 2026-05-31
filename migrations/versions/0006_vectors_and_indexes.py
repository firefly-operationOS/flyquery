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

"""pgvector + vector columns + tsvector + HNSW indexes

Revision ID: 0006_vectors_and_indexes
Revises: 0005_ops
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import TSVECTOR

revision = "0006_vectors_and_indexes"
down_revision = "0005_ops"


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.add_column(
        "flyquery_schema_objects",
        sa.Column("embedding", sa.ARRAY(sa.Float), nullable=True),
    )
    # Replace ARRAY with proper vector type via raw SQL (Alembic doesn't
    # know pgvector's `vector(N)`).
    op.execute("ALTER TABLE flyquery_schema_objects DROP COLUMN embedding")
    op.execute("ALTER TABLE flyquery_schema_objects ADD COLUMN embedding vector(1536)")
    op.add_column(
        "flyquery_schema_objects", sa.Column("content_tsv", TSVECTOR, nullable=True)
    )
    op.execute(
        "CREATE INDEX ix_objects_embedding ON flyquery_schema_objects "
        "USING hnsw (embedding vector_cosine_ops) "
        "WITH (m = 16, ef_construction = 64)"
    )
    op.execute("CREATE INDEX ix_objects_tsv ON flyquery_schema_objects USING gin(content_tsv)")

    op.execute("ALTER TABLE flyquery_examples ADD COLUMN embedding vector(1536)")
    op.execute(
        "CREATE INDEX ix_examples_embedding ON flyquery_examples "
        "USING hnsw (embedding vector_cosine_ops) "
        "WITH (m = 16, ef_construction = 64)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_examples_embedding")
    op.execute("ALTER TABLE flyquery_examples DROP COLUMN IF EXISTS embedding")
    op.execute("DROP INDEX IF EXISTS ix_objects_embedding")
    op.execute("DROP INDEX IF EXISTS ix_objects_tsv")
    op.execute("ALTER TABLE flyquery_schema_objects DROP COLUMN IF EXISTS content_tsv")
    op.execute("ALTER TABLE flyquery_schema_objects DROP COLUMN IF EXISTS embedding")
