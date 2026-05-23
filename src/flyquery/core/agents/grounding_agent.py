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
plus the workspace's schema catalogue (every table in the dataset,
each with its column-name list + a sample column description). You
may also receive top-ranked column matches, approved Q->SQL examples,
published semantic metrics, and a glossary.

Your job
--------
Pick the MINIMAL set of tables + columns + joins to answer the
question. Output a GroundedContext with:

- ``path``: ``SEMANTIC_LAYER`` if a published metric covers the
  question, ``SYNTHESIS`` otherwise (``HYBRID`` if both contribute).
- ``tables``: the actual tables you'll query, by their qualified_name
  (e.g. ``orbis_companies.IVI_MALAGA_SL__Activos``). MUST be non-empty
  for any answerable question.
- ``columns``: every column you'll project, filter, group, or order
  on, by qualified_name.
- ``joins``: any joins between tables.
- ``confidence`` in [0, 1].
- ``missing_info``: ambiguities the user should resolve, ONLY when
  confidence < 0.55.

Hard rules
----------
1. **Pick from the catalogue.** The "Complete dataset catalogue"
   section lists every table available. You MUST select tables only
   from that list. If you reach for ``balance_sheet``,
   ``income_statement``, ``cash_flow``, ``financials.*`` -- STOP.
   Those tables do not exist. Look at the catalogue and find the
   table whose column list answers the question. Table names may be
   in any language (Spanish ``Activos`` = English ``Assets``,
   ``Cuenta de Pérdidas y Ganancias`` = ``Profit & Loss``,
   ``Accionistas`` = ``Shareholders``). Translate as needed.
2. **Read the column fingerprints.** Each table entry carries a
   ``columns: ...`` line and ``sample column meaning: ...`` line.
   These tell you what the table is about even when the table name
   is opaque or non-English. Use them.
3. **Prefer the highest-signal match.** When two tables look
   relevant, pick the one whose column fingerprint most directly
   contains the metric the user asked for.
4. **Never invent.** Never output a qualified_name that doesn't
   appear in the catalogue or top-ranked columns. If nothing
   matches, set ``confidence`` low and explain in ``missing_info``.

Drill-down
----------
If the user is in a conversation and the prior turn provided a
``starting_point_sql``, treat it as the base SELECT and identify
only which deltas the new question requires.
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
