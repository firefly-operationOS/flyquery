# Copyright 2026 Firefly Software Solutions Inc
"""DerivedTableService — materialise a SELECT as a DERIVED table.

Flow:
1. AST classify + scope check (must be SELECT).
2. Run the SELECT via DuckDB against the dataset's current snapshots.
3. Write result as Parquet under ``derived/{table_id}/v1.parquet`` via ObjectStore.
4. Insert ``flyquery_tables`` row (kind=DERIVED, current_snapshot_id=NULL initially).
5. Insert ``flyquery_schema_snapshots`` row (status=PARTIAL initially).
6. Insert ``flyquery_schema_objects`` rows for the table (kind=TABLE) + each column (kind=COLUMN).
7. Atomic update: snapshot.status=READY + tables.current_snapshot_id = new snapshot.
8. Return the new table_id.

DML on DERIVED tables (INSERT/UPDATE/DELETE) is handled by
:class:`DuckDBExecutor` via copy-on-write Parquet versioning.
"""

from __future__ import annotations

import hashlib
import io
import logging
import uuid

import sqlalchemy as sa
from pyfly.container import service
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from flyquery.config import FlyquerySettings
from flyquery.core.services.execution.ast_classifier import AstClassifier
from flyquery.core.services.execution.duckdb_executor import (
    DuckDBExecutor,
    ExecutionError,
    ExecutionResult,
)
from flyquery.core.services.execution.scope_guard import ScopeGuard
from flyquery.core.services.execution.table_resolver import TableResolver
from flyquery.core.services.storage.object_store import ObjectStore
from flyquery.web.conventions import FireflyHTTPException

logger = logging.getLogger(__name__)

_DERIVE_SCOPES: set[str] = {"flyquery.query:read", "flyquery.sql:execute", "*"}


class DeriveTableError(FireflyHTTPException):
    status = 422
    code = "derive_table_error"
    title = "Failed to derive table"


class DeriveTableForbidden(FireflyHTTPException):
    status = 403
    code = "derive_table_forbidden"
    title = "Only SELECT statements are allowed for /tables:derive"


