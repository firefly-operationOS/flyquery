# Copyright 2026 Firefly Software Solutions Inc
"""End-to-end query pipeline demo (Plan 3 / Task 28).

Two variants:
  1. Mocked-agents (default) — patches the four agent factories to return
     deterministic canned responses; asserts the full wiring end-to-end.
  2. LLM mode (``@pytest.mark.llm``) — gated on ``ANTHROPIC_API_KEY`` +
     ``OPENAI_API_KEY``; builds real agents; skipped in CI by default.

Fixtures: orders.csv + customers.csv from tests/integration/parsers/fixtures/.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

# Parser-fixtures directory (subset used by Plan 2 parser tests).
FIX = Path(__file__).parent / "parsers" / "fixtures"


# ---------------------------------------------------------------------------
# Mocked-agents variant (default; runs without API keys)
# ---------------------------------------------------------------------------


@pytest.mark.integration
@pytest.mark.asyncio
async def test_e2e_query_pipeline_with_mocked_agents(started_app, monkeypatch) -> None:  # noqa: ANN001
    """Upload Northwind fixtures → mock agents to canned responses → POST /query → assert wiring."""
    from flyquery.core.agents.grounding_agent import (
        GroundedContext,
        GroundedColumn,
        GroundedTable,
    )
    from flyquery.core.agents.generation_agent import GeneratedCandidate, GeneratedCandidates
    from flyquery.core.agents.explainer_agent import ResultExplanation

    # ------------------------------------------------------------------
    # Canned agent outputs
    # ------------------------------------------------------------------

    canned_grounded = GroundedContext(
        path="SYNTHESIS",
        tables=[
            GroundedTable(table_qualified_name="orders", relevance=0.9),
            GroundedTable(table_qualified_name="customers", relevance=0.85),
        ],
        columns=[
            GroundedColumn(column_qualified_name="orders.total", relevance=0.9),
            GroundedColumn(column_qualified_name="customers.region", relevance=0.9),
        ],
        joins=[],
        metrics=[],
        examples_used=[],
        glossary_terms=[],
        confidence=0.82,
        missing_info=None,
    )

    canned_candidates = GeneratedCandidates(
        candidates=[
            GeneratedCandidate(
                sql=(
                    "SELECT customers.region, SUM(orders.total) AS total_revenue "
                    "FROM orders "
                    "JOIN customers ON orders.customer_id = customers.customer_id "
                    "GROUP BY customers.region"
                ),
                reasoning="join orders to customers, sum total, group by region",
                confidence=0.85,
            ),
        ]
    )

    canned_explanation = ResultExplanation(
        summary="Total revenue across regions calculated from the join of orders and customers.",
        chart_hint="bar",
    )

    # ------------------------------------------------------------------
    # Fake agent: run() returns the canned output directly (no wrapper)
    # ------------------------------------------------------------------

    class _FakeAgent:
        def __init__(self, output):
            self._output = output

        async def run(self, *args, **kwargs):
            return self._output

    _ctrl = "flyquery.web.controllers.query_controller"

    monkeypatch.setattr(
        f"{_ctrl}.build_grounding_agent",
        lambda settings: _FakeAgent(canned_grounded),
    )
    monkeypatch.setattr(
        f"{_ctrl}.build_generation_agent",
        lambda settings: _FakeAgent(canned_candidates),
    )
    monkeypatch.setattr(
        f"{_ctrl}.build_critic_agent",
        lambda settings: _FakeAgent(None),
    )
    monkeypatch.setattr(
        f"{_ctrl}.build_explainer_agent",
        lambda settings: _FakeAgent(canned_explanation),
    )

    # ------------------------------------------------------------------
    # Drive the HTTP surface
    # ------------------------------------------------------------------

    from flyquery.main import app
    from httpx import ASGITransport, AsyncClient

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://t",
        timeout=60.0,
    ) as c:
        h = {"X-Tenant-Id": "demo", "X-Workspace-Id": "nw"}

        # Create workspace
        r = await c.post(
            "/api/v1/workspaces",
            json={"slug": "nw-e2e-query", "name": "Northwind E2E Query"},
            headers=h,
        )
        assert r.status_code == 201, r.text
        ws_id = r.json()["id"]
        h["X-Workspace-Id"] = ws_id

        # Create dataset
        r = await c.post("/api/v1/datasets", json={"name": "Sales"}, headers=h)
        assert r.status_code == 201, r.text
        ds_id = r.json()["id"]

        # Upload orders.csv + customers.csv (minimum for JOIN to work)
        for fname in ("orders.csv", "customers.csv"):
            fpath = FIX / fname
            assert fpath.exists(), f"fixture missing: {fpath}"
            with open(fpath, "rb") as f:
                files = {"file": (fname, f, "application/octet-stream")}
                r = await c.post(
                    f"/api/v1/datasets/{ds_id}/files",
                    files=files,
                    headers=h,
                )
            assert r.status_code == 201, f"upload {fname} failed: {r.text}"

        # ------------------------------------------------------------------
        # POST /api/v1/query (sync)
        # ------------------------------------------------------------------
        r = await c.post(
            "/api/v1/query",
            json={"dataset_id": ds_id, "question": "what is total revenue by region?"},
            headers=h,
        )
        assert r.status_code == 200, r.text
        body = r.json()

        assert body["execution_status"] in ("OK", "REFINED_OK"), (
            f"unexpected execution_status: {body['execution_status']!r}"
        )
        assert "region" in body["sql"].lower(), f"SQL missing 'region': {body['sql']!r}"
        assert body["row_count"] is not None and body["row_count"] > 0, (
            f"expected row_count > 0, got {body['row_count']}"
        )
        assert body["chart_hint"] == "bar", f"expected chart_hint='bar', got {body['chart_hint']!r}"
        assert body["explanation"], "explanation must not be empty"
        assert body["preview"] and len(body["preview"]) > 0, "preview must have at least 1 row"

        # ------------------------------------------------------------------
        # POST /api/v1/query/stream (SSE)
        # ------------------------------------------------------------------
        events: list[str] = []
        async with c.stream(
            "POST",
            "/api/v1/query/stream",
            json={"dataset_id": ds_id, "question": "what is total revenue by region?"},
            headers=h,
        ) as resp:
            assert resp.status_code == 200, f"stream returned {resp.status_code}"
            async for line in resp.aiter_lines():
                if line.startswith("event:"):
                    event_name = line.split(": ", 1)[1].strip()
                    events.append(event_name)
                    if event_name == "final":
                        break  # stop once terminal event received

        assert events, "no SSE events received"
        assert events[0] == "schema_linked", (
            f"first event should be 'schema_linked', got {events[0]!r}"
        )
        assert "sql_generated" in events, f"'sql_generated' missing from events: {events}"
        assert "executed" in events, f"'executed' missing from events: {events}"
        assert "explained" in events, f"'explained' missing from events: {events}"
        assert events[-1] == "final", (
            f"last event should be 'final', got {events[-1]!r}"
        )


# ---------------------------------------------------------------------------
# LLM variant (requires ANTHROPIC_API_KEY + OPENAI_API_KEY; skipped in CI)
# ---------------------------------------------------------------------------


@pytest.mark.integration
@pytest.mark.llm
@pytest.mark.asyncio
async def test_e2e_query_pipeline_with_real_agents(started_app) -> None:  # noqa: ANN001
    """Same flow but with real LLM agents. Requires ANTHROPIC_API_KEY + OPENAI_API_KEY.

    The real LLM should produce SQL that mentions both 'region' and 'total'.
    """
    if not (os.environ.get("ANTHROPIC_API_KEY") and os.environ.get("OPENAI_API_KEY")):
        pytest.skip("requires ANTHROPIC_API_KEY and OPENAI_API_KEY")

    from flyquery.main import app
    from httpx import ASGITransport, AsyncClient

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://t",
        timeout=120.0,
    ) as c:
        h = {"X-Tenant-Id": "demo", "X-Workspace-Id": "nw"}

        # Create workspace + dataset
        r = await c.post(
            "/api/v1/workspaces",
            json={"slug": "nw-e2e-llm", "name": "Northwind E2E LLM"},
            headers=h,
        )
        assert r.status_code == 201, r.text
        ws_id = r.json()["id"]
        h["X-Workspace-Id"] = ws_id

        r = await c.post("/api/v1/datasets", json={"name": "Sales LLM"}, headers=h)
        assert r.status_code == 201, r.text
        ds_id = r.json()["id"]

        # Upload orders.csv + customers.csv
        for fname in ("orders.csv", "customers.csv"):
            fpath = FIX / fname
            assert fpath.exists(), f"fixture missing: {fpath}"
            with open(fpath, "rb") as f:
                files = {"file": (fname, f, "application/octet-stream")}
                r = await c.post(
                    f"/api/v1/datasets/{ds_id}/files",
                    files=files,
                    headers=h,
                )
            assert r.status_code == 201, f"upload {fname} failed: {r.text}"

        # ASK with real agents
        r = await c.post(
            "/api/v1/query",
            json={"dataset_id": ds_id, "question": "what is total revenue by region?"},
            headers=h,
        )
        assert r.status_code == 200, r.text
        body = r.json()

        assert body["execution_status"] in ("OK", "REFINED_OK"), (
            f"unexpected execution_status: {body['execution_status']!r}"
        )
        # The real LLM should produce SQL that references both 'region' and 'total'
        sql_lower = (body["sql"] or "").lower()
        assert "region" in sql_lower, f"SQL missing 'region': {body['sql']!r}"
        assert "total" in sql_lower, f"SQL missing 'total': {body['sql']!r}"
        assert body["row_count"] is not None and body["row_count"] > 0
        assert body["explanation"]
        assert body["preview"] and len(body["preview"]) > 0
