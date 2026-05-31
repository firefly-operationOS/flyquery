# Copyright 2026 Firefly Software Solutions Inc
"""Generic embedder backed by fireflyframework-agentic's provider registry.

This module delegates the actual embedding call to one of the eight
provider adapters shipped by ``fireflyframework_agentic.embeddings``,
so a local Ollama, an air-gapped Bedrock deployment, or a regulated
customer running Azure OpenAI are all supported through one surface:

* ``ollama``  -- local, default for tests + dev
* ``openai``  -- text-embedding-3-{small,large}
* ``cohere``  -- embed-english-v3.0
* ``voyage``  -- voyage-3, voyage-large-2
* ``azure``   -- Azure OpenAI deployments
* ``google``  -- Vertex AI text-embedding models
* ``mistral`` -- mistral-embed
* ``bedrock`` -- AWS Titan / Cohere on Bedrock
* ``null``    -- explicit "no embeddings" mode for BM25-only retrieval

Vector padding
--------------
The schema column is ``vector(<settings.embedding_dimensions>)`` (default
1536, matching the lock-step canon migration). Some providers emit
smaller vectors -- Ollama ``nomic-embed-text`` is 768, Cohere v3 is
1024. The persistence helper zero-pads them to the configured column
dim. Cosine similarity ranking is preserved because zero coordinates
contribute zero to both the dot product and the L2 norms.

Async + sync surface
--------------------
The public ``Embedder`` protocol is async-first to match the rest of
the codebase. A synchronous mirror (``embed_sync`` / ``embed_batch_sync``)
is exposed for CLI scripts and unit tests; it just wraps
``asyncio.run`` and is safe to call from any thread that doesn't
already have a running event loop.
"""

from __future__ import annotations

import asyncio
import logging
import os
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from flyquery.config import FlyquerySettings

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------
# Public Protocol
# ----------------------------------------------------------------------


class Embedder(Protocol):
    """Async embedder contract used by the embed stage + grounding agent."""

    @property
    def model(self) -> str: ...

    @property
    def dimensions(self) -> int: ...

    async def embed(self, text: str) -> list[float] | None: ...

    async def embed_batch(self, texts: list[str]) -> list[list[float] | None]: ...

    def embed_sync(self, text: str) -> list[float] | None: ...

    def embed_batch_sync(self, texts: list[str]) -> list[list[float] | None]: ...


# ----------------------------------------------------------------------
# Null embedder -- always returns None
# ----------------------------------------------------------------------


class NullEmbedder:
    """Embedder that always returns ``None``.

    Selected when ``embedding_provider="null"`` OR when the provider's
    API key / endpoint isn't reachable. Lets ingestion still complete
    and the schema KB is queryable -- retrieval just falls back to
    BM25 over ``content_tsv``.
    """

    def __init__(self, dimensions: int = 1536, model: str = "null") -> None:
        self._dim = dimensions
        self._model = model

    @property
    def model(self) -> str:
        return self._model

    @property
    def dimensions(self) -> int:
        return self._dim

    async def embed(self, text: str) -> list[float] | None:  # noqa: ARG002
        return None

    async def embed_batch(self, texts: list[str]) -> list[list[float] | None]:
        return [None] * len(texts)

    def embed_sync(self, text: str) -> list[float] | None:
        return None

    def embed_batch_sync(self, texts: list[str]) -> list[list[float] | None]:
        return [None] * len(texts)


# ----------------------------------------------------------------------
# fireflyframework-agentic-backed embedder
# ----------------------------------------------------------------------


class FireflyEmbedder:
    """Wraps a ``fireflyframework_agentic.embeddings.BaseEmbedder``.

    Adapts the ff-agentic ``async embed/embed_one`` surface to flyquery's
    ``embed/embed_batch`` Protocol, zero-pads to the configured column
    dimension, and exposes sync helpers for non-async callers.
    """

    def __init__(
        self,
        *,
        inner: Any,  # fireflyframework_agentic.embeddings.BaseEmbedder
        target_dim: int,
        native_dim: int,
    ) -> None:
        self._inner = inner
        self._target_dim = target_dim
        self._native_dim = native_dim

    @property
    def model(self) -> str:
        return self._inner.model

    @property
    def dimensions(self) -> int:
        return self._target_dim

    def _pad(self, vec: list[float]) -> list[float]:
        """Zero-pad or truncate ``vec`` to the column dim.

        Producers return native-dimensional vectors; the column is
        fixed-size. Pad with zeros when smaller (cosine-preserving),
        truncate when larger (information loss but rare).
        """
        n = len(vec)
        if n == self._target_dim:
            return vec
        if n < self._target_dim:
            return list(vec) + [0.0] * (self._target_dim - n)
        return list(vec[: self._target_dim])

    async def embed(self, text: str) -> list[float] | None:
        try:
            vec = await self._inner.embed_one(text)
        except Exception as exc:  # noqa: BLE001
            logger.warning("embedder=%s embed_one failed: %s", self._inner.model, exc)
            return None
        return self._pad(vec)

    async def embed_batch(self, texts: list[str]) -> list[list[float] | None]:
        if not texts:
            return []
        try:
            result = await self._inner.embed(texts)
        except Exception as exc:  # noqa: BLE001
            logger.warning("embedder=%s embed batch failed: %s", self._inner.model, exc)
            return [None] * len(texts)
        return [self._pad(v) for v in result.embeddings]

    def embed_sync(self, text: str) -> list[float] | None:
        return asyncio.run(self.embed(text))

    def embed_batch_sync(self, texts: list[str]) -> list[list[float] | None]:
        return asyncio.run(self.embed_batch(texts))


