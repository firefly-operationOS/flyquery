# Copyright 2026 Firefly Software Solutions Inc
"""SemanticService: CRUD + lifecycle for semantic-layer metrics."""

from __future__ import annotations

import uuid
from typing import Any, Protocol

from pyfly.container import service as service_bean

from flyquery.core.services.semantic.metricflow_compiler import MetricFlowCompiler
from flyquery.core.services.semantic.semantic_repository import SemanticRepository
from flyquery.core.services.semantic.yaml_schema import validate_metric_yaml
from flyquery.interfaces.semantic import SemanticMetricCreate, SemanticMetricUpdate


class _Repo(Protocol):
    async def create_metric(self, **fields: Any) -> dict[str, Any]: ...
    async def list_metrics(
        self, tenant_id: str, workspace_id: uuid.UUID, *, dataset_id: uuid.UUID | None
    ) -> list[dict[str, Any]]: ...
    async def get_metric(self, metric_id: uuid.UUID) -> dict[str, Any] | None: ...
    async def update_metric(self, metric_id: uuid.UUID, **fields: Any) -> dict[str, Any]: ...
    async def publish_metric(self, metric_id: uuid.UUID, compiled_sql: str) -> dict[str, Any]: ...
    async def retire_metric(self, metric_id: uuid.UUID) -> dict[str, Any]: ...
    async def list_history(self, metric_id: uuid.UUID) -> list[dict[str, Any]]: ...


@service_bean
class SemanticService:
    """Business logic for the semantic layer (metrics lifecycle)."""

    def __init__(self, semantic_repository: SemanticRepository) -> None:
        # Parameter renamed from ``repo`` to match snake-cased bean name.
        self._repo: _Repo = semantic_repository

    async def create(
        self,
        tenant_id: str,
        workspace_id: uuid.UUID,
        body: SemanticMetricCreate,
        *,
        actor: str = "user",
    ) -> dict[str, Any]:
        """Create a new semantic metric in DRAFT status.

        :param tenant_id: tenant identifier
        :param workspace_id: workspace UUID
        :param body: validated create payload (includes definition_yaml)
        :param actor: who created the metric
        :return: full metric dict
        :raises MetricYamlError: if the YAML fails schema validation
        """
        validate_metric_yaml(body.definition_yaml)
        return await self._repo.create_metric(
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
        """Return all metrics for a workspace."""
        return await self._repo.list_metrics(tenant_id, workspace_id, dataset_id=dataset_id)

    async def get(self, metric_id: uuid.UUID) -> dict[str, Any] | None:
        """Fetch a single metric by id; returns None when not found."""
        return await self._repo.get_metric(metric_id)

    async def update(
        self,
        metric_id: uuid.UUID,
        body: SemanticMetricUpdate,
        *,
        actor: str = "user",
    ) -> dict[str, Any]:
        """Sparse-update a metric; re-validates YAML if definition changes.

        :param metric_id: metric primary key
        :param body: sparse update payload
        :param actor: who is making the change
        :return: updated metric dict
        :raises MetricYamlError: if updated YAML fails validation
        """
        fields = body.model_dump(exclude_unset=True, exclude_none=True)
        if "definition_yaml" in fields:
            validate_metric_yaml(fields["definition_yaml"])
        fields["created_by"] = actor
        return await self._repo.update_metric(metric_id, **fields)

    async def publish(self, metric_id: uuid.UUID) -> dict[str, Any]:
        """Validate, compile, and publish a metric.

        Compiles the current ``definition_yaml`` to a DuckDB SQL template
        and persists it on the metric row before flipping status to PUBLISHED.

        :param metric_id: metric primary key
        :return: published metric dict with ``compiled_sql_template`` set
        :raises MetricYamlError: if the YAML is invalid at publish time
        """
        metric = await self._repo.get_metric(metric_id)
        if metric is None:
            raise KeyError(f"metric {metric_id} not found")
        validate_metric_yaml(metric["definition_yaml"])
        import yaml as _yaml

        compiled_sql = MetricFlowCompiler.compile(_yaml.safe_load(metric["definition_yaml"]))
        return await self._repo.publish_metric(metric_id, compiled_sql)

    async def retire(self, metric_id: uuid.UUID) -> dict[str, Any]:
        """Retire a metric (status → RETIRED).

        :param metric_id: metric primary key
        :return: retired metric dict
        """
        return await self._repo.retire_metric(metric_id)

    async def list_history(self, metric_id: uuid.UUID) -> list[dict[str, Any]]:
        """Return version history for a metric, oldest first."""
        return await self._repo.list_history(metric_id)
