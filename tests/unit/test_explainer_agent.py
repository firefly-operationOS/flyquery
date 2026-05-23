# Copyright 2026 Firefly Software Solutions Inc
"""Unit tests for ExplainerAgent.

All tests mock the FireflyAgent so no real LLM calls are made in CI.
"""

from __future__ import annotations

import unittest.mock

import pytest

from flyquery.core.agents.explainer_agent import ResultExplanation


def test_result_explanation_model_validation() -> None:
    """ResultExplanation can be constructed with all valid chart hints."""
    for hint in ("line", "bar", "table", "pie", "none"):
        r = ResultExplanation(summary="Revenue was $1M.", chart_hint=hint)
        assert r.chart_hint == hint


def test_result_explanation_invalid_chart_hint() -> None:
    """Invalid chart_hint values are rejected by the model."""
    with pytest.raises(Exception):
        ResultExplanation(summary="test", chart_hint="histogram")


def test_result_explanation_summary_can_be_long() -> None:
    """Summary supports multi-sentence text."""
    r = ResultExplanation(
        summary="Total revenue across all regions is $12,345. The Northeast region accounted for 42%.",
        chart_hint="bar",
    )
    assert "Northeast" in r.summary


@pytest.mark.asyncio
async def test_explainer_agent_build_wires_correctly() -> None:
    """build_explainer_agent calls build_agent with correct parameters."""

    class _FakeAgent:
        def __init__(self, *args, **kwargs):
            pass

    with unittest.mock.patch(
        "flyquery.core.agents.explainer_agent.build_agent", return_value=_FakeAgent()
    ) as mock_build:
        from flyquery.config import FlyquerySettings
        from flyquery.core.agents.explainer_agent import build_explainer_agent

        settings = FlyquerySettings()
        build_explainer_agent(settings)

        _, kwargs = mock_build.call_args
        assert kwargs["name"] == "flyquery-explainer"
        assert kwargs["output_type"] is ResultExplanation
        assert kwargs["model"] == settings.explainer_model


@pytest.mark.asyncio
async def test_explainer_agent_returns_structured_output() -> None:
    """Mocked explainer agent run returns ResultExplanation structure (wiring test)."""
    canned = ResultExplanation(
        summary="Total revenue across all regions is $12,345. The Northeast region accounted for 42%.",
        chart_hint="bar",
    )

    class _FakeAgent:
        async def run(self, *args, **kwargs):
            return canned

    with unittest.mock.patch("flyquery.core.agents.explainer_agent.build_agent", return_value=_FakeAgent()):
        from flyquery.config import FlyquerySettings
        from flyquery.core.agents.explainer_agent import build_explainer_agent

        settings = FlyquerySettings()
        agent = build_explainer_agent(settings)

    result = await agent.run(
        {
            "question": "total revenue by region",
            "sql": "SELECT region, SUM(total) FROM orders GROUP BY region",
            "row_count": 5,
            "preview": [{"region": "Northeast", "total": 5182}],
        }
    )
    assert isinstance(result, ResultExplanation)
    assert result.chart_hint == "bar"
    assert "Northeast" in result.summary
