# Copyright 2026 Firefly Software Solutions Inc
"""HybridRetriever: BM25 + pgvector with Reciprocal Rank Fusion (RRF).

Fuses rankings from multiple retrieval strategies into a single ranked
list of ``Hit`` objects. When no embedder is available, degrades
gracefully to BM25-only retrieval.
"""

from __future__ import annotations

import uuid
from collections import defaultdict
from typing import Any

from flyquery.core.services.retrieval.search_index import Hit, SearchIndex


def _rrf(rankings: list[list[Hit]], k: int = 60) -> list[Hit]:
    """Reciprocal Rank Fusion over multiple ranked lists.

    :param rankings: list of ranked hit lists (each from a different retriever)
    :param k: RRF constant (default 60, as per Cormack et al.)
    :return: single fused ranking, highest-score first
    """
    scores: dict[tuple[str, str], float] = defaultdict(float)
    by_key: dict[tuple[str, str], Hit] = {}
    for rank in rankings:
        for i, h in enumerate(rank):
            key = (h.source_kind, str(h.id))
            scores[key] += 1.0 / (k + i + 1)
            by_key[key] = h
    return sorted(by_key.values(), key=lambda h: scores[(h.source_kind, str(h.id))], reverse=True)


class HybridRetriever:
    """Retriever that fuses BM25 and pgvector results with RRF.

    When the embedder returns ``None`` (no API key), the vector branch is
    skipped and results come from BM25 only.
    """

    def __init__(self, index: SearchIndex, embedder: Any, rrf_k: int = 60) -> None:
        self._index = index
        self._embedder = embedder
        self._rrf_k = rrf_k

    async def retrieve(
        self,
        query: str,
        *,
        dataset_id: uuid.UUID,
        workspace_id: uuid.UUID,
        top_k_schema: int = 12,
        top_k_examples: int = 5,
        top_k_metrics: int = 8,
    ) -> dict[str, list[Hit]]:
        """Run full hybrid retrieval and return a bundle of hit lists.

        :param query: natural-language question
        :param dataset_id: dataset scope for schema objects / metrics
        :param workspace_id: workspace scope for examples / glossary
        :param top_k_schema: how many schema objects to return after fusion
        :param top_k_examples: how many examples to return
        :param top_k_metrics: how many published metrics to return
        :return: dict with keys schema_objects, examples, metrics, glossary, relations
        """
        bm25_schema = await self._index.bm25_schema_objects(
            query, dataset_id, limit=top_k_schema * 3
        )

        query_embedding: list[float] | None = None
        if self._embedder is not None:
            query_embedding = await self._embedder.embed(query)

        vector_schema: list[Hit] = []
        if query_embedding is not None:
            vector_schema = await self._index.vector_schema_objects(
                query_embedding, dataset_id, limit=top_k_schema * 3
            )

        examples = await self._index.approved_examples(
            query,
            query_embedding,
            workspace_id,
            dataset_id,
            limit=top_k_examples * 2,
        )
        metrics = await self._index.published_metrics(query, dataset_id, limit=top_k_metrics * 2)
        glossary = await self._index.glossary_hits(query, workspace_id, limit=8)
        relations = await self._index.approved_relations(dataset_id)

        schema_objects = _rrf([bm25_schema, vector_schema], k=self._rrf_k)[:top_k_schema]

        return {
            "schema_objects": schema_objects,
            "examples": examples[:top_k_examples],
            "metrics": metrics[:top_k_metrics],
            "glossary": glossary,
            "relations": relations,
        }
