# Copyright 2026 Firefly Software Solutions Inc
"""DescribeAgent — generates business-friendly descriptions + synonyms for columns.

Used in Stage 7 to populate description + synonyms_json for columns where
description IS NULL. Runs in batches capped by FLYQUERY_DESCRIBE_BATCH.
Cost is tracked per run and stops when FLYQUERY_DESCRIBE_BUDGET_CENTS_PER_RUN
is hit.
"""

from __future__ import annotations

from pydantic import BaseModel

from flyquery.core.agents.builder import build_agent


class DescribedColumn(BaseModel):
    qualified_name: str
    description: str  # 1-2 sentences, business-flavoured
    synonyms: list[str]  # 3-8 alternative business names


class DescribedObjects(BaseModel):
    columns: list[DescribedColumn]


def build_describe_agent(settings):
    """Build a DescribeAgent for Stage 7.

    Instructions loaded from ``resources/prompts/describe.yaml``.
    """
    from flyquery.core.agents.prompt_loader import load_prompt

    prompt = load_prompt("describe")
    return build_agent(
        name="flyquery-describe",
        model=settings.describe_model,
        output_type=DescribedObjects,
        instructions=prompt.instructions,
        settings=settings,
    )
