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

# Headers that DuckDB pulled from a data row instead of a real header row.
# These regexes intentionally treat "looks like a value" conservatively:
# false positives waste one LLM call per section; false negatives leave
# unusable names like ``5302354.32`` in the schema.
_NUMERIC_LITERAL_RE = re.compile(r"^\s*-?\d{1,3}(?:[,.\s]\d{3})*(?:[.,]\d+)?\s*$|^\s*-?\d+(?:[.,]\d+)?\s*$")
_LONG_TEXT_THRESHOLD = 60  # chars -- captures address rows, sentences
_MIN_COMMAS_FOR_ADDRESS = 2


def _looks_like_data_value(name: str) -> bool:
    """Return True when ``name`` looks like a value pulled from a data row.

    Catches the three concrete failure modes seen on real Orbis/BvD XLSX:

    * DuckDB synthetic ``columnNN`` -- no header row recognised.
    * A row of numeric financial values used as headers
      (``5,302,354.32`` -> not a meaningful column name).
    * A long free-text row used as a header
      (``Av. de los Pinos 23, 28042 Madrid, ES, Telf: ...``).

    Does NOT trigger on legitimate-but-numeric-looking headers like
    ``2020-12-31`` (period headers) -- those have hyphens, not commas
    or decimals, and stay under the long-text threshold.
    """
    if not name:
        return False
    n = name.strip()
    if not n:
        return False
    if _SYNTHETIC_NAME_RE.match(n):
        return True
    if _NUMERIC_LITERAL_RE.match(n):
        return True
    if len(n) >= _LONG_TEXT_THRESHOLD:
        return True
    return n.count(",") >= _MIN_COMMAS_FOR_ADDRESS


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
You are a column-name proposer. You receive a section label, the
current column names, and a small sample of values from each column.
The current names may be one of:

* DuckDB synthetic placeholders (``column00``, ``column01``, ...) when
  no header row was recognised at all.
* Values pulled from a data row that DuckDB mistakenly treated as the
  header (e.g. ``5302354.32`` -- a number; or
  ``Av. de los Pinos 23, 28042 Madrid, ES`` -- an address).
* A mix: some columns have meaningful names (``id``, ``country_code``)
  while others were taken from data values.

Your job is to propose business-meaningful ``snake_case`` replacement
names for ALL columns, in the same order.

Rules
-----
* Output exactly ``len(current_names)`` proposed names, aligned 1:1.
* Each proposed name MUST be:
  - lowercase ASCII (no accents -- convert "año" to "anio",
    "país" to "pais")
  - snake_case (words joined by underscores)
  - <= 50 characters
  - starts with a letter
  - unique within the list
* If a current name is ALREADY a meaningful business identifier
  (``id``, ``country_code``, ``period_end_2024``, ``email``), echo it
  back unchanged after lowercasing + snake_casing. Do not invent a
  new name when the existing one is already good.
* Prefer concise, descriptive names (``line_item``, ``year_2024``,
  ``total_assets``, ``country_code``) over generic ones (``col_a``,
  ``value``).
* If the first column's sample values are clearly row labels (e.g.
  "Activos fijos", "Activos totales"), name it ``line_item`` /
  ``label`` / ``metric`` / ``category`` per the section's subject.
* If a column's sample values are all dates of the form YYYY-MM-DD,
  name it ``period_end_<YYYY>`` or ``year_<YYYY>``.
* If a column's sample values are all the same currency code (USD,
  EUR), name it ``currency``.
* If the section label is an address/contact block and a column
  contains a phone number, an email, a street, etc., name it
  ``phone`` / ``email`` / ``street_address`` / ``city`` / ``country``
  per the actual content.
* If you genuinely can't tell from the samples + section label, fall
  back to ``<section>_col_<n>`` (e.g. ``activos_col_3``) -- never
  return literal ``column00`` or a numeric literal.
* Do NOT add prefixes like ``the_`` or ``a_``.
* Do NOT invent semantic content the samples don't support: a column
  of values like 1.0389 / 1.105 / ... is a ratio, not necessarily
  ``eur_usd_rate`` unless the section label or another column makes
  that explicit.
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
    """Return True iff the headers look like values pulled from a data row.

    Three triggers, in order of strength:

    1. Every name is synthetic ``columnNN`` -- DuckDB couldn't find any
       header row at all (the classic dashboard-XLSX case).
    2. Every name looks like a data value (all numeric, all long-text,
       etc.) -- DuckDB picked the wrong row as the header.
    3. At least half of the names look like data values, including any
       section with 1-3 columns where even one bad name is enough --
       a single ``Av. de los Pinos 23, ES`` column among two others
       is clearly a misdetected contact section.

    Clean inputs -- a CSV with ``id, name, email``, an XLSX sheet whose
    first row is ``Activos | 2024-12-31 | 2023-12-31`` -- pass through
    untouched (no LLM call).
    """
    if not current_names:
        return False
    if all(_SYNTHETIC_NAME_RE.match(n) for n in current_names):
        return True
    data_like = sum(1 for n in current_names if _looks_like_data_value(n))
    if data_like == 0:
        return False
    threshold = max(1, len(current_names) // 2)
    return data_like >= threshold


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
