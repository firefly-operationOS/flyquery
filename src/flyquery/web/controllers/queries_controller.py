# Copyright 2026 Firefly Software Solutions Inc
"""Query history REST controller (v1.0 -- new in 26.5.10).

``/api/v1/queries`` -- read-side view over the ``flyquery_queries``
ledger that the query pipeline writes on every NL question. The write
path was always there; v1 ships the read endpoints so consumers can
audit / retry / re-download.

Path conventions:
* ``GET /api/v1/queries``              -- paginated history with filters
* ``GET /api/v1/queries/{id}``         -- single query with full candidate list
* ``GET /api/v1/queries/{id}/result``  -- re-download preview + presigned Parquet URL
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pyfly.container import rest_controller
from pyfly.web import PathVar, QueryParam, get_mapping, request_mapping
from starlette.requests import Request

from flyquery.config import FlyquerySettings
from flyquery.core.services.query.query_repository import QueryRepository
from flyquery.core.services.storage.object_store import ObjectStore
from flyquery.interfaces.pagination import Paginated
from flyquery.interfaces.query import QueryDetailRead, QueryHistoryItem, QueryResultRead
from flyquery.web.conventions import ResourceNotFound, tenant_context_from_request


@rest_controller
@request_mapping("/api/v1/queries")
class QueriesController:
    """REST adapter for ``flyquery_queries`` + ``flyquery_query_results`` reads."""

    def __init__(
        self,
        query_repository: QueryRepository,
        object_store: ObjectStore,
        settings: FlyquerySettings,
    ) -> None:
        self._repo = query_repository
        self._object_store = object_store
        self._settings = settings

    # ------------------------------------------------------------------
    # GET /api/v1/queries -- paginated history
    # ------------------------------------------------------------------

    @get_mapping("")
    async def list_queries(
        self,
        http_request: Request,
        dataset_id: QueryParam[uuid.UUID] = None,
        execution_status: QueryParam[str] = None,
        semantic_path_taken: QueryParam[str] = None,
        date_from: QueryParam[datetime] = None,
        date_to: QueryParam[datetime] = None,
        limit: QueryParam[int] = 50,
        offset: QueryParam[int] = 0,
    ) -> Paginated[QueryHistoryItem]:
        """List queries for the caller's workspace, newest first.

        Filters
        -------
        * ``dataset_id``           -- restrict to one dataset
        * ``execution_status``     -- ``OK`` / ``REJECTED_BY_FIREWALL`` / ``FAILED`` / ...
        * ``semantic_path_taken``  -- e.g. ``"sql"`` vs ``"semantic-layer"``
        * ``date_from``            -- inclusive lower bound on ``created_at``
        * ``date_to``              -- exclusive upper bound on ``created_at``

        Page size is clamped to ``[1, 200]``. Each item is the compact
        history shape (no heavy JSONB columns). Use
        ``GET /queries/{id}`` for the full row.
        """
        ctx = tenant_context_from_request(http_request)
        ws = uuid.UUID(ctx.workspace_id) if isinstance(ctx.workspace_id, str) else ctx.workspace_id
        rows, total = await self._repo.list_queries(
            tenant_id=ctx.tenant_id,
            workspace_id=ws,
            dataset_id=dataset_id,
            execution_status=execution_status,
            semantic_path_taken=semantic_path_taken,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            offset=offset,
        )
        items = [_to_history_item(r) for r in rows]
        clamped_limit = max(1, min(200, int(limit)))
        clamped_offset = max(0, int(offset))
        return Paginated.of(items, total=total, limit=clamped_limit, offset=clamped_offset)

    # ------------------------------------------------------------------
    # GET /api/v1/queries/{id} -- single with candidates
    # ------------------------------------------------------------------

    @get_mapping("/{query_id}")
    async def get_query(
        self,
        http_request: Request,
        query_id: PathVar[uuid.UUID],
    ) -> QueryDetailRead:
        """Fetch a single query with every candidate, retry, and model id.

        Returns 404 if the query doesn't belong to the caller's
        ``(tenant, workspace)`` -- not just "not found", but also
        "exists but wrong tenant" (cross-tenant probing is the same
        404 as missing).
        """
        ctx = tenant_context_from_request(http_request)
        ws = uuid.UUID(ctx.workspace_id) if isinstance(ctx.workspace_id, str) else ctx.workspace_id
        row = await self._repo.get_query(query_id, tenant_id=ctx.tenant_id, workspace_id=ws)
        if row is None:
            raise ResourceNotFound(f"query {query_id!r} not found")
        return _to_detail_read(row)

    # ------------------------------------------------------------------
    # GET /api/v1/queries/{id}/result -- re-download
    # ------------------------------------------------------------------

    @get_mapping("/{query_id}/result")
    async def get_query_result(
        self,
        http_request: Request,
        query_id: PathVar[uuid.UUID],
    ) -> QueryResultRead:
        """Re-download a previously-executed query's preview + parquet.

        The preview is always inlined. The presigned Parquet URL is
        ``None`` when the TTL has elapsed (default 24h) -- consumers
        must rerun the query in that case. The presign TTL itself is
        bounded by ``object_store_presign_ttl_s`` (default 24h).

        Returns 404 if either the query OR its result row doesn't
        exist for this tenant.
        """
        ctx = tenant_context_from_request(http_request)
        ws = uuid.UUID(ctx.workspace_id) if isinstance(ctx.workspace_id, str) else ctx.workspace_id

        # Validate the query exists + belongs to this tenant first so
        # we never expose a result URL for a row the caller can't see
        # via the parent GET.
        query_row = await self._repo.get_query(query_id, tenant_id=ctx.tenant_id, workspace_id=ws)
        if query_row is None:
            raise ResourceNotFound(f"query {query_id!r} not found")

        result_row = await self._repo.get_result(query_id, tenant_id=ctx.tenant_id, workspace_id=ws)
        if result_row is None:
            raise ResourceNotFound(f"no result stored for query {query_id!r}")

        url: str | None = None
        ttl_expires_at = result_row.get("ttl_expires_at")
        object_key = result_row.get("result_object_key")
        if object_key and _is_url_still_valid(ttl_expires_at):
            try:
                url = await self._object_store.presign_get(
                    object_key,
                    ttl_s=int(self._settings.object_store_presign_ttl_s),
                )
            except Exception:  # noqa: BLE001
                # Presign failure (e.g. object reclaimed by GC, or
                # backend transient outage) is non-fatal -- callers
                # still get the inline preview and can rerun the
                # query to materialise a fresh URL.
                url = None

        return QueryResultRead(
            query_id=query_id,
            preview_json=result_row.get("result_preview_json") or [],
            parquet_presigned_url=url,
            result_byte_size=result_row.get("result_byte_size"),
            ttl_expires_at=ttl_expires_at,
        )


# --------------------------------------------------------------------------- #
# Row -> DTO helpers
# --------------------------------------------------------------------------- #


def _to_history_item(row: dict[str, Any]) -> QueryHistoryItem:
    return QueryHistoryItem(
        id=row["id"],
        tenant_id=row["tenant_id"],
        workspace_id=row["workspace_id"],
        dataset_id=row.get("dataset_id"),
        question=row["question"],
        executed_sql=row.get("executed_sql"),
        ast_classification=row.get("ast_classification"),
        execution_status=row.get("execution_status"),
        row_count=row.get("row_count"),
        elapsed_ms=row.get("elapsed_ms"),
        semantic_path_taken=row.get("semantic_path_taken"),
        retries=row.get("retries", 0),
        clarification_emitted=row.get("clarification_emitted", False),
        created_at=row["created_at"],
        finalised_at=row.get("finalised_at"),
    )


def _to_detail_read(row: dict[str, Any]) -> QueryDetailRead:
    return QueryDetailRead(
        id=row["id"],
        tenant_id=row["tenant_id"],
        workspace_id=row["workspace_id"],
        dataset_id=row.get("dataset_id"),
        question=row["question"],
        prior_turn_ids=list(row.get("prior_turn_ids") or []),
        table_id_snapshot_pins_json=row.get("table_id_snapshot_pins_json"),
        semantic_path_taken=row.get("semantic_path_taken"),
        candidates_json=list(row.get("candidates_json") or []),
        chosen_candidate_index=row.get("chosen_candidate_index"),
        executed_sql=row.get("executed_sql"),
        ast_classification=row.get("ast_classification"),
        execution_engine=row.get("execution_engine", "duckdb"),
        execution_status=row.get("execution_status"),
        retries=row.get("retries", 0),
        row_count=row.get("row_count"),
        elapsed_ms=row.get("elapsed_ms"),
        cost_cents=row.get("cost_cents"),
        clarification_emitted=row.get("clarification_emitted", False),
        clarification_json=row.get("clarification_json"),
        pii_findings_json=row.get("pii_findings_json"),
        error_json=row.get("error_json"),
        model_grounding=row.get("model_grounding"),
        model_generation=row.get("model_generation"),
        model_critic=row.get("model_critic"),
        model_explainer=row.get("model_explainer"),
        created_at=row["created_at"],
        finalised_at=row.get("finalised_at"),
    )


def _is_url_still_valid(ttl_expires_at: Any) -> bool:
    """Return True if the result row's TTL is in the future (or None)."""
    if ttl_expires_at is None:
        return True
    from datetime import UTC
    from datetime import datetime as _dt

    if isinstance(ttl_expires_at, _dt):
        try:
            return ttl_expires_at > _dt.now(UTC if ttl_expires_at.tzinfo else None)
        except Exception:  # noqa: BLE001
            return False
    return True


__all__ = ["QueriesController"]
