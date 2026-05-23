# Copyright 2026 Firefly Software Solutions Inc
"""GroundingAgent — picks the minimal table/column/join set to answer a NL question.

Consumes retrieved schema metadata (tables, columns, samples, descriptions,
relations, examples, semantic metrics, glossary) and emits a ``GroundedContext``
that the GenerationAgent uses to write SQL.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from flyquery.core.agents.builder import build_agent


class GroundedTable(BaseModel):
    table_qualified_name: str
    relevance: float = Field(ge=0, le=1)


class GroundedColumn(BaseModel):
    column_qualified_name: str
    relevance: float = Field(ge=0, le=1)


class GroundedJoin(BaseModel):
    from_table: str
    from_column: str
    to_table: str
    to_column: str
    relationship: Literal["inner", "left", "right", "outer"] = "inner"


class GroundedMetric(BaseModel):
    metric_name: str
    relevance: float = Field(ge=0, le=1)


class GroundedContext(BaseModel):
    path: Literal["SEMANTIC_LAYER", "SYNTHESIS", "HYBRID"]
    tables: list[GroundedTable]
    columns: list[GroundedColumn]
    joins: list[GroundedJoin] = Field(default_factory=list)
    metrics: list[GroundedMetric] = Field(default_factory=list)
    examples_used: list[str] = Field(default_factory=list)
    glossary_terms: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)
    missing_info: list[str] | None = None
    starting_point_sql: str | None = None  # from prior turn drill-down


def build_grounding_agent(settings):
    """Build a GroundingAgent for the query pipeline.

    Instructions are loaded from ``resources/prompts/grounding.yaml``
    so operators can tune them without rebuilding the Python package.
    """
    from flyquery.core.agents.prompt_loader import load_prompt

    prompt = load_prompt("grounding")
    return build_agent(
        name="flyquery-grounding",
        model=settings.grounding_model,
        output_type=GroundedContext,
        instructions=prompt.instructions,
        settings=settings,
    )
