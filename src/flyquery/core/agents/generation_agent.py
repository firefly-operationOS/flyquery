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


def build_generation_agent(settings):
    """Build a GenerationAgent for the query pipeline.

    Instructions loaded from ``resources/prompts/generation.yaml``.
    """
    from flyquery.core.agents.prompt_loader import load_prompt

    prompt = load_prompt("generation")
    return build_agent(
        name="flyquery-generation",
        model=settings.generation_model,
        output_type=GeneratedCandidates,
        instructions=prompt.instructions,
        settings=settings,
    )
