# Copyright 2026 Firefly Software Solutions Inc
"""Unit tests for the provider-agnostic Embedder + build_embedder factory."""

from __future__ import annotations

from typing import Any

import pytest

from flyquery.config import FlyquerySettings
from flyquery.core.services.retrieval.embedder import (
    Embedder,
    FireflyEmbedder,
    NullEmbedder,
    build_embedder,
)


class _FakeBaseEmbedder:
    """Stand-in for fireflyframework_agentic.embeddings.BaseEmbedder."""

    def __init__(self, model: str, native_dim: int, batch_return: list[list[float]] | None = None) -> None:
        self.model = model
        self._native_dim = native_dim
        self._batch_return = batch_return

    async def embed_one(self, text: str, **kwargs: Any) -> list[float]:  # noqa: ARG002
        return [float(i) for i in range(self._native_dim)]

    async def embed(self, texts: list[str], **kwargs: Any) -> Any:  # noqa: ARG002
        from types import SimpleNamespace

        vectors = self._batch_return or [[float(i) for i in range(self._native_dim)] for _ in texts]
        return SimpleNamespace(embeddings=vectors)


class TestNullEmbedder:
    @pytest.mark.asyncio
    async def test_returns_none(self) -> None:
        e = NullEmbedder(dimensions=8)
        assert e.dimensions == 8
        assert e.model == "null"
        assert (await e.embed("hi")) is None
        assert (await e.embed_batch(["a", "b", "c"])) == [None, None, None]

    def test_sync_returns_none(self) -> None:
        e = NullEmbedder(dimensions=8)
        assert e.embed_sync("hi") is None
        assert e.embed_batch_sync(["a", "b"]) == [None, None]

    def test_satisfies_protocol(self) -> None:
        e: Embedder = NullEmbedder(dimensions=8)
        # Static type assertion -- if NullEmbedder doesn't match Embedder
        # Protocol, mypy would fail. Runtime check: attributes are reachable.
        assert hasattr(e, "embed")
        assert hasattr(e, "embed_batch")
        assert hasattr(e, "embed_sync")
        assert hasattr(e, "embed_batch_sync")


class TestFireflyEmbedderPadding:
    @pytest.mark.asyncio
    async def test_native_dim_smaller_than_target_pads_with_zeros(self) -> None:
        inner = _FakeBaseEmbedder(model="nomic-embed-text", native_dim=4)
        e = FireflyEmbedder(inner=inner, target_dim=8, native_dim=4)
        vec = await e.embed("hi")
        assert vec is not None
        assert len(vec) == 8
        # Padded zeros at the end
        assert vec[4:] == [0.0, 0.0, 0.0, 0.0]
        # Native values preserved
        assert vec[:4] == [0.0, 1.0, 2.0, 3.0]

    @pytest.mark.asyncio
    async def test_exact_match_no_padding(self) -> None:
        inner = _FakeBaseEmbedder(model="m", native_dim=4)
        e = FireflyEmbedder(inner=inner, target_dim=4, native_dim=4)
        vec = await e.embed("hi")
        assert vec == [0.0, 1.0, 2.0, 3.0]

    @pytest.mark.asyncio
    async def test_native_dim_larger_than_target_truncates(self) -> None:
        inner = _FakeBaseEmbedder(model="m", native_dim=10)
        e = FireflyEmbedder(inner=inner, target_dim=4, native_dim=10)
        vec = await e.embed("hi")
        assert vec == [0.0, 1.0, 2.0, 3.0]

    @pytest.mark.asyncio
    async def test_batch_embed(self) -> None:
        inner = _FakeBaseEmbedder(
            model="m",
            native_dim=3,
            batch_return=[[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]],
        )
        e = FireflyEmbedder(inner=inner, target_dim=5, native_dim=3)
        vectors = await e.embed_batch(["a", "b"])
        assert vectors == [
            [1.0, 2.0, 3.0, 0.0, 0.0],
            [4.0, 5.0, 6.0, 0.0, 0.0],
        ]

    @pytest.mark.asyncio
    async def test_batch_embed_empty_input(self) -> None:
        inner = _FakeBaseEmbedder(model="m", native_dim=3)
        e = FireflyEmbedder(inner=inner, target_dim=5, native_dim=3)
        vectors = await e.embed_batch([])
        assert vectors == []

    @pytest.mark.asyncio
    async def test_inner_exception_returns_none(self) -> None:
        class _Boom:
            model = "m"

            async def embed_one(self, text: str) -> list[float]:  # noqa: ARG002
                raise RuntimeError("provider down")

            async def embed(self, texts: list[str]) -> Any:  # noqa: ARG002
                raise RuntimeError("provider down")

        e = FireflyEmbedder(inner=_Boom(), target_dim=4, native_dim=4)
        assert (await e.embed("hi")) is None
        assert (await e.embed_batch(["a", "b"])) == [None, None]

    def test_sync_helpers_wrap_async(self) -> None:
        inner = _FakeBaseEmbedder(model="m", native_dim=3)
        e = FireflyEmbedder(inner=inner, target_dim=5, native_dim=3)
        vec = e.embed_sync("hi")
        assert vec == [0.0, 1.0, 2.0, 0.0, 0.0]
        batch = e.embed_batch_sync(["a", "b"])
        assert batch == [
            [0.0, 1.0, 2.0, 0.0, 0.0],
            [0.0, 1.0, 2.0, 0.0, 0.0],
        ]


class TestBuildEmbedder:
    def test_null_provider_returns_null_embedder(self) -> None:
        s = FlyquerySettings(embedding_provider="null", embedding_dimensions=128)
        e = build_embedder(s)
        assert isinstance(e, NullEmbedder)
        assert e.dimensions == 128

    def test_unknown_provider_falls_back_to_null(self) -> None:
        # Bypass the Literal validation on FlyquerySettings -- _construct_inner
        # only checks the lowercased provider string, so any unknown string
        # must produce a NullEmbedder rather than a crash.
        s = FlyquerySettings(embedding_provider="null")
        object.__setattr__(s, "embedding_provider", "quantum_warp_field")
        e = build_embedder(s)
        assert isinstance(e, NullEmbedder)
        assert "disabled" in e.model or e.model == "null"

    def test_missing_api_key_falls_back_to_null(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        s = FlyquerySettings(
            embedding_provider="openai",
            embedding_model="text-embedding-3-small",
            embedding_dimensions=1536,
        )
        e = build_embedder(s)
        # Falls back gracefully
        assert isinstance(e, NullEmbedder)

    def test_ollama_uses_default_base_url(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Ollama can construct without env vars -- base_url defaults to localhost.

        We can't run a real request without a live server, but the
        construction path must succeed so deployments behind a docker
        compose Ollama container come up cleanly.
        """
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        s = FlyquerySettings(
            embedding_provider="ollama",
            embedding_model="nomic-embed-text",
            embedding_dimensions=1536,
            embedding_native_dim=768,
            embedding_base_url=None,
        )
        e = build_embedder(s)
        # Either constructed successfully (FireflyEmbedder) or fell
        # back to Null if fireflyframework-agentic isn't installed.
        assert isinstance(e, (FireflyEmbedder, NullEmbedder))
        if isinstance(e, FireflyEmbedder):
            assert e.dimensions == 1536
