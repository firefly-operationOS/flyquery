# Copyright 2026 Firefly Software Solutions Inc
"""RenameDetectionAgent — Stage 3 deep-dive for ambiguous column renames.

When reconcile finds a removed column that could match multiple new columns
(ambiguous rename candidate), this agent receives:
  - The removed column (name, description, samples)
  - A list of candidate new columns (with description + samples)

It returns a ranked list of RenameProposals. The top proposal is auto-confirmed
if confidence ≥ 0.8; otherwise a RENAMED_CANDIDATE row is written for human review.
"""

from __future__ import annotations

from pydantic import BaseModel

from flyquery.core.agents.builder import build_agent


class RenameProposal(BaseModel):
    removed_column: str
    new_column: str
    confidence: float   # 0..1
    rationale: str


class RenameProposals(BaseModel):
    items: list[RenameProposal]


_INSTRUCTIONS = (
    "You receive a removed database column and a list of candidate replacement "
    "columns from the new schema snapshot. The removed column may have been "
    "renamed to one of the candidates. "
    "For each candidate, assess how likely it is to be the same column under a "
    "different name, considering: name similarity, data type compatibility, "
    "description similarity, and sample value overlap. "
    "Return a ranked list of proposals with confidence in [0,1] and a brief "
    "rationale. Rank from most to least likely. "
    "If no candidate is a plausible rename (they are genuinely new columns), "
    "return an empty items list."
)

# Auto-confirm threshold: if top proposal ≥ this confidence, reconcile
# treats it as confirmed without human review.
AUTO_CONFIRM_THRESHOLD = 0.8


def build_rename_detection_agent(settings):
    """Build a RenameDetectionAgent for Stage 3 ambiguous rename resolution."""
    return build_agent(
        name="flyquery-rename-detector",
        model=settings.rename_detect_model,
        output_type=RenameProposals,
        instructions=_INSTRUCTIONS,
        settings=settings,
        # Rename detection is a short task; cap output tokens tightly
        max_output_tokens=2048,
    )
