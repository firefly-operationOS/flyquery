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
    confidence: float  # 0..1
    rationale: str


class RenameProposals(BaseModel):
    items: list[RenameProposal]


# Auto-confirm threshold: if top proposal ≥ this confidence, reconcile
# treats it as confirmed without human review.
AUTO_CONFIRM_THRESHOLD = 0.8


def build_rename_detection_agent(settings):
    """Build a RenameDetectionAgent for Stage 3 ambiguous rename resolution.

    Instructions loaded from ``resources/prompts/rename_detection.yaml``.
    """
    from flyquery.core.agents.prompt_loader import load_prompt

    prompt = load_prompt("rename_detection")
    return build_agent(
        name="flyquery-rename-detector",
        model=settings.rename_detect_model,
        output_type=RenameProposals,
        instructions=prompt.instructions,
        settings=settings,
        # Rename detection is a short task; cap output tokens tightly
        max_output_tokens=2048,
    )
