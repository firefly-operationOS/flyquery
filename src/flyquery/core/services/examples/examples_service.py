# Copyright 2026 Firefly Software Solutions Inc
"""ExamplesService: create, list, approve, reject question+SQL pairs."""

from __future__ import annotations

import re
import uuid
from typing import Any, Protocol

from pyfly.container import service as service_bean

from flyquery.core.services.examples.examples_repository import ExamplesRepository
from flyquery.core.services.retrieval.embedder import OpenAiEmbedder
from flyquery.interfaces.examples import ExampleCreate


def _normalise_sql(sql: str) -> str:
    """Deterministic SQL normalisation for deduplication.

    Tries ``sqlglot`` first (canonical AST round-trip).  Falls back to
    a simple lowercase + whitespace-collapse when sqlglot is unavailable
    or fails to parse the statement.
    """
    try:
        import sqlglot

        parsed = sqlglot.parse_one(sql)
        return parsed.sql(normalize=True)
    except Exception:  # noqa: BLE001
        return re.sub(r"\s+", " ", sql.strip().lower())


class _Repo(Protocol):
    async def create(self, **fields: Any) -> dict[str, Any]: ...
    async def list(
        self,
        tenant_id: str,
        workspace_id: uuid.UUID,
        *,
        quality: str | None,
        dataset_id: uuid.UUID | None,
        limit: int,
    ) -> list[dict[str, Any]]: ...
    async def get(self, example_id: uuid.UUID) -> dict[str, Any] | None: ...
    async def update_quality(self, example_id: uuid.UUID, quality: str) -> dict[str, Any]: ...


@service_bean
class ExamplesService:
    """Business logic for the examples knowledge base."""

    def __init__(self, repo: ExamplesRepository, embedder: OpenAiEmbedder | None = None) -> None:
        self._repo: _Repo = repo
        self._embedder = embedder  # may be None — embeddings stay NULL

    async def create(
        self,
        tenant_id: str,
        workspace_id: uuid.UUID,
        body: ExampleCreate,
        *,
        source: str = "USER_CURATED",
        quality: str = "PROPOSED",
        actor: str = "user",
    ) -> dict[str, Any]:
        """Insert a new example row.

        :param tenant_id: tenant identifier from request context
        :param workspace_id: workspace UUID
        :param body: validated create payload
        :param source: USER_CURATED (default) or AGENT_LEARNED
        :param quality: PROPOSED (default) — operator upgrades to APPROVED
        :param actor: who created the example (user / agent)
        :return: full example dict
        """
        normalised = _normalise_sql(body.generated_sql)
        embedding = None
        if self._embedder is not None:
            embedding = await self._embedder.embed(body.question)
        return await self._repo.create(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            dataset_id=body.dataset_id,
            question=body.question,
            generated_sql=body.generated_sql,
            normalised_sql=normalised,
            source=source,
            quality=quality,
            citations_json=body.citations_json,
            created_by=actor,
            embedding=embedding,
        )

    async def list(
        self,
        tenant_id: str,
        workspace_id: uuid.UUID,
        *,
        quality: str | None = None,
        dataset_id: uuid.UUID | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """List examples for a workspace, optionally filtered by quality or dataset."""
        return await self._repo.list(
            tenant_id,
            workspace_id,
            quality=quality,
            dataset_id=dataset_id,
            limit=limit,
        )

    async def get(self, example_id: uuid.UUID) -> dict[str, Any] | None:
        """Fetch a single example by id; returns None when not found."""
        return await self._repo.get(example_id)

    async def approve(self, example_id: uuid.UUID) -> dict[str, Any]:
        """Promote an example to APPROVED quality."""
        return await self._repo.update_quality(example_id, "APPROVED")

    async def reject(self, example_id: uuid.UUID) -> dict[str, Any]:
        """Reject an example (set quality=REJECTED)."""
        return await self._repo.update_quality(example_id, "REJECTED")
