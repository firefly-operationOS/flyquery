# Copyright 2026 Firefly Software Solutions Inc
"""AutoLearner: promote first-shot OK runs to AGENT_LEARNED, quality=PROPOSED."""

from __future__ import annotations

import uuid
from typing import Any

from flyquery.interfaces.examples import ExampleCreate


class AutoLearner:
    """Proposes an examples row after a successful first-shot query run.

    Skips when:
    - ``retries > 0`` (query required critic refinement)
    - PII findings were detected in the result

    Called by QueryService (Phase D) after a successful execution.
    """

    def __init__(self, examples_service: Any) -> None:
        self._service = examples_service

    async def maybe_propose(
        self,
        *,
        tenant_id: str,
        workspace_id: uuid.UUID,
        dataset_id: uuid.UUID | None,
        question: str,
        generated_sql: str,
        retries: int,
        pii_findings: list[Any],
        query_id: uuid.UUID,
    ) -> None:
        """Insert a flyquery_examples row when all criteria pass.

        :param tenant_id: tenant identifier
        :param workspace_id: workspace UUID
        :param dataset_id: optional dataset UUID
        :param question: original NL question
        :param generated_sql: SQL that was executed successfully
        :param retries: number of critic refinement loops (must be 0 to propose)
        :param pii_findings: any PII signals detected (must be empty to propose)
        :param query_id: UUID of the parent query record
        """
        if retries > 0:
            return
        if pii_findings:
            return
        await self._service.create(
            tenant_id,
            workspace_id,
            ExampleCreate(
                question=question,
                generated_sql=generated_sql,
                dataset_id=dataset_id,
                citations_json={"query_id": str(query_id)},
            ),
            source="AGENT_LEARNED",
            quality="PROPOSED",
            actor="agent",
        )