@service
class DerivedTableService:
    """Materialise a SELECT query as a DERIVED table in flyquery_tables.

    :param session: ``async_sessionmaker`` injected by pyfly's DI container
    :param object_store: blob store for Parquet output
    :param settings: application settings (object_store_base, etc.)
    """

    def __init__(
        self,
        session: async_sessionmaker[AsyncSession],
        object_store: ObjectStore,
        settings: FlyquerySettings,
    ) -> None:
        self._factory = session
        self._store = object_store
        self._settings = settings
        self._ast_classifier = AstClassifier()
        self._scope_guard = ScopeGuard()
        self._executor = DuckDBExecutor(settings)

    async def derive(
        self,
        *,
        tenant_id: str,
        workspace_id: uuid.UUID,
        dataset_id: uuid.UUID,
        name: str,
        sql: str,
        actor: str,
    ) -> uuid.UUID:
        """Materialise the SELECT result as a new DERIVED table.

        :param tenant_id: tenant identifier
        :param workspace_id: workspace UUID
        :param dataset_id: dataset to scope the table lookup and the new table
        :param name: human-readable name for the derived table (unique per dataset)
        :param sql: SELECT statement to materialise (no DML/DDL)
        :param actor: actor triggering the derivation
        :return: UUID of the newly created flyquery_tables row
        :raises DeriveTableForbidden: when the SQL is not a SELECT
        :raises DeriveTableError: when execution fails
        """
        # ------------------------------------------------------------------
        # 1. AST classify + scope check (SELECT only)
        # ------------------------------------------------------------------
        ast = self._ast_classifier.classify(sql)
        if ast.classification != "SELECT":
            raise DeriveTableForbidden(f"/tables:derive only accepts SELECT; got {ast.classification!r}")

        # ------------------------------------------------------------------
        # 2. Resolve parquet paths for the source tables
        # ------------------------------------------------------------------
        async with self._factory() as db_session:
            resolver = TableResolver(session=db_session, settings=self._settings)
            attached = await resolver.resolve(dataset_id, list(ast.table_refs))

        # ------------------------------------------------------------------
        # 3. Execute the SELECT via DuckDB
        # ------------------------------------------------------------------
        result = await self._executor.execute(sql, attached)
        if isinstance(result, ExecutionError):
            raise DeriveTableError(f"Execution failed: {result.message}")

        assert isinstance(result, ExecutionResult)

        # ------------------------------------------------------------------
        # 4. Write Parquet to object store
        # ------------------------------------------------------------------
        table_id = uuid.uuid4()
        object_key = f"flyquery/{tenant_id}/{workspace_id}/{dataset_id}/derived/{table_id}/v1.parquet"
        parquet_bytes = _rows_to_parquet(result.rows, result.columns)
        await self._store.put(object_key, parquet_bytes, content_type="application/x-parquet")

        # ------------------------------------------------------------------
        # 5–7. Insert DB rows atomically
        # ------------------------------------------------------------------
        snapshot_id = await self._persist_derived_table(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            dataset_id=dataset_id,
            table_id=table_id,
            name=name,
            sql=sql,
            actor=actor,
            object_key=object_key,
            parquet_byte_size=len(parquet_bytes),
            columns=result.columns,
            n_rows=result.row_count,
        )

        logger.info(
            "derived table created: table_id=%s name=%r snapshot_id=%s rows=%d",
            table_id,
            name,
            snapshot_id,
            result.row_count,
        )
        return table_id

    async def _persist_derived_table(
        self,
        *,
        tenant_id: str,
        workspace_id: uuid.UUID,
        dataset_id: uuid.UUID,
        table_id: uuid.UUID,
        name: str,
        sql: str,
        actor: str,
        object_key: str,
        parquet_byte_size: int,
        columns: list[str],
        n_rows: int,
    ) -> uuid.UUID:
        """Insert flyquery_tables + flyquery_schema_snapshots + schema_objects atomically.

        :return: the new snapshot_id
        """
        qualified_name = name
        snapshot_hash = hashlib.sha256(sql.encode()).hexdigest()[:16]
        snapshot_id = uuid.uuid4()

        async with self._factory() as s, s.begin():
            # Step 4 — flyquery_tables row (kind=DERIVED)
            await s.execute(
                sa.text("""
                    INSERT INTO flyquery_tables
                        (id, tenant_id, workspace_id, dataset_id, name, qualified_name,
                         kind, is_active)
                    VALUES
                        (:id, :tenant_id, :workspace_id, :dataset_id, :name, :qname,
                         'DERIVED', true)
                """),
                {
                    "id": table_id,
                    "tenant_id": tenant_id,
                    "workspace_id": workspace_id,
                    "dataset_id": dataset_id,
                    "name": name,
                    "qname": qualified_name,
                },
            )

            # Step 5 — flyquery_schema_snapshots (status=PARTIAL first)
            await s.execute(
                sa.text("""
                    INSERT INTO flyquery_schema_snapshots
                        (id, tenant_id, workspace_id, dataset_id, table_id,
                         snapshot_hash, n_columns, n_rows_actual,
                         parquet_object_key, parquet_byte_size,
                         status, triggered_by, created_by)
                    VALUES
                        (:id, :tenant_id, :workspace_id, :dataset_id, :table_id,
                         :snapshot_hash, :n_columns, :n_rows,
                         :object_key, :byte_size,
                         'PARTIAL', 'USER', :actor)
                """),
                {
                    "id": snapshot_id,
                    "tenant_id": tenant_id,
                    "workspace_id": workspace_id,
                    "dataset_id": dataset_id,
                    "table_id": table_id,
                    "snapshot_hash": snapshot_hash,
                    "n_columns": len(columns),
                    "n_rows": n_rows,
                    "object_key": object_key,
                    "byte_size": parquet_byte_size,
                    "actor": actor,
                },
            )

            # Step 6 — flyquery_schema_objects: TABLE row + COLUMN rows
            table_qname = qualified_name
            table_source_hash = snapshot_hash

            await s.execute(
                sa.text("""
                    INSERT INTO flyquery_schema_objects
                        (tenant_id, workspace_id, table_id, snapshot_id,
                         kind, qualified_name, is_active, source_hash)
                    VALUES
                        (:tenant_id, :workspace_id, :table_id, :snapshot_id,
                         'TABLE', :qname, true, :source_hash)
                """),
                {
                    "tenant_id": tenant_id,
                    "workspace_id": workspace_id,
                    "table_id": table_id,
                    "snapshot_id": snapshot_id,
                    "qname": table_qname,
                    "source_hash": table_source_hash,
                },
            )

            for col_name in columns:
                col_qname = f"{table_qname}.{col_name}"
                col_hash = hashlib.sha256(col_qname.encode()).hexdigest()[:16]
                await s.execute(
                    sa.text("""
                        INSERT INTO flyquery_schema_objects
                            (tenant_id, workspace_id, table_id, snapshot_id,
                             kind, qualified_name, is_active, source_hash)
                        VALUES
                            (:tenant_id, :workspace_id, :table_id, :snapshot_id,
                             'COLUMN', :qname, true, :source_hash)
                    """),
                    {
                        "tenant_id": tenant_id,
                        "workspace_id": workspace_id,
                        "table_id": table_id,
                        "snapshot_id": snapshot_id,
                        "qname": col_qname,
                        "source_hash": col_hash,
                    },
                )

            # Step 7 — atomic flip: snapshot READY + tables.current_snapshot_id
            await s.execute(
                sa.text("UPDATE flyquery_schema_snapshots SET status='READY' WHERE id = :id"),
                {"id": snapshot_id},
            )
            await s.execute(
                sa.text(
                    "UPDATE flyquery_tables "
                    "SET current_snapshot_id = :sid, updated_at = now() "
                    "WHERE id = :tid"
                ),
                {"sid": snapshot_id, "tid": table_id},
            )

        return snapshot_id


def _rows_to_parquet(rows: list[dict], columns: list[str]) -> bytes:
    """Serialise rows to a snappy-compressed Parquet byte string.

    :param rows: list of row dicts from DuckDBExecutor
    :param columns: column name order
    :return: Parquet bytes
    """
    import pyarrow as pa
    import pyarrow.parquet as pq

    if rows:
        table = pa.Table.from_pylist(rows)
    else:
        schema = pa.schema([(c, pa.string()) for c in columns])
        table = pa.table({c: [] for c in columns}, schema=schema)

    buf = io.BytesIO()
    pq.write_table(table, buf, compression="snappy")
    return buf.getvalue()
