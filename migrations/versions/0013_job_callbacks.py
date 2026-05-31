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

"""ingest_jobs: callback URL columns + flyquery_callback_outbox.

Revision ID: 0013_job_callbacks
Revises: 0012_normalize_jsonb_shapes
Create Date: 2026-05-24

Adds opt-in webhook delivery for every async ingest job. The job
row carries the caller-supplied delivery target (URL + secret +
custom headers); on terminal status, the worker writes one row to
``flyquery_callback_outbox`` in the same transaction as the status
flip (transactional outbox pattern). A separate ``CallbackWorker``
drains the outbox with exponential backoff.

We don't fire the HTTP call from inside the IngestWorker because:

* Webhook latency is unbounded -- a slow receiver would block the
  worker semaphore and degrade ingest throughput.
* A crash between the status flip and a fire-and-forget HTTP call
  would silently drop the callback. The outbox guarantees at-least-once
  delivery: the row is durable, and the dedicated worker retries until
  ``DELIVERED`` or ``DEAD`` (5 failed attempts).

The ``next_attempt_at`` cursor + ``status`` index make the
``WHERE status='PENDING' AND next_attempt_at <= now()`` claim query
seek-only at scale.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP, UUID

# revision identifiers
revision = "0013_job_callbacks"
down_revision = "0012_normalize_jsonb_shapes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- ingest_jobs columns -------------------------------------------------
    op.add_column(
        "flyquery_ingest_jobs",
        sa.Column("callback_url", sa.Text, nullable=True),
    )
    op.add_column(
        "flyquery_ingest_jobs",
        sa.Column("callback_secret", sa.Text, nullable=True),
    )
    op.add_column(
        "flyquery_ingest_jobs",
        sa.Column(
            "callback_headers",
            JSONB,
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
    )

    # --- outbox table --------------------------------------------------------
    op.create_table(
        "flyquery_callback_outbox",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "ingest_job_id",
            UUID(as_uuid=True),
            sa.ForeignKey("flyquery_ingest_jobs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("tenant_id", sa.Text, nullable=False),
        sa.Column("workspace_id", UUID(as_uuid=True), nullable=False),
        sa.Column("callback_url", sa.Text, nullable=False),
        sa.Column("callback_secret", sa.Text, nullable=True),
        sa.Column(
            "callback_headers",
            JSONB,
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("event_type", sa.Text, nullable=False),
        sa.Column("payload_json", JSONB, nullable=False),
        sa.Column(
            "status",
            sa.Text,
            nullable=False,
            server_default=sa.text("'PENDING'"),
        ),
        sa.Column(
            "attempts",
            sa.Integer,
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "last_attempt_at",
            TIMESTAMP(timezone=True),
            nullable=True,
        ),
        sa.Column("last_status_code", sa.Integer, nullable=True),
        sa.Column("last_error", sa.Text, nullable=True),
        sa.Column(
            "next_attempt_at",
            TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "created_at",
            TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "finished_at",
            TIMESTAMP(timezone=True),
            nullable=True,
        ),
        sa.CheckConstraint(
            "status IN ('PENDING','DELIVERED','FAILED','DEAD')",
            name="ck_callback_outbox_status",
        ),
    )

    op.create_index(
        "ix_callback_outbox_due",
        "flyquery_callback_outbox",
        ["status", "next_attempt_at"],
    )
    op.create_index(
        "ix_callback_outbox_ingest_job_id",
        "flyquery_callback_outbox",
        ["ingest_job_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_callback_outbox_ingest_job_id", "flyquery_callback_outbox")
    op.drop_index("ix_callback_outbox_due", "flyquery_callback_outbox")
    op.drop_table("flyquery_callback_outbox")
    op.drop_column("flyquery_ingest_jobs", "callback_headers")
    op.drop_column("flyquery_ingest_jobs", "callback_secret")
    op.drop_column("flyquery_ingest_jobs", "callback_url")
