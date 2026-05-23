# tests/integration/test_migrations.py
# Copyright 2026 Firefly Software Solutions Inc
"""End-to-end migration smoke: alembic upgrade head + table presence."""

from __future__ import annotations

import os
import subprocess

import pytest
import sqlalchemy as sa
from sqlalchemy import create_engine, inspect


@pytest.mark.integration
def test_alembic_upgrade_head_creates_all_tables() -> None:
    admin_url = os.environ["FLYQUERY_DATABASE_URL_ADMIN"]
    env = {**os.environ, "FLYQUERY_DATABASE_URL_ADMIN": admin_url}
    subprocess.run(["uv", "run", "alembic", "upgrade", "head"], check=True, env=env)
    eng = create_engine(admin_url)
    insp = inspect(eng)
    names = set(insp.get_table_names())
    expected = {
        "flyquery_workspaces", "flyquery_datasets", "flyquery_files", "flyquery_tables",
        "flyquery_schema_snapshots", "flyquery_schema_changes",
        "flyquery_schema_objects", "flyquery_relations",
    }
    expected |= {
        "flyquery_semantic_metrics", "flyquery_semantic_dimensions",
        "flyquery_semantic_versions", "flyquery_glossary_terms",
        "flyquery_examples",
    }
    expected |= {
        "flyquery_queries", "flyquery_query_results",
        "flyquery_conversations", "flyquery_conversation_turns",
    }
    expected |= {
        "flyquery_agent_tokens", "flyquery_audit_events", "flyquery_cost_events",
        "flyquery_ingest_jobs", "flyquery_ingest_events",
    }
    assert expected <= names


@pytest.mark.integration
def test_pgvector_and_indexes_present() -> None:
    eng = create_engine(os.environ["FLYQUERY_DATABASE_URL_ADMIN"])
    with eng.connect() as conn:
        ext = conn.execute(sa.text(
            "SELECT extname FROM pg_extension WHERE extname='vector'"
        )).scalar()
        assert ext == "vector"
        for idx in ("ix_objects_embedding", "ix_objects_tsv", "ix_examples_embedding"):
            count = conn.execute(sa.text(
                "SELECT count(*) FROM pg_indexes WHERE indexname=:n"
            ), {"n": idx}).scalar()
            assert count == 1, f"missing index {idx}"
