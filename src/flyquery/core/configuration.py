# Copyright 2026 Firefly Software Solutions Inc
"""DI configuration bean for flyquery."""

from __future__ import annotations

from pyfly.container import bean, configuration

from flyquery.config import FlyquerySettings
from flyquery.core.eda.ingest_publisher import IngestPublisher
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

    @bean
    def ingest_publisher(self, settings: FlyquerySettings) -> IngestPublisher:
        """Wire the IngestPublisher with pyfly's EventPublisher bean.

        The EventPublisher is auto-configured by pyfly when EDA is enabled
        (pyfly.eda.enabled=true in pyfly.yaml). If it's not available in the
        container (test isolation / single-process), we fall back to the
        in-memory stub so unit tests don't need a live Postgres channel.
        """
        try:
            from pyfly.eda import EventPublisher as _EventPublisher  # noqa: F401

            # Attempt to resolve the EventPublisher from pyfly's context
            # via a lazy import; falls through to None if unavailable.
            event_publisher = _resolve_eda_publisher()
        except Exception:  # noqa: BLE001
            event_publisher = None
        return IngestPublisher(event_publisher=event_publisher)

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


def _resolve_eda_publisher() -> object | None:
    """Lazily resolve pyfly's EventPublisher from the running container.

    Returns ``None`` when the container hasn't started yet (test isolation)
    or when pyfly's EDA module is not fully wired. The IngestPublisher
    falls back to in-memory mode in that case.
    """
    try:
        from pyfly.context import ApplicationContext

        ctx = ApplicationContext.current()
        if ctx is None:
            return None
        from pyfly.eda import EventPublisher

        return ctx.get_bean(EventPublisher)  # type: ignore[arg-type]
    except Exception:  # noqa: BLE001
        return None


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
