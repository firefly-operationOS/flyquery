# Copyright 2026 Firefly Software Solutions Inc
"""CriticAgent — repairs a candidate SQL that failed DuckDB execution.

Consumes the failing SQL + DuckDB error message + GroundedContext and
produces a corrected SQL statement. Called up to MAX_REFINE_RETRIES times
within the query pipeline.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from flyquery.core.agents.builder import build_agent


class RefinedSql(BaseModel):
    sql: str
    reasoning: str
    confidence: float = Field(ge=0, le=1)


_INSTRUCTIONS = """
You are a SQL critic. You receive a candidate SQL that FAILED execution
(DuckDB error + error message) AND the GroundedContext.

Produce a corrected SQL. Common errors to fix:
- Misnamed columns/tables (the grounded context is authoritative)
- Wrong join conditions
- Missing GROUP BY
- Type-coercion issues (e.g. comparing TEXT to INTEGER)
- Aggregation in WHERE (move to HAVING)

Stay within the grounded context's table+column set. Do not introduce
new tables or columns.
"""


def build_critic_agent(settings):
    """Build a CriticAgent for the query pipeline."""
    return build_agent(
        name="flyquery-critic",
        model=settings.critic_model,
        output_type=RefinedSql,
        instructions=_INSTRUCTIONS,
        settings=settings,
    )
