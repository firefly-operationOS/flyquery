# Copyright 2026 Firefly Software Solutions Inc
"""Unit tests for the v1 endpoint shapes -- queries, billing, stats.

Repos / object stores are stubbed; the focus is the
service-layer contract + DTO mapping. Integration tests against
real Postgres + MinIO live under tests/integration/.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any

import pytest

from flyquery.core.services.query.query_repository import QueryRepository
from flyquery.interfaces.query import QueryDetailRead, QueryHistoryItem

# --------------------------------------------------------------------------- #
# QueryHistoryItem / QueryDetailRead DTO mapping
# --------------------------------------------------------------------------- #


def test_query_history_item_accepts_row_dict() -> None:
    """The history DTO drops heavy JSONB columns -- model_validate must not choke."""
    src = {
        "id": uuid.uuid4(),
        "tenant_id": "acme",
        "workspace_id": uuid.uuid4(),
        "dataset_id": uuid.uuid4(),
        "question": "How many active users in Q1?",
        "executed_sql": "SELECT COUNT(*) FROM users WHERE active",
        "ast_classification": "SELECT",
        "execution_status": "OK",
        "row_count": 1,
        "elapsed_ms": 245,
        "semantic_path_taken": "sql",
        "retries": 0,
        "clarification_emitted": False,
        "created_at": datetime.now(UTC),
        "finalised_at": datetime.now(UTC),
    }
    dto = QueryHistoryItem(**src)
    assert dto.execution_status == "OK"
    assert dto.row_count == 1


def test_query_detail_read_preserves_candidates_list() -> None:
    """Detail DTO passes through the candidates JSONB list verbatim."""
    candidates = [
        {"sql": "SELECT 1", "reasoning": "first try", "confidence": 0.9},
        {"sql": "SELECT 2", "reasoning": "refine", "confidence": 0.95},
    ]
    src = {
        "id": uuid.uuid4(),
        "tenant_id": "acme",
        "workspace_id": uuid.uuid4(),
        "dataset_id": None,
        "question": "Q",
        "prior_turn_ids": [],
        "table_id_snapshot_pins_json": None,
        "semantic_path_taken": "sql",
        "candidates_json": candidates,
        "chosen_candidate_index": 1,
        "executed_sql": "SELECT 2",
        "ast_classification": "SELECT",
        "execution_engine": "duckdb",
        "execution_status": "OK",
        "retries": 0,
        "row_count": 1,
        "elapsed_ms": 100,
        "cost_cents": Decimal("0.0123"),
        "clarification_emitted": False,
        "clarification_json": None,
        "pii_findings_json": None,
        "error_json": None,
        "model_grounding": "anthropic:claude-sonnet-4-6",
        "model_generation": "anthropic:claude-sonnet-4-6",
        "model_critic": "anthropic:claude-sonnet-4-6",
        "model_explainer": "anthropic:claude-haiku-4-5",
        "created_at": datetime.now(UTC),
        "finalised_at": None,
    }
    dto = QueryDetailRead(**src)
    assert len(dto.candidates_json) == 2
    assert dto.candidates_json[1]["confidence"] == 0.95
    assert dto.chosen_candidate_index == 1


# --------------------------------------------------------------------------- #
# QueryRepository.list_queries clamps limit
# --------------------------------------------------------------------------- #


class _FakeSession:
    """Minimal async session stub that records the bound params."""

    def __init__(self, rows: list[dict[str, Any]] | None = None) -> None:
        self._rows = rows or []
        self.bound_params: list[dict[str, Any]] = []

    async def execute(self, stmt: Any, params: dict[str, Any]) -> Any:
        self.bound_params.append(params)

        class _Result:
            def __init__(self, rows: list[dict[str, Any]]) -> None:
                self._rows = rows

            def mappings(self) -> _Result:
                return self

            def all(self) -> list[dict[str, Any]]:
                return self._rows

            def scalar_one(self) -> int:
                return len(self._rows)

        # Inject _total column on the first row to mimic the window function.
        rows_with_total: list[dict[str, Any]] = []
        for r in self._rows:
            row = dict(r)
            row["_total"] = len(self._rows)
            rows_with_total.append(row)
        return _Result(rows_with_total)


class _FakeSessionFactory:
    def __init__(self, session: _FakeSession) -> None:
        self._session = session

    def __call__(self) -> _FakeSessionFactory:
        return self

    async def __aenter__(self) -> _FakeSession:
        return self._session

    async def __aexit__(self, *exc: Any) -> None:
        return None


@pytest.mark.asyncio
async def test_list_queries_clamps_limit_to_200_max() -> None:
    """Page size is clamped to [1, 200] -- huge limits become 200."""
    session = _FakeSession(rows=[])
    repo = QueryRepository(_FakeSessionFactory(session))  # type: ignore[arg-type]
    await repo.list_queries(
        tenant_id="acme",
        workspace_id=uuid.uuid4(),
        limit=10_000,
        offset=-50,
    )
    # The first call is the SELECT with the bound limit/offset.
    assert session.bound_params[0]["limit"] == 200
    assert session.bound_params[0]["offset"] == 0  # clamped from -50


@pytest.mark.asyncio
async def test_list_queries_clamps_limit_to_one_floor() -> None:
    session = _FakeSession(rows=[])
    repo = QueryRepository(_FakeSessionFactory(session))  # type: ignore[arg-type]
    await repo.list_queries(
        tenant_id="acme",
        workspace_id=uuid.uuid4(),
        limit=0,
        offset=0,
    )
    assert session.bound_params[0]["limit"] == 1


# --------------------------------------------------------------------------- #
# BillingService validates period
# --------------------------------------------------------------------------- #


@pytest.mark.asyncio
async def test_billing_service_rejects_unknown_period() -> None:
    from flyquery.core.services.ops.billing_service import BillingService

    svc = BillingService(_FakeSessionFactory(_FakeSession()))  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="unsupported period"):
        await svc.rollup(
            tenant_id="acme",
            workspace_id=uuid.uuid4(),
            period="year",  # type: ignore[arg-type]  -- intentional
        )


# --------------------------------------------------------------------------- #
# QueryResultRead presigned-url TTL guard
# --------------------------------------------------------------------------- #


def test_query_result_url_valid_returns_true_for_future_ttl() -> None:
    from flyquery.web.controllers.queries_controller import _is_url_still_valid

    assert _is_url_still_valid(datetime.now(UTC) + timedelta(hours=1)) is True


def test_query_result_url_valid_returns_false_for_past_ttl() -> None:
    from flyquery.web.controllers.queries_controller import _is_url_still_valid

    assert _is_url_still_valid(datetime.now(UTC) - timedelta(hours=1)) is False


def test_query_result_url_valid_returns_true_for_none_ttl() -> None:
    """``None`` TTL means 'no expiry tracked' -- treat as valid + let the
    presign call itself fail loudly if the object is gone."""
    from flyquery.web.controllers.queries_controller import _is_url_still_valid

    assert _is_url_still_valid(None) is True
