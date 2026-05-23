# Copyright 2026 Firefly Software Solutions Inc
"""Stage 8 — PII tag.

For each active COLUMN in the snapshot:
  1. Build (name, description, samples, data_type) from DB.
  2. Call PiiScanner.scan_column().
  3. If a PiiTag is returned, update pii_tag + pii_source and apply policy:
       warn   — log + keep samples as-is
       redact — set sample_values_json = [] (wipe samples)
       reject — flip is_active = false (requires human review)

Emits pii_tagged event summary.
"""

from __future__ import annotations

import json
import logging
import uuid
from typing import Any

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from flyquery.core.services.pii.factory import build_pii_scanner

logger = logging.getLogger(__name__)


async def run_pii_tag(
    *,
    tenant_id: str,
    snapshot_id: uuid.UUID,
    session_factory: async_sessionmaker[AsyncSession],
    settings: Any,  # FlyquerySettings
) -> dict[str, Any]:
    """Execute Stage 8: PII tag."""
    scanner = build_pii_scanner(settings.pii_scanner)
    policy: str = settings.pii_policy_samples  # "warn" | "redact" | "reject"

    columns = await _load_columns(tenant_id, snapshot_id, session_factory)
    tagged = 0

    for col in columns:
        col_id: uuid.UUID = col["id"]
        col_name: str = col["qualified_name"].rsplit(".", 1)[-1]
        samples: list[str] = col["sample_values_json"] or []
        description: str | None = col["description"]
        data_type: str = col["data_type"] or ""

        tag = await scanner.scan_column(
            name=col_name,
            description=description,
            samples=samples,
            data_type=data_type,
        )

        if tag is None:
            continue

        # PII found — apply policy
        tagged += 1
        await _apply_tag_and_policy(
            col_id=col_id,
            tag_name=tag.tag,
            source=tag.source,
            policy=policy,
            tenant_id=tenant_id,
            session_factory=session_factory,
        )
        logger.info(
            "stage=pii_tag col=%s tag=%s source=%s policy=%s",
            col_name,
            tag.tag,
            tag.source,
            policy,
        )

    logger.info(
        "stage=pii_tag snapshot_id=%s columns_tagged=%d",
        snapshot_id,
        tagged,
    )
    return {"snapshot_id": str(snapshot_id), "columns_tagged": tagged}


# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------

async def _load_columns(
    tenant_id: str,
    snapshot_id: uuid.UUID,
    session_factory: async_sessionmaker[AsyncSession],
) -> list[dict[str, Any]]:
    async with session_factory() as s:
        result = await s.execute(
            sa.text(
                """
                SELECT id, qualified_name, data_type, description,
                       sample_values_json
                FROM flyquery_schema_objects
                WHERE snapshot_id = :sid
                  AND tenant_id = :tenant
                  AND kind = 'COLUMN'
                  AND is_active = true
                ORDER BY qualified_name
                """
            ),
            {"sid": snapshot_id, "tenant": tenant_id},
        )
        return [dict(r) for r in result.mappings().all()]


async def _apply_tag_and_policy(
    *,
    col_id: uuid.UUID,
    tag_name: str,
    source: str,
    policy: str,
    tenant_id: str,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    """Persist the PII tag and apply the configured policy action."""
    if policy == "warn":
        # Just tag; samples stay
        async with session_factory() as s, s.begin():
            await s.execute(
                sa.text(
                    """
                    UPDATE flyquery_schema_objects
                    SET pii_tag = :tag, pii_source = :source
                    WHERE id = :id AND tenant_id = :tenant
                    """
                ),
                {"id": col_id, "tenant": tenant_id, "tag": tag_name, "source": source},
            )

    elif policy == "redact":
        # Tag + wipe samples
        async with session_factory() as s, s.begin():
            await s.execute(
                sa.text(
                    """
                    UPDATE flyquery_schema_objects
                    SET pii_tag = :tag, pii_source = :source,
                        sample_values_json = '[]'::jsonb
                    WHERE id = :id AND tenant_id = :tenant
                    """
                ),
                {"id": col_id, "tenant": tenant_id, "tag": tag_name, "source": source},
            )

    elif policy == "reject":
        # Tag + deactivate column (human must review)
        async with session_factory() as s, s.begin():
            await s.execute(
                sa.text(
                    """
                    UPDATE flyquery_schema_objects
                    SET pii_tag = :tag, pii_source = :source,
                        is_active = false
                    WHERE id = :id AND tenant_id = :tenant
                    """
                ),
                {"id": col_id, "tenant": tenant_id, "tag": tag_name, "source": source},
            )

    else:
        # Unknown policy — default to warn behaviour (log + tag only)
        logger.warning("stage=pii_tag unknown policy=%r treating as warn", policy)
        async with session_factory() as s, s.begin():
            await s.execute(
                sa.text(
                    """
                    UPDATE flyquery_schema_objects
                    SET pii_tag = :tag, pii_source = :source
                    WHERE id = :id AND tenant_id = :tenant
                    """
                ),
                {"id": col_id, "tenant": tenant_id, "tag": tag_name, "source": source},
            )
