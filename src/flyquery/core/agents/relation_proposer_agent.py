# Copyright 2026 Firefly Software Solutions Inc
"""RelationProposerAgent — stage 6b LLM-driven relation discovery.

Finds cross-table join candidates that are NOT exact name matches
(the heuristic detector in stage 6a covers those). Examples:
  orders.email <-> customers.email (non-PK match)
  shipments.tracking_no <-> tracking_events.tracking_id (naming mismatch)

Output: ProposedRelations with up to N proposals per table-pair.
"""

from __future__ import annotations

from pydantic import BaseModel

from flyquery.core.agents.builder import build_agent


class ProposedRelation(BaseModel):
    from_table: str
    from_column: str
    to_table: str
    to_column: str
    confidence: float
    reason: str


class ProposedRelations(BaseModel):
    items: list[ProposedRelation]


def build_relation_proposer_agent(settings):
    """Build a RelationProposerAgent for stage 6b.

    Instructions loaded from ``resources/prompts/relation_proposer.yaml``.
    """
    from flyquery.core.agents.prompt_loader import load_prompt

    prompt = load_prompt("relation_proposer")
    return build_agent(
        name="flyquery-relation-proposer",
        model=settings.relation_proposer_model,
        output_type=ProposedRelations,
        instructions=prompt.instructions,
        settings=settings,
    )
