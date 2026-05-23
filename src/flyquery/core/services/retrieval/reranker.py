# Copyright 2026 Firefly Software Solutions Inc
"""Cross-encoder reranker with graceful fallback to no-op.

``CrossEncoderReranker`` lazy-imports ``sentence-transformers``.
If the package is absent (or the model fails to load), ``build_reranker``
silently returns a ``NoopReranker`` instead.
"""

from __future__ import annotations

from typing import Any, Protocol

from flyquery.core.services.retrieval.search_index import Hit


class Reranker(Protocol):
    """Protocol for a reranking step in the retrieval pipeline."""

    async def rerank(self, query: str, hits: list[Hit], top_n: int) -> list[Hit]:
        """Return at most *top_n* hits re-ordered by cross-encoder score."""
        ...


class NoopReranker:
    """Identity reranker that preserves the original order."""

    async def rerank(self, query: str, hits: list[Hit], top_n: int) -> list[Hit]:  # noqa: ARG002
        """Return the first ``top_n`` hits unchanged.

        :param query: NL query string (unused)
        :param hits: candidate hits from the retriever
        :param top_n: how many to return
        :return: first ``top_n`` elements of ``hits``
        """
        return hits[:top_n]


class CrossEncoderReranker:
    """Reranker backed by a sentence-transformers CrossEncoder model.

    The model is loaded lazily in ``__init__``; if the import or model
    load fails the caller should use ``build_reranker`` which catches
    the error and falls back to ``NoopReranker``.
    """

    def __init__(self, model_name: str) -> None:
        from sentence_transformers import CrossEncoder  # type: ignore[import-untyped]

        self._model = CrossEncoder(model_name)

    async def rerank(self, query: str, hits: list[Hit], top_n: int) -> list[Hit]:
        """Score (query, passage) pairs and return top-n by score.

        :param query: NL query string
        :param hits: candidate hits to rerank
        :param top_n: how many top results to return
        :return: hits sorted by cross-encoder score, descending
        """
        if not hits:
            return []
        pairs = [(query, h.text) for h in hits]
        scores = self._model.predict(pairs)
        order = sorted(range(len(hits)), key=lambda i: float(scores[i]), reverse=True)
        return [hits[i] for i in order[:top_n]]


def build_reranker(settings: Any) -> NoopReranker | CrossEncoderReranker:
    """Factory: return a ``CrossEncoderReranker`` when possible.

    Falls back to ``NoopReranker`` when:
    - ``settings.reranker_model`` is empty / falsy
    - ``sentence-transformers`` is not installed
    - The specified model cannot be loaded (network error, etc.)

    :param settings: ``FlyquerySettings`` instance
    :return: a ready-to-use reranker
    """
    model_name = getattr(settings, "reranker_model", "") or ""
    if not model_name:
        return NoopReranker()
    try:
        return CrossEncoderReranker(model_name)
    except Exception:  # noqa: BLE001
        return NoopReranker()
