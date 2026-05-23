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


_INSTRUCTIONS = (
    "You receive a batch of database columns in JSON format. Each column has: "
    "qualified_name (dataset.table.column), data_type, samples (sample values), "
    "and table_context (other columns in the same table). "
    "For each column, write: "
    "(1) a 1-2 sentence business-oriented description explaining what the column "
    "stores and how it might be used by a business analyst, and "
    "(2) 3-8 alternative business names (synonyms) that an analyst might use to "
    "refer to this column. "
    "Be concise and precise. Avoid restating the column name in the description. "
    "Output every column from the input — do not skip any."
)


def build_describe_agent(settings):
    """Build a DescribeAgent for Stage 7."""
    return build_agent(
        name="flyquery-describe",
        model=settings.describe_model,
        output_type=DescribedObjects,
        instructions=_INSTRUCTIONS,
        settings=settings,
    )
