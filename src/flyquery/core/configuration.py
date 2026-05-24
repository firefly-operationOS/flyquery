# Copyright 2026 Firefly Software Solutions Inc
"""DI configuration bean for flyquery."""

from __future__ import annotations

from pyfly.container import bean, configuration

from flyquery.config import FlyquerySettings
from flyquery.core.services.auth.agent_token_service import (
    AgentTokenService,
    RateLimiter,
    _RateLimiter,
)
from flyquery.core.services.auth.redis_rate_limiter import RedisRateLimiter
from flyquery.core.services.retrieval.embedder import Embedder, build_embedder
from flyquery.core.services.retrieval.reranker import NoopReranker, build_reranker
from flyquery.core.services.storage.object_store import ObjectStore
from flyquery.core.services.storage.object_store_factory import build_object_store
from flyquery.models.repositories.agent_token_repository import AgentTokenRepository
from flyquery.web.conventions.idempotency import (
    IdempotencyStore,
    InMemoryIdempotencyStore,
)
from flyquery.web.conventions.redis_idempotency import RedisIdempotencyStore


@configuration
class FlyqueryConfiguration:
    """Exposes :class:`FlyquerySettings` and core auth services to the pyfly DI container."""

    @bean
    def settings(self) -> FlyquerySettings:
        return FlyquerySettings()

    # ------------------------------------------------------------------
    # Auth services
    # ------------------------------------------------------------------

    @bean
    def rate_limiter(self, settings: FlyquerySettings) -> RateLimiter:
        """Per-token sliding-window rate limiter.

        Backend selection mirrors canon (memory: lock_step_conventions_canon_radar):
        * ``FLYQUERY_RATE_LIMIT_BACKEND=redis`` -- always Redis.
        * ``FLYQUERY_RATE_LIMIT_BACKEND=in_memory`` -- always in-memory.
        * unset / ``auto`` (default) -- Redis when ``redis_url`` is configured.
        """
        if _use_redis(settings, "rate_limit_backend"):
            client = _build_redis_client(settings)
            return RedisRateLimiter(client)
        return _RateLimiter()

    @bean
    def agent_token_repository(self, settings: FlyquerySettings) -> AgentTokenRepository:
        return AgentTokenRepository.from_url(settings.database_url)

    @bean
    def agent_token_service(
        self,
        agent_token_repository: AgentTokenRepository,
        rate_limiter: RateLimiter,
    ) -> AgentTokenService:
        return AgentTokenService(agent_token_repository, rate_limiter=rate_limiter)

    # ------------------------------------------------------------------
    # ObjectStore (blob storage)
    # ------------------------------------------------------------------

    @bean
    def object_store(self, settings: FlyquerySettings) -> ObjectStore:
        return build_object_store(settings)

    # ------------------------------------------------------------------
    # EDA publisher
    # ------------------------------------------------------------------
    #
    # ``IngestPublisher`` registers itself via ``@service`` (see
    # ``flyquery.core.eda.ingest_publisher``). Do NOT add a @bean
    # factory here: a factory shadows the @service registration and
    # resolves ``EventPublisher`` at factory-evaluation time (before
    # ``EdaAutoConfiguration`` has wired it), so the wrapper ends up
    # with ``self._publisher = None`` and silently drops every publish
    # into the in-memory branch -- workers never see the event.

    # ------------------------------------------------------------------
    # Retrieval infrastructure
    # ------------------------------------------------------------------

    @bean
    def embedder(self, settings: FlyquerySettings) -> Embedder:
        """Provider-agnostic embedder via fireflyframework-agentic.

        Reads ``settings.embedding_provider`` (default ``ollama``) and
        builds the matching adapter. Falls back to a ``NullEmbedder``
        when the provider is unavailable; retrieval gracefully
        degrades to BM25 over ``content_tsv``.
        """
        return build_embedder(settings)

    @bean
    def reranker(self, settings: FlyquerySettings) -> NoopReranker:
        """Cross-encoder reranker (falls back to NoopReranker when unavailable)."""
        return build_reranker(settings)  # type: ignore[return-value]

    # ------------------------------------------------------------------
    # Idempotency store (agent surface)
    # ------------------------------------------------------------------

    @bean
    def idempotency_store(self, settings: FlyquerySettings) -> IdempotencyStore:
        if _use_redis(settings, "idempotency_backend"):
            client = _build_redis_client(settings)
            return RedisIdempotencyStore(client)
        return InMemoryIdempotencyStore()


# ----------------------------------------------------------------------
# Redis adapter helpers
# ----------------------------------------------------------------------


def _use_redis(settings: FlyquerySettings, backend_field: str) -> bool:
    explicit = getattr(settings, backend_field, "auto") or "auto"
    explicit = explicit.lower()
    if explicit == "redis":
        return True
    if explicit in {"in_memory", "memory"}:
        return False
    return bool(settings.redis_url)


def _build_redis_client(settings: FlyquerySettings):  # noqa: ANN202
    from redis.asyncio import from_url as _redis_from_url

    return _redis_from_url(settings.redis_url)
