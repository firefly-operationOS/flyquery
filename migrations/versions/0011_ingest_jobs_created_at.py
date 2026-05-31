"""ingest_jobs: add created_at for orphan-PENDING reaper.

Revision ID: 0011_ingest_jobs_created_at
Revises: 0010_allow_unknown_ast
Create Date: 2026-05-24

The ``RetentionWorker`` orphan-PENDING reaper needs a wall-clock cutoff
to decide which PENDING jobs to republish. ``flyquery_ingest_jobs``
carries a ``created_at`` populated by the service-layer insert on every
new job; the DB default ``now()`` covers fresh inserts and any rows
without a value are set to ``now()``.

A b-tree index on ``(status, created_at)`` keeps the reaper's
``WHERE status='PENDING' AND created_at < cutoff`` query fast even
at scale.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import TIMESTAMP

# revision identifiers
revision = "0011_ingest_jobs_created_at"
down_revision = "0010_allow_unknown_ast"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add the column with DEFAULT now() + NOT NULL. The DEFAULT
    # backfills every existing row in a single statement, so we
    # don't need a second UPDATE pass.
    op.add_column(
        "flyquery_ingest_jobs",
        sa.Column(
            "created_at",
            TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index(
        "ix_jobs_status_created_at",
        "flyquery_ingest_jobs",
        ["status", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_jobs_status_created_at", "flyquery_ingest_jobs")
    op.drop_column("flyquery_ingest_jobs", "created_at")
