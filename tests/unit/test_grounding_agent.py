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

"""Unit tests for GroundingAgent.

All tests mock the FireflyAgent so no real LLM calls are made in CI.
Tests marked with ``@pytest.mark.llm`` require API keys and are skipped by default.
"""

from __future__ import annotations

import unittest.mock

import pytest

from flyquery.core.agents.grounding_agent import (
    GroundedColumn,
    GroundedContext,
    GroundedJoin,
    GroundedMetric,
    GroundedTable,
)


def test_grounded_context_model_validation() -> None:
    """GroundedContext can be constructed with the expected fields."""
    ctx = GroundedContext(
        path="SYNTHESIS",
        tables=[GroundedTable(table_qualified_name="orders", relevance=0.9)],
        columns=[GroundedColumn(column_qualified_name="orders.total", relevance=0.8)],
        confidence=0.85,
    )
    assert ctx.path == "SYNTHESIS"
    assert len(ctx.tables) == 1
    assert ctx.tables[0].table_qualified_name == "orders"
    assert ctx.confidence == 0.85
    assert ctx.missing_info is None


def test_grounded_context_semantic_layer_path() -> None:
    """SEMANTIC_LAYER path is valid and metrics list can be populated."""
    ctx = GroundedContext(
        path="SEMANTIC_LAYER",
        tables=[],
        columns=[],
        metrics=[GroundedMetric(metric_name="revenue_by_region", relevance=1.0)],
        confidence=0.95,
    )
    assert ctx.path == "SEMANTIC_LAYER"
    assert len(ctx.metrics) == 1


def test_grounded_context_low_confidence_has_missing_info() -> None:
    """When confidence is below threshold, missing_info can be set."""
    ctx = GroundedContext(
        path="SYNTHESIS",
        tables=[],
        columns=[],
        confidence=0.40,
        missing_info=["Which time period?", "Which region?"],
    )
    assert ctx.confidence == 0.40
    assert ctx.missing_info is not None
    assert len(ctx.missing_info) == 2


def test_grounded_join_default_relationship() -> None:
    """GroundedJoin defaults to inner join."""
    j = GroundedJoin(
        from_table="orders",
        from_column="customer_id",
        to_table="customers",
        to_column="id",
    )
    assert j.relationship == "inner"


@pytest.mark.asyncio
async def test_grounding_agent_build_wires_correctly() -> None:
    """build_grounding_agent calls build_agent with the correct name and output_type."""

    class _FakeAgent:
        def __init__(self, *args, **kwargs):
            pass

    # Patch build_agent where it is used inside grounding_agent module
    with unittest.mock.patch(
        "flyquery.core.agents.grounding_agent.build_agent", return_value=_FakeAgent()
    ) as mock_build:
        from flyquery.config import FlyquerySettings
        from flyquery.core.agents.grounding_agent import build_grounding_agent

        settings = FlyquerySettings()
        build_grounding_agent(settings)

        _, kwargs = mock_build.call_args
        assert kwargs["name"] == "flyquery-grounding"
        assert kwargs["output_type"] is GroundedContext
        assert kwargs["model"] == settings.grounding_model


@pytest.mark.asyncio
async def test_grounding_agent_returns_structured_output() -> None:
    """Mocked agent run returns GroundedContext (wiring test)."""
    canned = GroundedContext(
        path="SYNTHESIS",
        tables=[GroundedTable(table_qualified_name="orders", relevance=0.9)],
        columns=[GroundedColumn(column_qualified_name="orders.total", relevance=0.8)],
        confidence=0.85,
    )

    class _FakeAgent:
        async def run(self, *args, **kwargs):
            return canned

    with unittest.mock.patch("flyquery.core.agents.grounding_agent.build_agent", return_value=_FakeAgent()):
        from flyquery.config import FlyquerySettings
        from flyquery.core.agents.grounding_agent import build_grounding_agent

        settings = FlyquerySettings()
        agent = build_grounding_agent(settings)

    result = await agent.run({"question": "total revenue", "bundle": {}})
    assert isinstance(result, GroundedContext)
    assert result.path == "SYNTHESIS"
    assert result.confidence == 0.85
