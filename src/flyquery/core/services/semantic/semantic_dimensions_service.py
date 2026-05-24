# Copyright 2026 Firefly Software Solutions Inc
"""SemanticDimensionsService: CRUD + lifecycle for semantic-layer dimensions."""

from __future__ import annotations

import uuid
from typing import Any, Protocol

from pyfly.container import service as service_bean

from flyquery.core.services.semantic.metricflow_compiler import MetricFlowCompiler
from flyquery.core.services.semantic.semantic_dimensions_repository import (
    SemanticDimensionsRepository,
)
from flyquery.core.services.semantic.yaml_schema import validate_metric_yaml
from flyquery.interfaces.semantic import SemanticDimensionCreate, SemanticDimensionUpdate


class _Repo(Protocol):
    async def create_dimension(self, **fields: Any) -> dict[str, Any]: ...
    async def list_dimensions(
        self, tenant_id: str, workspace_id: uuid.UUID, *, dataset_id: uuid.UUID | None
    ) -> list[dict[str, Any]]: ...
    async def get_dimension(self, dimension_id: uuid.UUID) -> dict[str, Any] | None: ...
    async def update_dimension(self, dimension_id: uuid.UUID, **fields: Any) -> dict[str, Any]: ...
    async def publish_dimension(self, dimension_id: uuid.UUID, compiled_sql: str) -> dict[str, Any]: ...
    async def retire_dimension(self, dimension_id: uuid.UUID) -> dict[str, Any]: ...
    async def list_history(self, dimension_id: uuid.UUID) -> list[dict[str, Any]]: ...


@service_bean
class SemanticDimensionsService:
    """Business logic for the semantic layer (dimensions lifecycle)."""

    def __init__(self, semantic_dimensions_repository: SemanticDimensionsRepository) -> None:
        # Parameter renamed from ``repo`` to match snake-cased bean name.
        self._repo: _Repo = semantic_dimensions_repository

    async def create(
        self,
        tenant_id: str,
        workspace_id: uuid.UUID,
        body: SemanticDimensionCreate,
        *,
        actor: str = "user",
    ) -> dict[str, Any]:
        """Create a new semantic dimension in DRAFT status.

        :param tenant_id: tenant identifier
        :param workspace_id: workspace UUID
        :param body: validated create payload (includes definition_yaml)
        :param actor: who created the dimension
        :return: full dimension dict
        :raises MetricYamlError: if the YAML fails schema validation
        """
        validate_metric_yaml(body.definition_yaml)
        return await self._repo.create_dimension(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            dataset_id=body.dataset_id,
            name=body.name,
            label=body.label,
            description=body.description,
            definition_yaml=body.definition_yaml,
            metric_type=body.metric_type,
            created_by=actor,
        )

    async def list(
        self,
        tenant_id: str,
        workspace_id: uuid.UUID,
        *,
        dataset_id: uuid.UUID | None = None,
    ) -> list[dict[str, Any]]:
        """Return all dimensions for a workspace."""
        return await self._repo.list_dimensions(tenant_id, workspace_id, dataset_id=dataset_id)

    async def get(self, dimension_id: uuid.UUID) -> dict[str, Any] | None:
        """Fetch a single dimension by id; returns None when not found."""
        return await self._repo.get_dimension(dimension_id)

    async def update(
        self,
        dimension_id: uuid.UUID,
        body: SemanticDimensionUpdate,
        *,
        actor: str = "user",
    ) -> dict[str, Any]:
        """Sparse-update a dimension; re-validates YAML if definition changes.

        :param dimension_id: dimension primary key
        :param body: sparse update payload
        :param actor: who is making the change
        :return: updated dimension dict
        :raises MetricYamlError: if updated YAML fails validation
        """
        fields = body.model_dump(exclude_unset=True, exclude_none=True)
        if "definition_yaml" in fields:
            validate_metric_yaml(fields["definition_yaml"])
        fields["created_by"] = actor
        return await self._repo.update_dimension(dimension_id, **fields)

    async def publish(self, dimension_id: uuid.UUID) -> dict[str, Any]:
        """Validate, compile, and publish a dimension.

        Compiles the current ``definition_yaml`` to a DuckDB SQL template
        and persists it before flipping status to PUBLISHED.

        :param dimension_id: dimension primary key
        :return: published dimension dict with ``compiled_sql_template`` set
        :raises MetricYamlError: if the YAML is invalid at publish time
        """
        dimension = await self._repo.get_dimension(dimension_id)
        if dimension is None:
            raise KeyError(f"dimension {dimension_id} not found")
        validate_metric_yaml(dimension["definition_yaml"])
        import yaml as _yaml

        compiled_sql = MetricFlowCompiler.compile(_yaml.safe_load(dimension["definition_yaml"]))
        return await self._repo.publish_dimension(dimension_id, compiled_sql)

    async def retire(self, dimension_id: uuid.UUID) -> dict[str, Any]:
        """Retire a dimension (status → RETIRED).

        :param dimension_id: dimension primary key
        :return: retired dimension dict
        """
        return await self._repo.retire_dimension(dimension_id)

    async def list_history(self, dimension_id: uuid.UUID) -> list[dict[str, Any]]:
        """Return version history for a dimension, oldest first."""
        return await self._repo.list_history(dimension_id)
