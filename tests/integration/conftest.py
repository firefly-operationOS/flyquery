# Copyright 2026 Firefly Software Solutions Inc
"""Integration-test fixtures: Postgres + Redis + MinIO containers."""

from __future__ import annotations

import os
from collections.abc import Iterator

import pytest
from testcontainers.minio import MinioContainer
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer


@pytest.fixture(scope="session")
def postgres_container() -> Iterator[PostgresContainer]:
    with PostgresContainer("pgvector/pgvector:pg16") as pg:
        # Container exposes the default `test` user as SUPERUSER which
        # would silently BYPASSRLS (memory: postgres_test_role_bypasses_rls).
        # We provision flyquery_admin (BYPASSRLS) + flyquery_app (no bypass)
        # via the RLS migration in Task 21 / fixture below.
        yield pg


@pytest.fixture(scope="session")
def redis_container() -> Iterator[RedisContainer]:
    with RedisContainer() as r:
        yield r


@pytest.fixture(scope="session")
def minio_container() -> Iterator[MinioContainer]:
    with MinioContainer() as m:
        yield m


@pytest.fixture(autouse=True)
def configure_env(
    monkeypatch: pytest.MonkeyPatch,
    postgres_container: PostgresContainer,
    redis_container: RedisContainer,
    minio_container: MinioContainer,
) -> None:
    sync_url = postgres_container.get_connection_url()  # postgresql+psycopg2://...
    async_url = sync_url.replace("+psycopg2", "+asyncpg").replace("+psycopg", "+asyncpg")
    admin_url = sync_url.replace("+psycopg2", "+psycopg")
    monkeypatch.setenv("FLYQUERY_DATABASE_URL", async_url)
    monkeypatch.setenv("FLYQUERY_DATABASE_URL_ADMIN", admin_url)
    redis_host = redis_container.get_container_host_ip()
    redis_port = redis_container.get_exposed_port(redis_container.port)
    monkeypatch.setenv("FLYQUERY_REDIS_URL", f"redis://{redis_host}:{redis_port}/0")
    monkeypatch.setenv("FLYQUERY_OBJECT_STORE", "s3")
    monkeypatch.setenv("FLYQUERY_OBJECT_STORE_BASE", f"s3://{minio_container.get_config()['endpoint']}/flyquery-test")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", minio_container.access_key)
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", minio_container.secret_key)
    monkeypatch.setenv("FLYQUERY_RUN_MIGRATIONS", "false")
    # After migration 0007 provisions flyquery_app (NOSUPERUSER), the runtime
    # URL must authenticate as that role so RLS policies actually fire.
    # The admin URL (BYPASSRLS) is kept in FLYQUERY_DATABASE_URL_ADMIN for
    # migrations and seeding (memory: postgres_test_role_bypasses_rls).
    app_url = async_url.replace(
        f"//{postgres_container.username}:{postgres_container.password}",
        "//flyquery_app:flyquery_app"
    )
    monkeypatch.setenv("FLYQUERY_DATABASE_URL", app_url)
