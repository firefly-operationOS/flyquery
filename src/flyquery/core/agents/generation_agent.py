# Copyright 2026 Firefly Software Solutions Inc
"""GenerationAgent — writes N candidate SQL queries from a GroundedContext.

Consumes the GroundedContext produced by the GroundingAgent and generates
N candidate SQL statements ordered by confidence, highest first.
Trust order: SEMANTIC_LAYER > UPLOADED_TABLE.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from flyquery.core.agents.builder import build_agent


class GeneratedCandidate(BaseModel):
    sql: str
    reasoning: str
    confidence: float = Field(ge=0, le=1)


class GeneratedCandidates(BaseModel):
    candidates: list[GeneratedCandidate]  # always N items, ordered by confidence descending


_INSTRUCTIONS = """
You are a SQL generation agent. You receive a GroundedContext
(tables, columns, joins, metrics) plus the NL question.

Generate exactly N candidate SQL queries against DuckDB, ordered by
confidence (highest first). Each candidate must:
- Use only the tables and columns from the grounded context
- Use the joins specified
- Be a SINGLE statement (no multi-statement; no DDL)
- Be a SELECT against ingested tables (no DML on UPLOADED tables)
- Prefer semantic-layer metrics over re-derived aggregations

Trust order: SEMANTIC_LAYER > UPLOADED_TABLE.

If the GroundedContext provides a starting_point_sql, your candidates
should be deltas (added WHERE clause, swapped column, etc.) — do not
rewrite from scratch unless necessary.

Output exactly the GeneratedCandidates structure.
"""


def build_generation_agent(settings):
    """Build a GenerationAgent for the query pipeline."""
    return build_agent(
        name="flyquery-generation",
        model=settings.generation_model,
        output_type=GeneratedCandidates,
        instructions=_INSTRUCTIONS,
        settings=settings,
    )
