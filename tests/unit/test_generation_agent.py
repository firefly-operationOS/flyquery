# Copyright 2026 Firefly Software Solutions Inc
"""Unit tests for GenerationAgent.

All tests mock the FireflyAgent so no real LLM calls are made in CI.
"""

from __future__ import annotations

import unittest.mock

import pytest

from flyquery.core.agents.generation_agent import GeneratedCandidate, GeneratedCandidates


def test_generated_candidates_model_validation() -> None:
    """GeneratedCandidates can be constructed with the expected fields."""
    result = GeneratedCandidates(
        candidates=[
            GeneratedCandidate(
                sql="SELECT region, SUM(total) FROM orders GROUP BY region",
                reasoning="Groups by region and sums the total column.",
                confidence=0.92,
            )
        ]
    )
    assert len(result.candidates) == 1
    assert "GROUP BY" in result.candidates[0].sql


def test_generated_candidate_confidence_bounds() -> None:
    """confidence must be in [0, 1]."""
    with pytest.raises(Exception):
        GeneratedCandidate(sql="SELECT 1", reasoning="test", confidence=1.5)

    with pytest.raises(Exception):
        GeneratedCandidate(sql="SELECT 1", reasoning="test", confidence=-0.1)


def test_generated_candidates_ordered_by_confidence() -> None:
    """Multiple candidates can be created and inspected."""
    result = GeneratedCandidates(
        candidates=[
            GeneratedCandidate(
                sql="SELECT region, SUM(total) FROM orders GROUP BY region", reasoning="best", confidence=0.95
            ),
            GeneratedCandidate(
                sql="SELECT region, COUNT(*) FROM orders GROUP BY region",
                reasoning="fallback",
                confidence=0.70,
            ),
        ]
    )
    assert result.candidates[0].confidence > result.candidates[1].confidence


@pytest.mark.asyncio
async def test_generation_agent_build_wires_correctly() -> None:
    """build_generation_agent calls build_agent with correct parameters."""

    class _FakeAgent:
        def __init__(self, *args, **kwargs):
            pass

    with unittest.mock.patch(
        "flyquery.core.agents.generation_agent.build_agent", return_value=_FakeAgent()
    ) as mock_build:
        from flyquery.config import FlyquerySettings
        from flyquery.core.agents.generation_agent import build_generation_agent

        settings = FlyquerySettings()
        build_generation_agent(settings)

        _, kwargs = mock_build.call_args
        assert kwargs["name"] == "flyquery-generation"
        assert kwargs["output_type"] is GeneratedCandidates
        assert kwargs["model"] == settings.generation_model


@pytest.mark.asyncio
async def test_generation_agent_returns_structured_output() -> None:
    """Mocked agent run returns GeneratedCandidates structure (wiring test)."""
    canned = GeneratedCandidates(
        candidates=[
            GeneratedCandidate(
                sql="SELECT region, SUM(total) AS revenue FROM orders GROUP BY region",
                reasoning="Direct aggregation from orders table.",
                confidence=0.90,
            ),
        ]
    )

    class _FakeAgent:
        async def run(self, *args, **kwargs):
            return canned

    with unittest.mock.patch("flyquery.core.agents.generation_agent.build_agent", return_value=_FakeAgent()):
        from flyquery.config import FlyquerySettings
        from flyquery.core.agents.generation_agent import build_generation_agent

        settings = FlyquerySettings()
        agent = build_generation_agent(settings)

    result = await agent.run({"grounded": {}, "question": "revenue by region"})
    assert isinstance(result, GeneratedCandidates)
    assert len(result.candidates) == 1
    assert result.candidates[0].confidence == 0.90
