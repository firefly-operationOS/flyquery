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

"""SemanticService: CRUD + lifecycle for semantic-layer metrics.

Publish/update compile the definition to a DuckDB SQL template via
:class:`SemanticCompiler`, then run it through the publish-time firewall
before persisting. ``group_by`` entries that name a published dimension are
resolved to that dimension's compiled expression; measure expressions are
qualified ``table.column`` references.
"""

from __future__ import annotations

import uuid
from typing import Any

from pyfly.container import service as service_bean

from flyquery.core.services.semantic.compiler import SemanticCompiler
from flyquery.core.services.semantic.firewall import assert_safe_template
from flyquery.core.services.semantic.semantic_dimensions_repository import (
    SemanticDimensionsRepository,
)
from flyquery.core.services.semantic.semantic_repository import SemanticRepository
from flyquery.core.services.semantic.yaml_schema import MetricDefinition, validate_metric_yaml
from flyquery.interfaces.semantic import SemanticMetricCreate, SemanticMetricUpdate


@service_bean
class SemanticService:
    """Business logic for the semantic layer (metrics lifecycle)."""

    def __init__(
        self,
        semantic_repository: SemanticRepository,
        semantic_dimensions_repository: SemanticDimensionsRepository,
    ) -> None:
        self._repo = semantic_repository
        self._dim_repo = semantic_dimensions_repository

    # ------------------------------------------------------------------
    # Compilation helpers
    # ------------------------------------------------------------------

    async def _compile(
        self,
        definition: MetricDefinition,
        *,
        tenant_id: str,
        workspace_id: uuid.UUID,
        dataset_id: uuid.UUID,
    ) -> str:
        """Compile + firewall a validated definition, resolving dimension group-bys."""
        dim_map: dict[str, str] = {}
        for col in definition.group_by:
            if "." in col:
                continue
            row = await self._dim_repo.get_by_name(
                col, dataset_id, tenant_id=tenant_id, workspace_id=workspace_id
            )
            if row and row.get("compiled_sql_template"):
                dim_map[col] = row["compiled_sql_template"]
        compiled = SemanticCompiler.compile(
            definition,
            resolve_dimension=lambda name, ds=None: dim_map.get(name, name),
            dataset_id=dataset_id,
        )
        assert_safe_template(compiled)
        return compiled

    # ------------------------------------------------------------------
    # CRUD + lifecycle
    # ------------------------------------------------------------------

    async def create(
        self,
        tenant_id: str,
        workspace_id: uuid.UUID,
        body: SemanticMetricCreate,
        *,
        actor: str = "user",
    ) -> dict[str, Any]:
        """Create a new semantic metric in DRAFT status (validates the YAML)."""
        definition = validate_metric_yaml(body.definition_yaml)
        return await self._repo.create_metric(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            dataset_id=body.dataset_id,
            name=body.name,
            label=body.label or definition.label,
            description=body.description or definition.description,
            definition_yaml=body.definition_yaml,
            metric_type=definition.type.upper(),
            metadata_json=definition.meta,
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
        """Return metrics for a workspace (optionally filtered by dataset/status)."""
        return await self._repo.list_metrics(
            tenant_id, workspace_id, dataset_id=dataset_id, status=status
        )

    async def get(
        self, tenant_id: str, workspace_id: uuid.UUID, metric_id: uuid.UUID
    ) -> dict[str, Any] | None:
        """Fetch a single metric by id; returns None when not found."""
        return await self._repo.get_metric(metric_id, tenant_id=tenant_id, workspace_id=workspace_id)

    async def update(
        self,
        tenant_id: str,
        workspace_id: uuid.UUID,
        metric_id: uuid.UUID,
        body: SemanticMetricUpdate,
        *,
        actor: str = "user",
    ) -> dict[str, Any]:
        """Sparse-update a metric; recompiles + re-publishes if it was PUBLISHED."""
        existing = await self._repo.get_metric(
            metric_id, tenant_id=tenant_id, workspace_id=workspace_id
        )
        if existing is None:
            raise KeyError(f"metric {metric_id} not found")

        fields = body.model_dump(exclude_unset=True, exclude_none=True)
        if "definition_yaml" in fields:
            definition = validate_metric_yaml(fields["definition_yaml"])
            fields["metric_type"] = definition.type.upper()
            fields["metadata_json"] = definition.meta
            if existing["status"] == "PUBLISHED":
                fields["compiled_sql_template"] = await self._compile(
                    definition,
                    tenant_id=tenant_id,
                    workspace_id=workspace_id,
                    dataset_id=existing["dataset_id"],
                )
        fields["created_by"] = actor
        return await self._repo.update_metric(
            metric_id, tenant_id=tenant_id, workspace_id=workspace_id, **fields
        )

    async def publish(
        self, tenant_id: str, workspace_id: uuid.UUID, metric_id: uuid.UUID
    ) -> dict[str, Any]:
        """Validate, compile, firewall, and publish a metric."""
        metric = await self._repo.get_metric(
            metric_id, tenant_id=tenant_id, workspace_id=workspace_id
        )
        if metric is None:
            raise KeyError(f"metric {metric_id} not found")
        definition = validate_metric_yaml(metric["definition_yaml"])
        compiled_sql = await self._compile(
            definition,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            dataset_id=metric["dataset_id"],
        )
        return await self._repo.publish_metric(
            metric_id, compiled_sql, tenant_id=tenant_id, workspace_id=workspace_id
        )

    async def retire(
        self, tenant_id: str, workspace_id: uuid.UUID, metric_id: uuid.UUID
    ) -> dict[str, Any]:
        """Retire a metric (status → RETIRED)."""
        return await self._repo.retire_metric(
            metric_id, tenant_id=tenant_id, workspace_id=workspace_id
        )

    async def list_history(
        self, tenant_id: str, workspace_id: uuid.UUID, metric_id: uuid.UUID
    ) -> list[dict[str, Any]]:
        """Return version history for a metric, oldest first."""
        return await self._repo.list_history(
            metric_id, tenant_id=tenant_id, workspace_id=workspace_id
        )
