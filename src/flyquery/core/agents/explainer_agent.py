# Copyright 2026 Firefly Software Solutions Inc
"""ExplainerAgent — produces a NL summary + chart hint from a query result.

Receives the original question, the executed SQL, the row count, and up to
50 preview rows, and returns a concise 1-3 sentence summary and a chart hint.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from flyquery.core.agents.builder import build_agent


class ResultExplanation(BaseModel):
    summary: str  # 1-3 sentence NL answer
    chart_hint: Literal["line", "bar", "table", "pie", "none"]


_INSTRUCTIONS = """
You are a result explainer. You receive: the original question, the
executed SQL, the row count, and up to 50 rows of the result preview.

Output:
- summary: a 1-3 sentence direct answer to the question using the
  data (e.g. "Total revenue across all regions is $12,345. The
  Northeast region accounted for 42%.")
- chart_hint: pick the visualisation that best fits the result shape.
  - 1 row × 1 col → "none"
  - many rows × 2 cols (1 categorical + 1 numeric) → "bar" or "pie"
  - many rows × 2 cols (1 temporal + 1 numeric) → "line"
  - otherwise → "table"

Never invent numbers. Cite only what's in the result preview.
"""


def build_explainer_agent(settings):
    """Build an ExplainerAgent for the query pipeline."""
    return build_agent(
        name="flyquery-explainer",
        model=settings.explainer_model,
        output_type=ResultExplanation,
        instructions=_INSTRUCTIONS,
        settings=settings,
    )
