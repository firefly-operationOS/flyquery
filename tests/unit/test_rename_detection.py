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

"""Unit tests for RenameDetectionAgent + Stage 3 rename detection logic."""

from __future__ import annotations

import pytest


class TestRenameDetectionAgent:
    def test_agent_models_importable(self):
        from flyquery.core.agents.rename_detection_agent import (
            AUTO_CONFIRM_THRESHOLD,
            RenameProposal,
        )

        assert AUTO_CONFIRM_THRESHOLD == 0.8
        proposal = RenameProposal(
            removed_column="old_col",
            new_column="new_col",
            confidence=0.9,
            rationale="Semantically equivalent.",
        )
        assert proposal.confidence == 0.9

    def test_rename_proposals_list(self):
        from flyquery.core.agents.rename_detection_agent import (
            RenameProposal,
            RenameProposals,
        )

        proposals = RenameProposals(
            items=[
                RenameProposal(removed_column="a", new_column="b", confidence=0.95, rationale="x"),
            ]
        )
        assert len(proposals.items) == 1
        assert proposals.items[0].confidence >= 0.8


class TestDetectRenamesLogic:
    """Test the _detect_renames helper with no agent (settings=None).

    ``_detect_renames`` returns a 3-tuple ``(confirmed, rationales, candidates)``
    so the LLM rename rationale can be persisted alongside the auto-confirmed
    match. With ``settings=None`` the LLM agent is skipped, so ambiguous
    removed-columns fall through to the unscored fallback candidates list.
    """

    @pytest.mark.asyncio
    async def test_unambiguous_rename_auto_confirmed(self):
        from flyquery.core.services.ingestion.stages.reconcile import _detect_renames

        # One removed col, one added col, same type → auto-confirmed
        confirmed, rationales, candidates = await _detect_renames(
            removed_names=["old_email"],
            added_names=["contact_email"],
            prev_columns={"old_email": "VARCHAR"},
            new_columns={"contact_email": "VARCHAR"},
            prev_detail=[],
            settings=None,
        )
        assert "old_email" in confirmed
        assert confirmed["old_email"] == "contact_email"
        # 1-to-1 type match emits a synthetic rationale so the persisted
        # llm_rationale field is never empty for auto-confirmed renames.
        assert "old_email" in rationales
        assert rationales["old_email"]
        assert candidates == []

    @pytest.mark.asyncio
    async def test_ambiguous_becomes_candidate(self):
        from flyquery.core.services.ingestion.stages.reconcile import _detect_renames

        # Two removed cols → two added cols, same type → ambiguous → candidates
        confirmed, rationales, candidates = await _detect_renames(
            removed_names=["col_a", "col_b"],
            added_names=["new_a", "new_b"],
            prev_columns={"col_a": "INTEGER", "col_b": "INTEGER"},
            new_columns={"new_a": "INTEGER", "new_b": "INTEGER"},
            prev_detail=[],
            settings=None,
        )
        # Settings=None → LLM agent skipped → fallback candidate list with
        # ``confidence=None`` and ``rationale=None`` for every entry.
        assert len(candidates) >= 1
        for _old_name, ranked in candidates:
            assert isinstance(ranked, list)
            for item in ranked:
                assert set(item.keys()) == {"name", "confidence", "rationale"}

    @pytest.mark.asyncio
    async def test_type_mismatch_no_rename(self):
        from flyquery.core.services.ingestion.stages.reconcile import _detect_renames

        # Type mismatch → no rename detected
        confirmed, rationales, candidates = await _detect_renames(
            removed_names=["old_col"],
            added_names=["new_col"],
            prev_columns={"old_col": "INTEGER"},
            new_columns={"new_col": "VARCHAR"},
            prev_detail=[],
            settings=None,
        )
        # Different types → no match at all
        assert "old_col" not in confirmed
        assert len(confirmed) == 0
        assert rationales == {}

    @pytest.mark.asyncio
    async def test_empty_lists_no_op(self):
        from flyquery.core.services.ingestion.stages.reconcile import _detect_renames

        confirmed, rationales, candidates = await _detect_renames(
            removed_names=[],
            added_names=[],
            prev_columns={},
            new_columns={},
            prev_detail=[],
            settings=None,
        )
        assert confirmed == {}
        assert rationales == {}
        assert candidates == []


class TestReconcileModuleImportable:
    def test_reconcile_importable(self):
        from flyquery.core.services.ingestion.stages.reconcile import run_reconcile

        assert callable(run_reconcile)
