# Copyright 2026 Firefly Software Solutions Inc
"""Tables derive REST controller.

``POST /api/v1/tables:derive`` — run a SELECT and materialise the result
as a new DERIVED table (kind=DERIVED) in flyquery_tables.

The derived table participates in the query pipeline identically to an
uploaded table: its Parquet snapshot is registered, schema objects are
created for retrieval, and subsequent queries can join against it.
"""

from __future__ import annotations

import uuid

from pyfly.container import rest_controller
from pyfly.web import Body, Valid, post_mapping, request_mapping
from starlette.requests import Request

from flyquery.core.services.derived.derived_table_service import DerivedTableService
from flyquery.web.conventions import tenant_context_from_request
from pydantic import BaseModel, ConfigDict, Field


class DeriveTableRequest(BaseModel):
    """Request body for POST /api/v1/tables:derive."""

    model_config = ConfigDict(populate_by_name=True)

    dataset_id: uuid.UUID
    name: str = Field(min_length=1, max_length=200)
    sql: str = Field(min_length=1, max_length=65536)


class DeriveTableResponse(BaseModel):
    """Response from POST /api/v1/tables:derive."""

    table_id: uuid.UUID
    name: str
    dataset_id: uuid.UUID


@rest_controller
@request_mapping("/api/v1")
class TablesDeriveController:
    """REST adapter for derived table materialisation.

    Accepts a SELECT statement, runs it via DuckDB against the dataset's
    current Parquet snapshots, writes the result as Parquet, and registers
    the new table in flyquery_tables (kind=DERIVED) with a READY snapshot.

    :param derived_table_service: service that orchestrates the derive flow
    """

    def __init__(self, derived_table_service: DerivedTableService) -> None:
        self._service = derived_table_service

    @post_mapping("/tables:derive", status_code=201)
    async def derive(
        self,
        http_request: Request,
        body: Valid[Body[DeriveTableRequest]],
    ) -> DeriveTableResponse:
        """Materialise a SELECT result as a new DERIVED table.

        :param http_request: Starlette request (tenant context headers)
        :param body: dataset_id + name + sql (must be a SELECT)
        :return: DeriveTableResponse with the new table_id
        :raises DeriveTableForbidden: when sql is not a SELECT
        :raises DeriveTableError: when DuckDB execution fails
        """
        ctx = tenant_context_from_request(http_request)
        workspace_id = uuid.UUID(str(ctx.workspace_id))

        table_id = await self._service.derive(
            tenant_id=ctx.tenant_id,
            workspace_id=workspace_id,
            dataset_id=body.dataset_id,
            name=body.name,
            sql=body.sql,
            actor=ctx.actor or "user",
        )

        return DeriveTableResponse(
            table_id=table_id,
            name=body.name,
            dataset_id=body.dataset_id,
        )
