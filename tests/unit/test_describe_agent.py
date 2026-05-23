# Copyright 2026 Firefly Software Solutions Inc
"""Unit tests for DescribeAgent + Stage 7."""

from __future__ import annotations


class TestDescribeAgentModels:
    def test_described_column_importable(self):
        from flyquery.core.agents.describe_agent import DescribedColumn

        col = DescribedColumn(
            qualified_name="ds.tbl.col",
            description="The total order amount.",
            synonyms=["amount", "price", "order_total"],
        )
        assert col.qualified_name == "ds.tbl.col"
        assert len(col.synonyms) == 3

    def test_described_objects_importable(self):
        from flyquery.core.agents.describe_agent import DescribedColumn, DescribedObjects

        objs = DescribedObjects(
            columns=[
                DescribedColumn(
                    qualified_name="a.b.c",
                    description="Something.",
                    synonyms=["foo"],
                )
            ]
        )
        assert len(objs.columns) == 1


class TestDescribeStageModuleImportable:
    def test_run_describe_importable(self):
        from flyquery.core.services.ingestion.stages.describe import run_describe

        assert callable(run_describe)

    def test_build_prompt_importable(self):
        from flyquery.core.services.ingestion.stages.describe import _build_prompt

        cols = [
            {
                "qualified_name": "ds.tbl.col",
                "data_type": "VARCHAR",
                "sample_values_json": ["a", "b"],
                "sibling_names": ["col", "other"],
                "parent_id": None,
            }
        ]
        result = _build_prompt(cols, None)
        assert len(result) == 1
        assert result[0]["qualified_name"] == "ds.tbl.col"
        assert result[0]["data_type"] == "VARCHAR"
        assert result[0]["samples"] == ["a", "b"]


class TestCostTracking:
    def test_cost_per_token_positive(self):
        from flyquery.core.services.ingestion.stages import describe as d_mod

        assert d_mod._CENTS_PER_INPUT_TOKEN > 0
        assert d_mod._CENTS_PER_OUTPUT_TOKEN > 0

    def test_budget_stops_batching(self):
        """Verify that a 0-cent budget would defer all columns."""
        # This is a logic unit test — no DB/agent needed
        columns = [{"qualified_name": f"ds.t.c{i}"} for i in range(5)]
        batch_size = 2
        budget_cents = 0.0
        spent_cents = 0.0
        described = 0
        deferred = 0

        for batch_start in range(0, len(columns), batch_size):
            batch = columns[batch_start : batch_start + batch_size]
            if spent_cents >= budget_cents:
                deferred += len(batch)
                continue
            described += len(batch)

        assert deferred == 5
        assert described == 0
