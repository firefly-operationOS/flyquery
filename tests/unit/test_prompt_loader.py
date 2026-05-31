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

"""Unit tests for the YAML+Jinja2 prompt loader.

These tests pin the contract for ``flyquery.core.agents.prompt_loader``:

* known prompts load with their ``instructions`` + ``user`` keys parsed
* render passes Jinja2 variables through
* unknown names raise ``PromptNotFoundError``
* the shipped grounding.yaml has the anti-hallucination rules baked in
  (regression guard for the LLM-tuning work on 2026-05-23)
"""

from __future__ import annotations

import pytest

from flyquery.core.agents.prompt_loader import (
    PromptNotFoundError,
    PromptTemplate,
    load_prompt,
)


def test_load_grounding_prompt_known() -> None:
    tpl = load_prompt("grounding")
    assert isinstance(tpl, PromptTemplate)
    assert tpl.name == "grounding"
    assert tpl.instructions, "grounding.yaml must declare instructions"
    assert tpl.user_template, "grounding.yaml must declare user template"


def test_load_unknown_raises() -> None:
    with pytest.raises(PromptNotFoundError):
        load_prompt("definitely-not-a-real-prompt")


def test_render_user_substitutes_variables() -> None:
    tpl = load_prompt("grounding")
    user_prompt = tpl.render_user(
        question="What are total assets?",
        starting_point_sql=None,
        inv_tables=[
            {
                "qualified_name": "ds.activos",
                "text": "columns: line_item, value_yr1",
            }
        ],
        column_hits=[],
        examples=[],
        metrics=[],
        glossary=[],
        relations=[],
    )
    assert "What are total assets?" in user_prompt
    assert "ds.activos" in user_prompt
    assert "Complete dataset catalogue" in user_prompt


def test_grounding_instructions_have_anti_hallucination_rules() -> None:
    """Regression guard for the anti-hallucination prompt tuning.

    The grounding agent was inventing ``balance_sheet`` /
    ``income_statement`` table names. The hard rules in the
    instructions explicitly call these out -- if someone reverts
    them, this test catches it.
    """
    tpl = load_prompt("grounding")
    instr = tpl.instructions
    assert "balance_sheet" in instr
    assert "income_statement" in instr
    assert "Never invent" in instr
    assert "Pick from the catalogue" in instr


def test_render_both_returns_tuple() -> None:
    tpl = load_prompt("grounding")
    instr, user = tpl.render(
        question="Q?",
        starting_point_sql=None,
        inv_tables=[],
        column_hits=[],
        examples=[],
        metrics=[],
        glossary=[],
        relations=[],
    )
    # Instructions are static (no jinja2 vars), so the rendered output
    # equals the source modulo trailing whitespace from YAML block
    # scalar's trailing newline.
    assert instr.strip() == tpl.instructions.strip()
    assert "Q?" in user
