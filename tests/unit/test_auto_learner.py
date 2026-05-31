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

"""Unit tests for AutoLearner."""

from __future__ import annotations

import uuid

import pytest

from flyquery.core.services.examples.auto_learner import AutoLearner


class FakeExamplesService:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    async def create(self, tenant_id, workspace_id, body, *, source, quality, actor):
        self.calls.append(
            {
                "tenant_id": tenant_id,
                "workspace_id": workspace_id,
                "body": body,
                "source": source,
                "quality": quality,
                "actor": actor,
            }
        )


@pytest.mark.asyncio
async def test_maybe_propose_inserts_on_first_shot_ok() -> None:
    svc = FakeExamplesService()
    learner = AutoLearner(svc)
    qid = uuid.uuid4()
    ws = uuid.uuid4()
    await learner.maybe_propose(
        tenant_id="ten-a",
        workspace_id=ws,
        dataset_id=None,
        question="total revenue",
        generated_sql="SELECT sum(total) FROM orders",
        retries=0,
        pii_findings=[],
        query_id=qid,
    )
    assert len(svc.calls) == 1
    call = svc.calls[0]
    assert call["source"] == "AGENT_LEARNED"
    assert call["quality"] == "PROPOSED"
    assert call["actor"] == "agent"
    assert str(qid) in str(call["body"].citations_json)


@pytest.mark.asyncio
async def test_maybe_propose_skips_when_retries_gt_zero() -> None:
    svc = FakeExamplesService()
    learner = AutoLearner(svc)
    await learner.maybe_propose(
        tenant_id="ten-a",
        workspace_id=uuid.uuid4(),
        dataset_id=None,
        question="q",
        generated_sql="SELECT 1",
        retries=1,
        pii_findings=[],
        query_id=uuid.uuid4(),
    )
    assert len(svc.calls) == 0


@pytest.mark.asyncio
async def test_maybe_propose_skips_when_pii_findings() -> None:
    svc = FakeExamplesService()
    learner = AutoLearner(svc)
    await learner.maybe_propose(
        tenant_id="ten-a",
        workspace_id=uuid.uuid4(),
        dataset_id=None,
        question="q",
        generated_sql="SELECT 1",
        retries=0,
        pii_findings=[{"type": "email"}],
        query_id=uuid.uuid4(),
    )
    assert len(svc.calls) == 0
