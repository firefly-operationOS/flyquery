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

"""GenerationAgent — writes N candidate SQL queries from a GroundedContext.

Consumes the GroundedContext produced by the GroundingAgent and generates
N candidate SQL statements ordered by confidence, highest first.
Trust order: SEMANTIC_LAYER > UPLOADED_TABLE.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from flyquery.core.agents.builder import build_agent


class GeneratedCandidate(BaseModel):
    sql: str
    reasoning: str
    confidence: float = Field(ge=0, le=1)


class GeneratedCandidates(BaseModel):
    candidates: list[GeneratedCandidate]  # always N items, ordered by confidence descending


def build_generation_agent(settings):
    """Build a GenerationAgent for the query pipeline.

    Instructions loaded from ``resources/prompts/generation.yaml``.
    """
    from flyquery.core.agents.prompt_loader import load_prompt

    prompt = load_prompt("generation")
    return build_agent(
        name="flyquery-generation",
        model=settings.generation_model,
        output_type=GeneratedCandidates,
        instructions=prompt.instructions,
        settings=settings,
    )
