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

"""SemanticDimensionsService: CRUD + lifecycle for semantic-layer dimensions.

A dimension compiles to a column expression (categorical → the expression
verbatim; time → ``DATE_TRUNC(grain, expr)``). That expression is stored as
``compiled_sql_template`` and substituted into metric ``group_by`` clauses
when a metric references the dimension by name.
"""

from __future__ import annotations

import uuid
from typing import Any

from pyfly.container import service as service_bean

from flyquery.core.services.semantic.firewall import assert_safe_dimension_expr
from flyquery.core.services.semantic.semantic_dimensions_repository import (
    SemanticDimensionsRepository,
)
from flyquery.core.services.semantic.yaml_schema import (
    DimensionDefinition,
    validate_dimension_yaml,
)
from flyquery.interfaces.semantic import SemanticDimensionCreate, SemanticDimensionUpdate


def _compile_dimension(definition: DimensionDefinition) -> str:
    """Compile a dimension to its column expression (grain-truncated for time)."""
    if definition.type == "time":
        return f"DATE_TRUNC('{definition.grain}', {definition.expr})"
    return definition.expr


@service_bean
class SemanticDimensionsService:
    """Business logic for the semantic layer (dimensions lifecycle)."""

    def __init__(self, semantic_dimensions_repository: SemanticDimensionsRepository) -> None:
        self._repo = semantic_dimensions_repository

    async def create(
        self,
        tenant_id: str,
        workspace_id: uuid.UUID,
        body: SemanticDimensionCreate,
        *,
        actor: str = "user",
    ) -> dict[str, Any]:
        """Create a new semantic dimension in DRAFT status (validates the YAML)."""
        definition = validate_dimension_yaml(body.definition_yaml)
        return await self._repo.create_dimension(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            dataset_id=body.dataset_id,
            name=body.name,
            label=body.label or definition.label,
            description=body.description or definition.description,
            definition_yaml=body.definition_yaml,
            dimension_type=definition.type,
            metadata_json={},
            created_by=actor,
        )

    async def list(
        self,
        tenant_id: str,
        workspace_id: uuid.UUID,
        *,
        dataset_id: uuid.UUID | None = None,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        """Return dimensions for a workspace (optionally filtered by dataset/status)."""
        return await self._repo.list_dimensions(tenant_id, workspace_id, dataset_id=dataset_id, status=status)

    async def get(
        self, tenant_id: str, workspace_id: uuid.UUID, dimension_id: uuid.UUID
    ) -> dict[str, Any] | None:
        """Fetch a single dimension by id; returns None when not found."""
        return await self._repo.get_dimension(dimension_id, tenant_id=tenant_id, workspace_id=workspace_id)

    async def update(
        self,
        tenant_id: str,
        workspace_id: uuid.UUID,
        dimension_id: uuid.UUID,
        body: SemanticDimensionUpdate,
        *,
        actor: str = "user",
    ) -> dict[str, Any]:
        """Sparse-update a dimension; recompiles if PUBLISHED and the YAML changes."""
        existing = await self._repo.get_dimension(
            dimension_id, tenant_id=tenant_id, workspace_id=workspace_id
        )
        if existing is None:
            raise KeyError(f"dimension {dimension_id} not found")
        fields = body.model_dump(exclude_unset=True, exclude_none=True)
        if "definition_yaml" in fields:
            definition = validate_dimension_yaml(fields["definition_yaml"])
            fields["dimension_type"] = definition.type
            if existing["status"] == "PUBLISHED":
                expr = _compile_dimension(definition)
                assert_safe_dimension_expr(expr)
                fields["compiled_sql_template"] = expr
        fields["created_by"] = actor
        return await self._repo.update_dimension(
            dimension_id, tenant_id=tenant_id, workspace_id=workspace_id, **fields
        )

    async def publish(
        self, tenant_id: str, workspace_id: uuid.UUID, dimension_id: uuid.UUID
    ) -> dict[str, Any]:
        """Validate, compile, firewall, and publish a dimension."""
        dimension = await self._repo.get_dimension(
            dimension_id, tenant_id=tenant_id, workspace_id=workspace_id
        )
        if dimension is None:
            raise KeyError(f"dimension {dimension_id} not found")
        definition = validate_dimension_yaml(dimension["definition_yaml"])
        expr = _compile_dimension(definition)
        assert_safe_dimension_expr(expr)
        return await self._repo.publish_dimension(
            dimension_id, expr, tenant_id=tenant_id, workspace_id=workspace_id
        )

    async def retire(
        self, tenant_id: str, workspace_id: uuid.UUID, dimension_id: uuid.UUID
    ) -> dict[str, Any]:
        """Retire a dimension (status → RETIRED)."""
        return await self._repo.retire_dimension(dimension_id, tenant_id=tenant_id, workspace_id=workspace_id)

    async def list_history(
        self, tenant_id: str, workspace_id: uuid.UUID, dimension_id: uuid.UUID
    ) -> list[dict[str, Any]]:
        """Return version history for a dimension, oldest first."""
        return await self._repo.list_history(dimension_id, tenant_id=tenant_id, workspace_id=workspace_id)
