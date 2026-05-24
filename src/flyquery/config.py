# Copyright 2026 Firefly Software Solutions Inc
"""Runtime configuration for flyquery (pydantic-settings).

Every knob exposed by the spec §12 lands here. The class is mounted
into the pyfly context as a @configuration bean (see
core/configuration.py).
"""

from __future__ import annotations

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class FlyquerySettings(BaseSettings):
    """All FLYQUERY_* env vars in one place."""

    model_config = SettingsConfigDict(
        env_prefix="FLYQUERY_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Service
    log_level: str = "INFO"
    port: int = 8520
    database_url: str = "postgresql+asyncpg://flyquery:flyquery@localhost:5552/flyquery"
    database_url_admin: str = "postgresql+psycopg://flyquery_admin:flyquery_admin@localhost:5552/flyquery"
    run_migrations: bool = True

    # Object store
    object_store: Literal["local", "s3", "gcs", "azure"] = "local"
    object_store_base: str = "/var/lib/flyquery/blobs"
    object_store_kms_default: str = ""
    object_store_presign_ttl_s: int = 86400

    # DuckDB execution (Plan 3; harmless to define now)
    duckdb_httpfs: bool = True
    duckdb_httpfs_metadata_cache_mb: int = 512
    duckdb_memory_limit: str = "4GB"
    default_row_cap: int = 1000
    default_statement_timeout_ms: int = 30000
    result_preview_max_bytes: int = 131072
    result_ttl_hours: int = 24

    # Upload caps (Plan 2)
    max_file_mb: int = 2048
    max_workspace_gb: int = 200

    # Ingestion knobs (Plans 2-3)
    ingest_topic: str = "flyquery.ingest"
    ingest_worker_concurrency: int = 4
    ingest_handler_timeout_s: int = 600
    ingest_shutdown_grace_s: int = 30
    ingest_heartbeat_s: int = 30
    ingest_max_attempts: int = 3
    sample_n: int = 8
    profile_row_threshold: int = 10_000_000
    describe_budget_cents_per_run: int = 200
    describe_batch: int = 20
    relation_proposer_enabled: bool = True
    relation_proposer_max_per_pair: int = 3
    relation_heuristic_min_confidence: float = 0.5
    max_title_rows: int = 3
    type_infer_sample_rows: int = 8192
    default_locale: str = "en-US"

    # Pipeline knobs (Plan 3)
    grounding_model: str = "anthropic:claude-sonnet-4-6"
    generation_model: str = "anthropic:claude-sonnet-4-6"
    critic_model: str = "anthropic:claude-sonnet-4-6"
    explainer_model: str = "anthropic:claude-haiku-4-5"
    describe_model: str = "anthropic:claude-haiku-4-5"
    relation_proposer_model: str = "anthropic:claude-sonnet-4-6"
    rename_detect_model: str = "anthropic:claude-haiku-4-5"
    fallback_model: str = "openai:gpt-4o"
    generation_candidates: int = 3
    max_refine_retries: int = 2
    expand_iters: int = 2
    grounding_min_confidence: float = 0.55
    agent_max_output_tokens: int = 8192

    # Ingestion pipeline concurrency / throughput tuning.
    #
    # ``ingest_section_concurrency`` caps the number of XLSX sections
    # processed in parallel through the synchronous per-section
    # pipeline (reconcile -> sample -> profile -> describe -> embed ->
    # publish). Each section runs ~1 describe + 1 column-naming LLM
    # call; for a 60-section dashboard XLSX serialising those takes
    # ~4 min and firing them all at once (60 simultaneous) trips
    # Anthropic's per-key RPM. The default of 8 keeps wall-clock low
    # while staying under standard rate limits.
    ingest_section_concurrency: int = 8

    # Embeddings + retrieval (lock-step with canon)
    #
    # Provider selection lets the operator pick between hosted (OpenAI,
    # Cohere, Voyage, Mistral, Azure, Google, Bedrock) and local
    # (Ollama) embedding backends. The implementation is delegated to
    # fireflyframework-agentic's ``BaseEmbedder`` registry so any
    # provider supported there is available here.
    #
    # Default: ``ollama`` + ``nomic-embed-text`` (768-d). This lets a
    # fresh ``docker compose up`` work end-to-end without an OpenAI
    # account -- Ollama is bundled in the test stack. The schema
    # column is ``vector(1536)`` so smaller-dim providers are
    # zero-padded by the persistence helper; cosine similarity is
    # preserved across the padding because the extra zero coordinates
    # add zero to both the dot product and the L2 norms (the rankings
    # in `embedding <=> CAST(:emb AS vector)` are stable).
    embedding_provider: Literal[
        "ollama", "openai", "cohere", "voyage", "azure", "google", "mistral", "bedrock", "null"
    ] = "ollama"
    embedding_model: str = "nomic-embed-text"
    embedding_dimensions: int = 1536
    embedding_native_dim: int = 768  # native dim of the chosen model (used for padding)
    embedding_base_url: str | None = None  # set for Ollama (http://localhost:11434) etc
    embedding_rate_limit_rpm: int = 3000
    vector_store: str = "pgvector"
    top_k_schema: int = 12
    top_k_examples: int = 5
    top_k_metrics: int = 8
    rrf_k: int = 60
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    reranker_top_n: int = 30
    query_expansion_enabled: bool = False

    # PII
    pii_scanner: Literal["regex", "presidio", "disabled"] = "regex"
    pii_policy_samples: Literal["warn", "redact", "reject"] = "redact"
    pii_policy_results: Literal["warn", "redact", "reject"] = "warn"
    pii_regex_patterns_path: str = ""
    presidio_spacy_model: str = "en_core_web_sm"

    # Auth + backends
    redis_url: str = ""
    rate_limit_backend: str = "auto"
    idempotency_backend: str = "auto"

    # EDA
    eda_adapter: str = "postgres"
    eda_destinations: str = "flyquery.ingest,flyquery.schema,flyquery.audit"
    eda_group: str = "flyquery-workers"
    kafka_bootstrap_servers: str = ""

    # Conversation memory
    conv_ttl_days: int = 90
    conv_history_turns: int = 10
    conv_summary_max_tokens: int = 500
    conv_summary_interval: int = 5

    # Auto-learn
    autolearn_enabled: bool = True

    # Observability
    otel_endpoint: str = ""

    # ------------------------------------------------------------------
    # Retention worker (26.5.10+)
    # ------------------------------------------------------------------
    #
    # ``RetentionWorker`` is the second long-running process the
    # service now needs (the first is ``IngestWorker``). It runs a
    # periodic loop that:
    #
    # 1. **Reaps stuck RUNNING ingest jobs** -- a crashed worker
    #    leaves a job in RUNNING with no path back to PENDING (the
    #    atomic claim in ``_mark_running`` requires PENDING). Every
    #    sweep we reset jobs whose ``started_at`` is older than
    #    ``processing_lease_s`` and republish them onto the bus.
    # 2. **Republishes orphan PENDING jobs** -- a publish that crashed
    #    after the DB insert leaves the row in PENDING with no event
    #    on the bus. We republish PENDING jobs older than
    #    ``orphan_queued_grace_s``.
    # 3. **TTL-deletes** rows in ``flyquery_ingest_events``,
    #    ``flyquery_audit_events``, and ``flyquery_cost_events``
    #    older than the per-table retention window. Set a window to
    #    ``0`` to disable TTL on that table (kept forever).
    # 4. **Reclaims storage for PURGING datasets** -- the SQL row of
    #    a dataset whose ``status`` has been ``PURGING`` for longer
    #    than ``dataset_purge_tombstone_days`` is finally deleted.
    #
    # Defaults are conservative -- prod operators tune via env vars.
    retention_scan_interval_s: int = 300  # 5 minutes
    retention_ingest_events_days: int = 30
    retention_audit_events_days: int = 365  # one year, compliance default
    retention_cost_events_days: int = 365
    processing_lease_s: int = 1800  # 30 minutes -- longer than the longest job
    orphan_queued_grace_s: int = 600  # 10 minutes
    dataset_purge_tombstone_days: int = 90
