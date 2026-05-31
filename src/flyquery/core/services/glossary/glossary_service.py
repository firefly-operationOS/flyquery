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

"""GlossaryService: CRUD over workspace-scoped glossary terms."""

from __future__ import annotations

import uuid
from typing import Any, Protocol

from pyfly.container import service as service_bean

from flyquery.core.services.glossary.glossary_repository import GlossaryRepository
from flyquery.interfaces.glossary import GlossaryTermCreate, GlossaryTermUpdate


class _Repo(Protocol):
    async def create(self, **fields: Any) -> dict[str, Any]: ...
    async def list(
        self,
        tenant_id: str,
        workspace_id: uuid.UUID,
        *,
        limit: int,
        offset: int,
    ) -> list[dict[str, Any]]: ...
    async def get(self, term_id: uuid.UUID) -> dict[str, Any] | None: ...
    async def update(self, term_id: uuid.UUID, **fields: Any) -> dict[str, Any]: ...
    async def delete(self, term_id: uuid.UUID) -> None: ...


@service_bean
class GlossaryService:
    """Business logic for the workspace glossary."""

    def __init__(self, repo: GlossaryRepository) -> None:
        self._repo: _Repo = repo

    async def create(
        self,
        tenant_id: str,
        workspace_id: uuid.UUID,
        body: GlossaryTermCreate,
    ) -> dict[str, Any]:
        """Insert a new glossary term.

        :param tenant_id: tenant identifier
        :param workspace_id: workspace UUID
        :param body: validated create payload
        :return: full glossary term dict
        :raises: DB-level UniqueConstraintError on (workspace_id, term) duplicate
        """
        return await self._repo.create(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            term=body.term,
            definition=body.definition,
            synonyms_json=body.synonyms_json,
            tags_json=body.tags_json,
            related_columns_json=body.related_columns_json,
            related_metrics_json=body.related_metrics_json,
        )

    async def list(
        self,
        tenant_id: str,
        workspace_id: uuid.UUID,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Return paginated glossary terms for a workspace."""
        return await self._repo.list(tenant_id, workspace_id, limit=limit, offset=offset)

    async def get(self, term_id: uuid.UUID) -> dict[str, Any] | None:
        """Fetch a single glossary term; returns None when not found."""
        return await self._repo.get(term_id)

    async def update(self, term_id: uuid.UUID, body: GlossaryTermUpdate) -> dict[str, Any]:
        """Sparse-update a glossary term."""
        fields = body.model_dump(exclude_unset=True, exclude_none=False)
        return await self._repo.update(term_id, **{k: v for k, v in fields.items() if v is not None})

    async def delete(self, term_id: uuid.UUID) -> None:
        """Hard-delete a glossary term."""
        await self._repo.delete(term_id)
