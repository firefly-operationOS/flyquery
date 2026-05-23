# Copyright 2026 Firefly Software Solutions Inc
"""Embedder protocol + OpenAI implementation.

The ``OpenAiEmbedder`` gracefully returns ``None`` when no
``OPENAI_API_KEY`` is set — retrieval degrades to BM25-only.
"""

from __future__ import annotations

import os
from typing import Protocol


class Embedder(Protocol):
    """Protocol for single / batch embedding operations."""

    async def embed(self, text: str) -> list[float] | None:
        """Return an embedding vector, or None on unavailability."""
        ...

    async def embed_batch(self, texts: list[str]) -> list[list[float] | None]:
        """Return a list of embedding vectors (None entries on error)."""
        ...


class OpenAiEmbedder:
    """Wraps OpenAI ``text-embedding-3-small``.

    Returns ``None`` from all embed methods when ``OPENAI_API_KEY`` is
    absent from the environment — callers treat None as "no vector
    available" and fall back to BM25-only retrieval.
    """

    def __init__(self, model: str = "text-embedding-3-small", dim: int = 1536) -> None:
        self._model = model
        self._dim = dim
        self._client = None
        if os.environ.get("OPENAI_API_KEY"):
            try:
                from openai import AsyncOpenAI  # type: ignore[import-untyped]

                self._client = AsyncOpenAI()
            except ImportError:
                pass

    async def embed(self, text: str) -> list[float] | None:
        """Embed a single text string.

        :param text: input text to embed
        :return: 1536-dim vector or None if unavailable
        """
        if not self._client:
            return None
        resp = await self._client.embeddings.create(model=self._model, input=text)
        return resp.data[0].embedding  # type: ignore[no-any-return]

    async def embed_batch(self, texts: list[str]) -> list[list[float] | None]:
        """Embed a batch of texts.

        :param texts: list of input strings
        :return: list of vectors (None entries when unavailable)
        """
        if not self._client or not texts:
            return [None] * len(texts)
        resp = await self._client.embeddings.create(model=self._model, input=texts)
        return [d.embedding for d in resp.data]  # type: ignore[return-value]
