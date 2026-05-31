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


def build_explainer_agent(settings):
    """Build an ExplainerAgent for the query pipeline.

    Instructions loaded from ``resources/prompts/explainer.yaml``.
    """
    from flyquery.core.agents.prompt_loader import load_prompt

    prompt = load_prompt("explainer")
    return build_agent(
        name="flyquery-explainer",
        model=settings.explainer_model,
        output_type=ResultExplanation,
        instructions=prompt.instructions,
        settings=settings,
    )
