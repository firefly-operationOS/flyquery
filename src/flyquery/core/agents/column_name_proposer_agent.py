# Copyright 2026 Firefly Software Solutions Inc
"""ColumnNameProposerAgent -- turn synthetic ``columnNN`` headers into meaningful names.

When an XLSX section is materialised, DuckDB's CSV auto-detection falls
back to ``column0`` / ``column1`` / ... whenever the first row of the
section doesn't look like a header (e.g. dashboard-style XLSX where the
real "header" is a band of merged title cells far above the data
block). The synthetic names work mechanically but defeat Text-to-SQL:
the model can't reason about ``column03`` the way it can reason about
``year_2024_total`` or ``line_item``.

This agent looks at:

* the section label (Activos, Pasivo/activo, Cuenta de Pérdidas y
  Ganancias, Información de contacto, ...),
* the current synthetic column names,
* a small sample of values from each column,

and proposes business-meaningful ``snake_case`` names. The proposer is
ONLY consulted when every column name matches the synthetic
``columnNN`` pattern -- if the file's first row already provided real
headers, we keep them verbatim.

Output is a flat list of ``proposed_names`` aligned 1:1 with the
``current_names`` input. The pipeline then rewrites the Parquet
``SELECT col0 AS proposed0, col1 AS proposed1, ...`` so all downstream
stages (sample / profile / embed / Grounding / Generation / Explainer)
see the friendly names.
"""

from __future__ import annotations

import re

from pydantic import BaseModel, Field

from flyquery.core.agents.builder import build_agent

_SYNTHETIC_NAME_RE = re.compile(r"^column\d+$", re.IGNORECASE)


class ProposedColumnNames(BaseModel):
    """Aligned 1:1 with the input column list."""

    proposed_names: list[str] = Field(
        description=(
            "List of proposed snake_case column names, in the same order as the "
            "input. Each name must be ASCII, lowercase, snake_case, <= 50 chars, "
            "starting with a letter, and unique within the list."
        )
    )


_INSTRUCTIONS = """
You are a column-name proposer. You receive a section label, a list of
synthetic column names (column00, column01, ...), and a small sample
of values from each column. Your job is to propose business-meaningful
``snake_case`` replacement names.

Rules
-----
* Output exactly ``len(current_names)`` proposed names, aligned 1:1.
* Each proposed name MUST be:
  - lowercase ASCII (no accents -- convert "año" to "anio", "país" to "pais")
  - snake_case (words joined by underscores)
  - <= 50 characters
  - starts with a letter
  - unique within the list
* Prefer concise, descriptive names (``line_item``, ``year_2024``,
  ``total_assets``, ``country_code``) over generic ones (``col_a``,
  ``value``).
* If the first column's sample values are clearly row labels (e.g.
  "Activos fijos", "Activos totales" -- they label what each row
  represents), name it ``line_item`` / ``label`` / ``metric`` /
  ``category`` depending on what the section is about.
* If a column's sample values are all dates of the form YYYY-MM-DD,
  name it ``period_<YYYY_MM_DD>`` or ``year_<YYYY>`` (collapsing the
  date to a year is acceptable when the day component is always 12-31
  / 06-30 -- "period_end_<YYYY>" is also fine).
* If a column's sample values are all the same currency code (USD,
  EUR), name it ``currency`` / ``currency_USD`` (sub-section context).
* If you genuinely can't tell from the samples + section label, fall
  back to ``<section>_col_<n>`` (e.g. ``activos_col_3``) -- never
  return literal ``column00``.
* Do NOT add prefixes like ``the_`` or ``a_``.
* Do NOT invent semantic content the samples don't support -- if a
  column has values like 1.0389 / 1.105 / ..., it's a ratio, not
  necessarily "eur_usd_rate" unless the section label or another
  column makes that explicit.
"""


def build_column_name_proposer_agent(settings):
    """Build a ColumnNameProposerAgent."""
    return build_agent(
        name="flyquery-column-name-proposer",
        model=settings.describe_model,  # cheap-fast model is fine here
        output_type=ProposedColumnNames,
        instructions=_INSTRUCTIONS,
        settings=settings,
    )


def needs_proposal(current_names: list[str]) -> bool:
    """Return True iff every name matches the synthetic ``columnNN`` pattern.

    Files that already arrive with real headers (a clean CSV, a sheet
    whose first row is real column labels) keep their names verbatim.
    """
    return bool(current_names) and all(_SYNTHETIC_NAME_RE.match(n) for n in current_names)


def render_proposal_prompt(
    *,
    section_label: str,
    current_names: list[str],
    sample_values: list[list[object]],
) -> str:
    """Build the user prompt for the proposer.

    Parameters
    ----------
    section_label
        Human-readable section name from XLSX section extraction
        (e.g. "Activos", "Cuenta de Pérdidas y Ganancias").
    current_names
        The synthetic ``columnNN`` names DuckDB assigned.
    sample_values
        Aligned with ``current_names`` -- a list of sample value lists,
        one list per column, each containing up to ~5 cell values.
    """
    out: list[str] = []
    out.append(f"# Section label\n{section_label}\n")
    out.append("# Columns to rename")
    out.append(
        "Each entry shows the current synthetic name and a sample of up to 5 values from that column.\n"
    )
    for i, name in enumerate(current_names):
        samples = sample_values[i] if i < len(sample_values) else []
        sample_strs = [str(s)[:80] for s in samples if s is not None and s != ""]
        out.append(f"- `{name}`")
        if sample_strs:
            for s in sample_strs[:5]:
                out.append(f"    - {s}")
        else:
            out.append("    - (no samples available)")
    out.append("")
    out.append(
        f"# Task\nReturn `proposed_names` with exactly {len(current_names)} "
        f"entries, aligned 1:1 with the columns above."
    )
    return "\n".join(out)
