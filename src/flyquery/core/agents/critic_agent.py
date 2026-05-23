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


def build_critic_agent(settings):
    """Build a CriticAgent for the query pipeline.

    Instructions loaded from ``resources/prompts/critic.yaml``.
    """
    from flyquery.core.agents.prompt_loader import load_prompt

    prompt = load_prompt("critic")
    return build_agent(
        name="flyquery-critic",
        model=settings.critic_model,
        output_type=RefinedSql,
        instructions=prompt.instructions,
        settings=settings,
    )