# ----------------------------------------------------------------------
# Factory
# ----------------------------------------------------------------------


def build_embedder(settings: FlyquerySettings) -> Embedder:
    """Build the configured embedder, with a Null fallback on any error.

    The factory inspects ``settings.embedding_provider`` and pulls the
    matching adapter from ``fireflyframework_agentic.embeddings.providers``.
    A missing API key / unreachable Ollama is logged + downgraded to
    ``NullEmbedder`` so ingestion still completes.
    """
    provider = (settings.embedding_provider or "null").lower()
    target_dim = int(settings.embedding_dimensions)
    native_dim = int(getattr(settings, "embedding_native_dim", target_dim))
    model = settings.embedding_model

    if provider == "null":
        return NullEmbedder(dimensions=target_dim, model="null")

    try:
        inner = _construct_inner(provider, model, native_dim, settings)
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "embedder provider=%s model=%s unavailable (%s) -- falling back to NullEmbedder. "
            "Retrieval will use BM25 over content_tsv only.",
            provider,
            model,
            exc,
        )
        return NullEmbedder(dimensions=target_dim, model=f"{provider}:{model}:disabled")

    return FireflyEmbedder(inner=inner, target_dim=target_dim, native_dim=native_dim)


def _construct_inner(
    provider: str,
    model: str,
    native_dim: int,
    settings: FlyquerySettings,
) -> Any:
    """Instantiate the right ``fireflyframework_agentic.embeddings`` adapter."""
    base_url = settings.embedding_base_url

    if provider == "ollama":
        from fireflyframework_agentic.embeddings.providers.ollama import OllamaEmbedder

        return OllamaEmbedder(
            model=model,
            dimensions=native_dim,
            base_url=base_url or "http://localhost:11434",
        )
    if provider == "openai":
        from fireflyframework_agentic.embeddings.providers.openai import OpenAIEmbedder

        if not os.environ.get("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY not set")
        return OpenAIEmbedder(model=model, dimensions=native_dim)
    if provider == "cohere":
        from fireflyframework_agentic.embeddings.providers.cohere import CohereEmbedder

        if not os.environ.get("COHERE_API_KEY"):
            raise RuntimeError("COHERE_API_KEY not set")
        return CohereEmbedder(model=model, dimensions=native_dim)
    if provider == "voyage":
        from fireflyframework_agentic.embeddings.providers.voyage import VoyageEmbedder

        if not os.environ.get("VOYAGE_API_KEY"):
            raise RuntimeError("VOYAGE_API_KEY not set")
        return VoyageEmbedder(model=model, dimensions=native_dim)
    if provider == "mistral":
        from fireflyframework_agentic.embeddings.providers.mistral import MistralEmbedder

        if not os.environ.get("MISTRAL_API_KEY"):
            raise RuntimeError("MISTRAL_API_KEY not set")
        return MistralEmbedder(model=model, dimensions=native_dim)
    if provider == "azure":
        from fireflyframework_agentic.embeddings.providers.azure import AzureEmbedder

        endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
        if not endpoint:
            raise RuntimeError("AZURE_OPENAI_ENDPOINT not set")
        return AzureEmbedder(
            model=model,
            dimensions=native_dim,
            azure_endpoint=endpoint,
            api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
        )
    if provider == "google":
        from fireflyframework_agentic.embeddings.providers.google import GoogleEmbedder

        return GoogleEmbedder(model=model, dimensions=native_dim)
    if provider == "bedrock":
        from fireflyframework_agentic.embeddings.providers.bedrock import BedrockEmbedder

        return BedrockEmbedder(model=model, dimensions=native_dim)
    raise ValueError(f"Unknown embedding_provider={provider!r}")
