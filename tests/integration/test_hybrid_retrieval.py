# Copyright 2026 Firefly Software Solutions Inc
"""Integration tests for HybridRetriever + SearchIndex."""

from __future__ import annotations

import uuid

import pytest
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine


class _FixedEmbedder:
    """Deterministic embedder that returns a fixed 1536-dim vector."""

    async def embed(self, text: str) -> list[float]:  # noqa: ARG002
        return [0.1] * 1536

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [[0.1] * 1536 for _ in texts]


class _NullEmbedder:
    """Embedder that always returns None (simulates missing API key)."""

    async def embed(self, text: str) -> None:  # noqa: ARG002
        return None

    async def embed_batch(self, texts: list[str]) -> list[None]:
        return [None] * len(texts)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_bm25_only_retrieval(started_app: None) -> None:  # noqa: ARG001
    """BM25-only branch returns hits when schema objects exist."""
    import os

    from sqlalchemy.ext.asyncio import async_sessionmaker

    from flyquery.core.services.retrieval.hybrid_retriever import HybridRetriever
    from flyquery.core.services.retrieval.search_index import SearchIndex

    db_url = os.environ["FLYQUERY_DATABASE_URL"]
    engine = create_async_engine(db_url)
    factory = async_sessionmaker(engine, expire_on_commit=False)

    # --- seed workspace + dataset + table + schema_object ---
    async with factory() as s, s.begin():
        tenant = "ten-hybrid"
        ws_id = uuid.uuid4()
        ds_id = uuid.uuid4()
        tbl_id = uuid.uuid4()
        obj_id = uuid.uuid4()

        await s.execute(
            sa.text(
                "INSERT INTO flyquery_workspaces (id, tenant_id, slug, name, status) "
                "VALUES (:id, :t, :slug, :name, 'ACTIVE')"
            ),
            {"id": ws_id, "t": tenant, "slug": f"hw-{ws_id}", "name": "Hybrid WS"},
        )
        await s.execute(
            sa.text(
                "INSERT INTO flyquery_datasets (id, tenant_id, workspace_id, name, status, drift_policy) "
                "VALUES (:id, :t, :ws, :name, 'ACTIVE', 'WARN')"
            ),
            {"id": ds_id, "t": tenant, "ws": ws_id, "name": "Hybrid DS"},
        )
        await s.execute(
            sa.text(
                "INSERT INTO flyquery_tables (id, tenant_id, workspace_id, dataset_id, name, qualified_name, kind, status) "
                "VALUES (:id, :t, :ws, :ds, 'orders', 'orders', 'UPLOADED', 'ACTIVE')"
            ),
            {"id": tbl_id, "t": tenant, "ws": ws_id, "ds": ds_id},
        )
        await s.execute(
            sa.text(
                """
                INSERT INTO flyquery_schema_objects
                    (id, tenant_id, workspace_id, table_id, qualified_name, column_name,
                     object_kind, data_type, is_active,
                     content_tsv)
                VALUES
                    (:id, :t, :ws, :tbl, 'orders.total', 'total',
                     'COLUMN', 'DECIMAL', true,
                     to_tsvector('english', 'revenue total money sales'))
                """
            ),
            {"id": obj_id, "t": tenant, "ws": ws_id, "tbl": tbl_id},
        )

    async with factory() as session:
        idx = SearchIndex(session)
        retriever = HybridRetriever(idx, _NullEmbedder())
        bundle = await retriever.retrieve(
            "total revenue",
            dataset_id=ds_id,
            workspace_id=ws_id,
        )

    assert isinstance(bundle, dict)
    assert "schema_objects" in bundle
    # At least the seeded column should appear (BM25 matches "total revenue")
    assert len(bundle["schema_objects"]) >= 1
    await engine.dispose()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_hybrid_retrieval_with_embedder(started_app: None) -> None:  # noqa: ARG001
    """Hybrid branch (BM25 + vector) merges results via RRF."""
    import os

    from sqlalchemy.ext.asyncio import async_sessionmaker

    from flyquery.core.services.retrieval.hybrid_retriever import HybridRetriever
    from flyquery.core.services.retrieval.search_index import SearchIndex

    db_url = os.environ["FLYQUERY_DATABASE_URL"]
    engine = create_async_engine(db_url)
    factory = async_sessionmaker(engine, expire_on_commit=False)

    tenant = "ten-hybrid2"
    ws_id = uuid.uuid4()
    ds_id = uuid.uuid4()
    tbl_id = uuid.uuid4()

    async with factory() as s, s.begin():
        await s.execute(
            sa.text(
                "INSERT INTO flyquery_workspaces (id, tenant_id, slug, name, status) "
                "VALUES (:id, :t, :slug, :name, 'ACTIVE')"
            ),
            {"id": ws_id, "t": tenant, "slug": f"hv-{ws_id}", "name": "HybVec WS"},
        )
        await s.execute(
            sa.text(
                "INSERT INTO flyquery_datasets (id, tenant_id, workspace_id, name, status, drift_policy) "
                "VALUES (:id, :t, :ws, :name, 'ACTIVE', 'WARN')"
            ),
            {"id": ds_id, "t": tenant, "ws": ws_id, "name": "HybVec DS"},
        )
        await s.execute(
            sa.text(
                "INSERT INTO flyquery_tables (id, tenant_id, workspace_id, dataset_id, name, qualified_name, kind, status) "
                "VALUES (:id, :t, :ws, :ds, 'sales', 'sales', 'UPLOADED', 'ACTIVE')"
            ),
            {"id": tbl_id, "t": tenant, "ws": ws_id, "ds": ds_id},
        )
        # Insert column with embedding
        vec = str([0.1] * 1536)
        await s.execute(
            sa.text(
                """
                INSERT INTO flyquery_schema_objects
                    (id, tenant_id, workspace_id, table_id, qualified_name, column_name,
                     object_kind, data_type, is_active,
                     content_tsv, embedding)
                VALUES
                    (gen_random_uuid(), :t, :ws, :tbl, 'sales.amount', 'amount',
                     'COLUMN', 'DECIMAL', true,
                     to_tsvector('english', 'amount money total'),
                     :emb::vector)
                """
            ),
            {"t": tenant, "ws": ws_id, "tbl": tbl_id, "emb": vec},
        )

    async with factory() as session:
        idx = SearchIndex(session)
        retriever = HybridRetriever(idx, _FixedEmbedder())
        bundle = await retriever.retrieve(
            "total amount",
            dataset_id=ds_id,
            workspace_id=ws_id,
        )

    assert len(bundle["schema_objects"]) >= 1
    await engine.dispose()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_glossary_terms_appear_in_bundle(started_app: None) -> None:  # noqa: ARG001
    """Glossary terms seeded in the workspace appear in the retrieved bundle."""
    import os

    from sqlalchemy.ext.asyncio import async_sessionmaker

    from flyquery.core.services.retrieval.hybrid_retriever import HybridRetriever
    from flyquery.core.services.retrieval.search_index import SearchIndex

    db_url = os.environ["FLYQUERY_DATABASE_URL"]
    engine = create_async_engine(db_url)
    factory = async_sessionmaker(engine, expire_on_commit=False)

    tenant = "ten-glossary"
    ws_id = uuid.uuid4()
    ds_id = uuid.uuid4()
    tbl_id = uuid.uuid4()

    async with factory() as s, s.begin():
        await s.execute(
            sa.text(
                "INSERT INTO flyquery_workspaces (id, tenant_id, slug, name, status) "
                "VALUES (:id, :t, :slug, :name, 'ACTIVE')"
            ),
            {"id": ws_id, "t": tenant, "slug": f"gl-{ws_id}", "name": "Glossary WS"},
        )
        await s.execute(
            sa.text(
                "INSERT INTO flyquery_datasets (id, tenant_id, workspace_id, name, status, drift_policy) "
                "VALUES (:id, :t, :ws, :name, 'ACTIVE', 'WARN')"
            ),
            {"id": ds_id, "t": tenant, "ws": ws_id, "name": "Glossary DS"},
        )
        await s.execute(
            sa.text(
                "INSERT INTO flyquery_tables (id, tenant_id, workspace_id, dataset_id, name, qualified_name, kind, status) "
                "VALUES (:id, :t, :ws, :ds, 'orders', 'orders', 'UPLOADED', 'ACTIVE')"
            ),
            {"id": tbl_id, "t": tenant, "ws": ws_id, "ds": ds_id},
        )
        # Seed a schema object so schema retrieval does not error
        await s.execute(
            sa.text(
                """
                INSERT INTO flyquery_schema_objects
                    (id, tenant_id, workspace_id, table_id, qualified_name, column_name,
                     object_kind, data_type, is_active, content_tsv)
                VALUES
                    (gen_random_uuid(), :t, :ws, :tbl, 'orders.revenue', 'revenue',
                     'COLUMN', 'DECIMAL', true,
                     to_tsvector('english', 'revenue income earnings'))
                """
            ),
            {"t": tenant, "ws": ws_id, "tbl": tbl_id},
        )
        # Seed a glossary term
        await s.execute(
            sa.text(
                """
                INSERT INTO flyquery_glossary_terms
                    (id, tenant_id, workspace_id, term, definition,
                     synonyms_json, tags_json, related_columns_json, related_metrics_json)
                VALUES
                    (gen_random_uuid(), :t, :ws, 'revenue',
                     'Total monetary value of all sales in a given period.',
                     '["income","earnings","sales"]'::jsonb, '[]'::jsonb,
                     '[]'::jsonb, '[]'::jsonb)
                """
            ),
            {"t": tenant, "ws": ws_id},
        )

    async with factory() as session:
        idx = SearchIndex(session)
        retriever = HybridRetriever(idx, _NullEmbedder())
        bundle = await retriever.retrieve(
            "total revenue",
            dataset_id=ds_id,
            workspace_id=ws_id,
        )

    assert "glossary" in bundle
    assert len(bundle["glossary"]) >= 1
    terms = [h.metadata["term"] for h in bundle["glossary"]]
    assert "revenue" in terms
    await engine.dispose()
