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

"""CriticAgent — repairs a candidate SQL that failed DuckDB execution.

Consumes the failing SQL + DuckDB error message + GroundedContext and
produces a corrected SQL statement. Called up to MAX_REFINE_RETRIES times
within the query pipeline.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from flyquery.core.agents.builder import build_agent


class RefinedSql(BaseModel):
    sql: str
    reasoning: str
    confidence: float = Field(ge=0, le=1)


def build_critic_agent(settings):
    """Build a CriticAgent for the query pipeline.

    Instructions loaded from ``resources/prompts/critic.yaml``.
    """
    from flyquery.core.agents.prompt_loader import load_prompt

    prompt = load_prompt("critic")
    return build_agent(
        name="flyquery-critic",
        model=settings.critic_model,
        output_type=RefinedSql,
        instructions=prompt.instructions,
        settings=settings,
    )
