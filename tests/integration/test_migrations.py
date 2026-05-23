# tests/integration/test_migrations.py
# Copyright 2026 Firefly Software Solutions Inc
"""End-to-end migration smoke: alembic upgrade head + table presence."""

from __future__ import annotations

import os
import subprocess

import pytest
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
    assert expected <= names
