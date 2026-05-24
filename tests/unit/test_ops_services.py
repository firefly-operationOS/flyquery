# Copyright 2026 Firefly Software Solutions Inc
"""Unit tests for AuditEventService + CostEventService.

Focuses on the best-effort write semantics: a repository failure must
never break the caller's business path. Read filtering is exercised in
the integration tests (it's pure SQL forwarding).
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

import pytest

from flyquery.core.services.ops.audit_event_service import AuditEventService
from flyquery.core.services.ops.cost_event_service import CostEventService


class _RecordingAuditRepo:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    async def insert(self, **fields: Any) -> uuid.UUID:
        self.rows.append(fields)
        return uuid.uuid4()

    async def list_filtered(self, **kwargs: Any) -> tuple[list, int]:
        return [], 0


class _FailingAuditRepo:
    async def insert(self, **fields: Any) -> uuid.UUID:
        raise RuntimeError("simulated DB failure")

    async def list_filtered(self, **kwargs: Any) -> tuple[list, int]:
        return [], 0


class _RecordingCostRepo:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    async def insert(self, **fields: Any) -> uuid.UUID:
        self.rows.append(fields)
        return uuid.uuid4()

    async def list_filtered(self, **kwargs: Any) -> tuple[list, int]:
        return [], 0


class _FailingCostRepo:
    async def insert(self, **fields: Any) -> uuid.UUID:
        raise RuntimeError("simulated DB failure")

    async def list_filtered(self, **kwargs: Any) -> tuple[list, int]:
        return [], 0


@pytest.mark.asyncio
async def test_audit_record_forwards_to_repo() -> None:
    repo = _RecordingAuditRepo()
    svc = AuditEventService(repo)  # type: ignore[arg-type]
    ws = uuid.uuid4()
    await svc.record(
        tenant_id="acme",
        workspace_id=ws,
        actor="user:alice",
        event_type="dataset.created",
        resource_kind="dataset",
        resource_id="ds-1",
        correlation_id="corr-1",
        payload={"name": "Q1 sales"},
    )
    assert len(repo.rows) == 1
    row = repo.rows[0]
    assert row["tenant_id"] == "acme"
    assert row["actor"] == "user:alice"
    assert row["event_type"] == "dataset.created"
    assert row["payload"] == {"name": "Q1 sales"}


@pytest.mark.asyncio
async def test_audit_record_swallows_repo_errors(caplog) -> None:
    """A failed insert must NEVER break the calling business operation."""
    svc = AuditEventService(_FailingAuditRepo())  # type: ignore[arg-type]
    with caplog.at_level(logging.WARNING):
        await svc.record(
            tenant_id="acme",
            workspace_id=uuid.uuid4(),
            actor="user",
            event_type="something",
            resource_kind="dataset",
        )
    assert any("audit insert failed" in m for m in caplog.messages)


@pytest.mark.asyncio
async def test_cost_record_forwards_to_repo_with_decimal_cents() -> None:
    repo = _RecordingCostRepo()
    svc = CostEventService(repo)  # type: ignore[arg-type]
    ws = uuid.uuid4()
    qid = uuid.uuid4()
    await svc.record(
        tenant_id="acme",
        workspace_id=ws,
        actor="user:alice",
        operation="grounding",
        model="anthropic:claude-sonnet-4-6",
        input_tokens=1234,
        output_tokens=567,
        cost_cents=Decimal("0.0823"),
        query_id=qid,
        correlation_id="corr-2",
    )
    assert len(repo.rows) == 1
    row = repo.rows[0]
    assert row["operation"] == "grounding"
    assert row["model"] == "anthropic:claude-sonnet-4-6"
    assert row["input_tokens"] == 1234
    assert row["output_tokens"] == 567
    assert row["cost_cents"] == Decimal("0.0823")
    assert row["query_id"] == qid


@pytest.mark.asyncio
async def test_cost_record_swallows_repo_errors(caplog) -> None:
    svc = CostEventService(_FailingCostRepo())  # type: ignore[arg-type]
    with caplog.at_level(logging.WARNING):
        await svc.record(
            tenant_id="acme",
            workspace_id=uuid.uuid4(),
            actor="agent",
            operation="generation",
            cost_cents=1,
        )
    assert any("cost insert failed" in m for m in caplog.messages)


@pytest.mark.asyncio
async def test_audit_list_filtered_clamps_limit() -> None:
    """``limit`` must be clamped to [1, 1000]."""
    repo = _RecordingAuditRepo()
    svc = AuditEventService(repo)  # type: ignore[arg-type]
    # Capture the clamped value via a small spy.
    captured: dict[str, Any] = {}

    async def spy(**kwargs: Any) -> tuple[list, int]:
        captured.update(kwargs)
        return [], 0

    repo.list_filtered = spy  # type: ignore[assignment]
    await svc.list_filtered(tenant_id="acme", workspace_id=uuid.uuid4(), limit=5000, offset=-10)
    assert captured["limit"] == 1000
    assert captured["offset"] == 0


def test_audit_read_dto_roundtrips_payload_dict() -> None:
    """Read DTO must round-trip a dict ``payload_json`` field cleanly."""
    from flyquery.interfaces.ops import AuditEventRead

    src = {
        "id": uuid.uuid4(),
        "tenant_id": "acme",
        "workspace_id": uuid.uuid4(),
        "actor": "user",
        "event_type": "dataset.created",
        "resource_kind": "dataset",
        "resource_id": None,
        "correlation_id": None,
        "payload_json": {"name": "x"},
        "created_at": datetime.now(),
    }
    dto = AuditEventRead.model_validate(src)
    assert dto.payload_json == {"name": "x"}
