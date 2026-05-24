# Copyright 2026 Firefly Software Solutions Inc
"""Unit tests for SchemaChangeService -- not_found / wrong_state / happy path."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

import pytest

from flyquery.core.services.schema_changes.schema_change_service import (
    SchemaChangeNotFound,
    SchemaChangeService,
    SchemaChangeWrongState,
)


class _FakeRepo:
    def __init__(self, *, row: dict[str, Any] | None, err: str | None) -> None:
        self._row = row
        self._err = err
        self.last_call: dict[str, Any] | None = None

    async def confirm_transaction(
        self,
        change_id: uuid.UUID,
        *,
        tenant_id: str,
        approved_by: str,
        approved_at: datetime,
    ) -> tuple[dict[str, Any] | None, str | None]:
        self.last_call = {
            "change_id": change_id,
            "tenant_id": tenant_id,
            "approved_by": approved_by,
            "approved_at": approved_at,
        }
        return self._row, self._err


@pytest.mark.asyncio
async def test_confirm_happy_path_returns_overlaid_row() -> None:
    cid = uuid.uuid4()
    repo = _FakeRepo(
        row={
            "id": cid,
            "table_id": uuid.uuid4(),
            "next_snapshot_id": uuid.uuid4(),
            "column_name": "amount",
            "change": "RENAMED_CANDIDATE",
            "created_at": datetime.now(),
        },
        err=None,
    )
    svc = SchemaChangeService(repo)  # type: ignore[arg-type]
    out = await svc.confirm(cid, tenant_id="acme", approved_by="user:alice")
    assert out.approved_by == "user:alice"
    assert out.row["change"] == "RENAMED_CANDIDATE"  # repo returns pre-update snapshot


@pytest.mark.asyncio
async def test_confirm_not_found_raises_typed_exception() -> None:
    svc = SchemaChangeService(_FakeRepo(row=None, err="not_found"))  # type: ignore[arg-type]
    with pytest.raises(SchemaChangeNotFound):
        await svc.confirm(uuid.uuid4(), tenant_id="acme", approved_by="user")


@pytest.mark.asyncio
async def test_confirm_wrong_state_raises_typed_exception() -> None:
    svc = SchemaChangeService(  # type: ignore[arg-type]
        _FakeRepo(
            row={"id": uuid.uuid4(), "change": "RENAMED"},
            err="wrong_state",
        )
    )
    with pytest.raises(SchemaChangeWrongState):
        await svc.confirm(uuid.uuid4(), tenant_id="acme", approved_by="user")
