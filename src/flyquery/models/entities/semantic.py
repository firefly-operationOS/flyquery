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

"""flyquery semantic layer entities.

Covers: semantic_metrics, semantic_dimensions, semantic_versions,
glossary_terms.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, Integer, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP, UUID
from sqlalchemy.orm import Mapped, mapped_column

from flyquery.models.entities import Base


class SemanticMetric(Base):
    __tablename__ = "flyquery_semantic_metrics"
    __table_args__ = (
        UniqueConstraint("dataset_id", "name", name="uq_flyquery_semantic_metrics_dataset_name"),
        CheckConstraint(
            "metric_type IN ('SIMPLE','RATIO','DERIVED','CUMULATIVE')",
            name="ck_flyquery_semantic_metrics_type",
        ),
        CheckConstraint(
            "status IN ('DRAFT','PUBLISHED','RETIRED')", name="ck_flyquery_semantic_metrics_status"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    tenant_id: Mapped[str] = mapped_column(String, nullable=False)
    workspace_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    dataset_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    label: Mapped[str | None] = mapped_column(String, nullable=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    definition_yaml: Mapped[str] = mapped_column(String, nullable=False)
    compiled_sql_template: Mapped[str | None] = mapped_column(String, nullable=True)
    metric_type: Mapped[str] = mapped_column(String, nullable=False, server_default=text("'SIMPLE'"))
    status: Mapped[str] = mapped_column(String, nullable=False, server_default=text("'DRAFT'"))
    current_version: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )


class SemanticDimension(Base):
    __tablename__ = "flyquery_semantic_dimensions"
    __table_args__ = (
        UniqueConstraint("dataset_id", "name", name="uq_flyquery_semantic_dimensions_dataset_name"),
        CheckConstraint(
            "metric_type IN ('SIMPLE','RATIO','DERIVED','CUMULATIVE')",
            name="ck_flyquery_semantic_dimensions_type",
        ),
        CheckConstraint(
            "dimension_type IN ('categorical','time')",
            name="ck_flyquery_semantic_dimensions_dimtype",
        ),
        CheckConstraint(
            "status IN ('DRAFT','PUBLISHED','RETIRED')", name="ck_flyquery_semantic_dimensions_status"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    tenant_id: Mapped[str] = mapped_column(String, nullable=False)
    workspace_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    dataset_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    label: Mapped[str | None] = mapped_column(String, nullable=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    definition_yaml: Mapped[str] = mapped_column(String, nullable=False)
    compiled_sql_template: Mapped[str | None] = mapped_column(String, nullable=True)
    metric_type: Mapped[str] = mapped_column(String, nullable=False, server_default=text("'SIMPLE'"))
    dimension_type: Mapped[str] = mapped_column(String, nullable=False, server_default=text("'categorical'"))
    status: Mapped[str] = mapped_column(String, nullable=False, server_default=text("'DRAFT'"))
    current_version: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )


class SemanticVersion(Base):
    __tablename__ = "flyquery_semantic_versions"
    __table_args__ = (
        UniqueConstraint("kind", "parent_id", "version", name="uq_versions_kind_parent_version"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    tenant_id: Mapped[str] = mapped_column(String, nullable=False)
    workspace_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    kind: Mapped[str] = mapped_column(String, nullable=False)
    parent_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    definition_yaml: Mapped[str] = mapped_column(String, nullable=False)
    compiled_sql_template: Mapped[str | None] = mapped_column(String, nullable=True)
    created_by: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )


class GlossaryTerm(Base):
    __tablename__ = "flyquery_glossary_terms"
    __table_args__ = (UniqueConstraint("workspace_id", "term", name="uq_glossary_workspace_term"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    tenant_id: Mapped[str] = mapped_column(String, nullable=False)
    workspace_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    term: Mapped[str] = mapped_column(String, nullable=False)
    definition: Mapped[str] = mapped_column(String, nullable=False)
    synonyms_json: Mapped[list] = mapped_column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))
    tags_json: Mapped[list] = mapped_column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))
    related_columns_json: Mapped[list] = mapped_column(
        JSONB, nullable=False, server_default=text("'[]'::jsonb")
    )
    related_metrics_json: Mapped[list] = mapped_column(
        JSONB, nullable=False, server_default=text("'[]'::jsonb")
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
