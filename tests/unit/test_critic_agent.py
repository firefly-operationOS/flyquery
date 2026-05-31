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

"""Unit tests for CriticAgent.

All tests mock the FireflyAgent so no real LLM calls are made in CI.
"""

from __future__ import annotations

import unittest.mock

import pytest

from flyquery.core.agents.critic_agent import RefinedSql


def test_refined_sql_model_validation() -> None:
    """RefinedSql can be constructed with the expected fields."""
    result = RefinedSql(
        sql="SELECT region, SUM(total) FROM orders GROUP BY region",
        reasoning="Added missing GROUP BY clause.",
        confidence=0.88,
    )
    assert "GROUP BY" in result.sql
    assert result.confidence == 0.88


def test_refined_sql_confidence_bounds() -> None:
    """confidence must be in [0, 1]."""
    with pytest.raises(Exception):
        RefinedSql(sql="SELECT 1", reasoning="test", confidence=2.0)

    with pytest.raises(Exception):
        RefinedSql(sql="SELECT 1", reasoning="test", confidence=-0.5)


@pytest.mark.asyncio
async def test_critic_agent_build_wires_correctly() -> None:
    """build_critic_agent calls build_agent with correct parameters."""

    class _FakeAgent:
        def __init__(self, *args, **kwargs):
            pass

    with unittest.mock.patch(
        "flyquery.core.agents.critic_agent.build_agent", return_value=_FakeAgent()
    ) as mock_build:
        from flyquery.config import FlyquerySettings
        from flyquery.core.agents.critic_agent import build_critic_agent

        settings = FlyquerySettings()
        build_critic_agent(settings)

        _, kwargs = mock_build.call_args
        assert kwargs["name"] == "flyquery-critic"
        assert kwargs["output_type"] is RefinedSql
        assert kwargs["model"] == settings.critic_model


@pytest.mark.asyncio
async def test_critic_agent_returns_structured_output() -> None:
    """Mocked critic agent run returns RefinedSql structure (wiring test)."""
    canned = RefinedSql(
        sql="SELECT region, SUM(total) AS revenue FROM orders GROUP BY region",
        reasoning="Fixed missing GROUP BY — original failed with 'must appear in GROUP BY'.",
        confidence=0.85,
    )

    class _FakeAgent:
        async def run(self, *args, **kwargs):
            return canned

    with unittest.mock.patch("flyquery.core.agents.critic_agent.build_agent", return_value=_FakeAgent()):
        from flyquery.config import FlyquerySettings
        from flyquery.core.agents.critic_agent import build_critic_agent

        settings = FlyquerySettings()
        agent = build_critic_agent(settings)

    result = await agent.run(
        {
            "sql": "SELECT region, SUM(total) FROM orders",
            "error": "column 'region' must appear in GROUP BY",
            "grounded": {},
            "question": "revenue by region",
        }
    )
    assert isinstance(result, RefinedSql)
    assert result.confidence == 0.85
    assert "GROUP BY" in result.sql
