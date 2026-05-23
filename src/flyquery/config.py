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
    sample_n: int = 8
    profile_row_threshold: int = 10_000_000
    describe_budget_cents_per_run: int = 200
    describe_batch: int = 20
    relation_proposer_enabled: bool = True
    relation_proposer_max_per_pair: int = 3
    relation_heuristic_min_confidence: float = 0.85
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

    # Embeddings + retrieval (lock-step with canon)
    embedding_model: str = "openai:text-embedding-3-small"
    embedding_dimensions: int = 1536
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

    # Auth + backends
    redis_url: str = ""
    rate_limit_backend: str = "auto"
    idempotency_backend: str = "auto"

    # EDA
    eda_adapter: str = "postgres"
    eda_destinations: str = "flyquery.ingest,flyquery.schema,flyquery.audit"
    eda_group: str = "flyquery-workers"
