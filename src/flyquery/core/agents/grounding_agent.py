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


_INSTRUCTIONS = """
You are a SQL grounding agent. You receive a natural-language question
plus retrieved schema metadata (tables, columns, samples, descriptions,
relations, examples, semantic metrics, glossary).

Your job: pick the MINIMAL set of tables + columns + joins to answer
the question. Output a GroundedContext with:
- path: SEMANTIC_LAYER if a published metric covers the question,
  SYNTHESIS otherwise (HYBRID if both contribute)
- tables, columns, joins (with reasoning)
- confidence ∈ [0, 1]
- missing_info: list of ambiguities the user should resolve, ONLY when
  confidence is below 0.55 — otherwise leave None

If the user is in a conversation and the prior turn provided a
starting_point_sql, treat it as the base SELECT and identify only
which deltas the new question requires.

Never invent tables or columns. Use only what's in the retrieved
metadata.
"""


def build_grounding_agent(settings):
    """Build a GroundingAgent for the query pipeline."""
    return build_agent(
        name="flyquery-grounding",
        model=settings.grounding_model,
        output_type=GroundedContext,
        instructions=_INSTRUCTIONS,
        settings=settings,
    )
