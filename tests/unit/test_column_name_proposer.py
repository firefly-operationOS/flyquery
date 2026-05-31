# Copyright 2024-2026 Firefly Software Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Unit tests for ColumnNameProposerAgent + the ``needs_proposal`` heuristic.

These tests pin down the trigger logic that decides whether a section's
header row needs to be replaced. They cover every concrete failure mode
seen on real Orbis/BvD XLSX uploads, plus the clean-input passthrough
cases that must NEVER cost an LLM call.
"""

from __future__ import annotations

from flyquery.core.agents.column_name_proposer_agent import (
    ProposedColumnNames,
    _looks_like_data_value,
    needs_proposal,
    render_proposal_prompt,
)


class TestLooksLikeDataValue:
    def test_synthetic_column_n(self):
        assert _looks_like_data_value("column00")
        assert _looks_like_data_value("column42")
        assert _looks_like_data_value("Column1")  # case-insensitive

    def test_numeric_literal(self):
        assert _looks_like_data_value("5302354.32")
        assert _looks_like_data_value("1234567")
        assert _looks_like_data_value("-987.5")
        assert _looks_like_data_value("1,234,567.89")  # thousands separator
        assert _looks_like_data_value("0")

    def test_long_text_block(self):
        long = "x" * 60
        assert _looks_like_data_value(long)
        very_long = "Av. de los Pinos 23, Edif Norte, 28042 Madrid, ES"
        # 49 chars -- under threshold but multi-comma
        assert _looks_like_data_value(very_long)

    def test_address_multi_comma(self):
        assert _looks_like_data_value("Madrid, ES, 28042")
        assert _looks_like_data_value("Calle Pinos 23, 28042 Madrid, ES")
        # only one comma -- should not trigger
        assert not _looks_like_data_value("Madrid, Spain")

    def test_legitimate_headers_not_flagged(self):
        # The cases that MUST pass through unchanged.
        assert not _looks_like_data_value("id")
        assert not _looks_like_data_value("country_code")
        assert not _looks_like_data_value("Total amount (USD)")
        assert not _looks_like_data_value("2020-12-31")  # period header
        assert not _looks_like_data_value("Activos")
        assert not _looks_like_data_value("Pérdidas y Ganancias")
        assert not _looks_like_data_value("email")
        assert not _looks_like_data_value("line_item")

    def test_empty_and_whitespace(self):
        assert not _looks_like_data_value("")
        assert not _looks_like_data_value("   ")
        assert not _looks_like_data_value(None)  # type: ignore[arg-type]


class TestNeedsProposal:
    def test_empty_list(self):
        assert not needs_proposal([])

    def test_all_synthetic(self):
        """DuckDB picked no header row at all -- the classic XLSX case."""
        assert needs_proposal([f"column{i:02d}" for i in range(10)])

    def test_clean_csv_passes_through(self):
        """A clean CSV with real headers must not trigger an LLM call."""
        assert not needs_proposal(["id", "name", "email", "country_code"])

    def test_period_headers_pass_through(self):
        """``2020-12-31 .. 2024-12-31`` are legitimate date headers."""
        assert not needs_proposal(["line_item", "2020-12-31", "2021-12-31", "2022-12-31", "2023-12-31"])

    def test_all_numeric_headers(self):
        """DuckDB picked a row of financial values as the header."""
        assert needs_proposal(["5302354.32", "4823195.55", "4321500.00", "3998000.00"])

    def test_single_column_with_address(self):
        """Contact section: one column whose name is an address line."""
        assert needs_proposal(["Av. de los Pinos 23, 28042 Madrid, ES"])

    def test_mixed_majority_data(self):
        """≥50% data-like names triggers (10-col section, 5 numeric)."""
        names = ["line_item", "1234.56", "2345.67", "3456.78", "4567.89", "5678.90", "x", "y", "z", "w"]
        assert needs_proposal(names)

    def test_mixed_minority_data_passes(self):
        """One bad name in 10 stays under threshold -- don't rename a mostly-clean section."""
        names = [
            "id",
            "name",
            "email",
            "country",
            "phone",
            "5302354.32",
            "active",
            "tier",
            "notes",
            "created_at",
        ]
        assert not needs_proposal(names)

    def test_small_section_one_bad_triggers(self):
        """For 1-3 column sections, a single bad name is enough."""
        assert needs_proposal(["1234.56", "id", "name"])
        assert needs_proposal(["1234.56"])
        assert needs_proposal(["foo", "1234.56"])

    def test_dates_alone_pass_through(self):
        """Sheet whose headers are all dates -- legitimate period table."""
        assert not needs_proposal(["2020-12-31", "2021-12-31", "2022-12-31"])


class TestProposedColumnNamesSchema:
    def test_pydantic_model_roundtrip(self):
        obj = ProposedColumnNames(proposed_names=["line_item", "period_end_2024"])
        assert obj.proposed_names == ["line_item", "period_end_2024"]
        as_dict = obj.model_dump()
        assert as_dict["proposed_names"] == ["line_item", "period_end_2024"]


class TestRenderProposalPrompt:
    def test_prompt_includes_section_label(self):
        prompt = render_proposal_prompt(
            section_label="Activos",
            current_names=["column00", "column01"],
            sample_values=[["Activos fijos", "Activos totales"], [1234.5, 5678.9]],
        )
        assert "Activos" in prompt
        assert "column00" in prompt
        assert "column01" in prompt
        assert "Activos fijos" in prompt
        assert "2 " in prompt  # "exactly 2 entries"

    def test_prompt_handles_empty_samples(self):
        prompt = render_proposal_prompt(
            section_label="Empty",
            current_names=["column00"],
            sample_values=[[]],
        )
        assert "no samples available" in prompt

    def test_prompt_truncates_long_samples(self):
        prompt = render_proposal_prompt(
            section_label="Long",
            current_names=["column00"],
            sample_values=[["x" * 200]],
        )
        # max 80 chars per sample (per the renderer's truncation)
        assert "x" * 80 in prompt
        assert "x" * 81 not in prompt
