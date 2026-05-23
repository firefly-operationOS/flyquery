# Copyright 2026 Firefly Software Solutions Inc
"""Integration-test fixtures: Postgres + Redis + MinIO containers."""

from __future__ import annotations

import os
import subprocess
from collections.abc import AsyncIterator, Iterator

import pytest
import pytest_asyncio
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


def _build_urls(postgres_container: PostgresContainer) -> tuple[str, str, str]:
    """Return (async_url, admin_url, app_url) from the container's sync URL."""
    sync_url = postgres_container.get_connection_url()  # postgresql+psycopg2://...
    async_url = sync_url.replace("+psycopg2", "+asyncpg").replace("+psycopg", "+asyncpg")
    admin_url = sync_url.replace("+psycopg2", "+psycopg")
    app_url = async_url.replace(
        f"//{postgres_container.username}:{postgres_container.password}",
        "//flyquery_app:flyquery_app",
    )
    return async_url, admin_url, app_url


@pytest.fixture(scope="session")
def run_migrations(
    postgres_container: PostgresContainer,
) -> None:
    """Run ``alembic upgrade head`` once per session against the test DB.

    This fixture is session-scoped so migrations run exactly once regardless
    of the order tests are collected. CRUD tests depend on it implicitly via
    the ``autouse`` ``configure_env`` fixture which pulls it in as a dependency.
    """
    _, admin_url, _ = _build_urls(postgres_container)
    env = {**os.environ, "FLYQUERY_DATABASE_URL_ADMIN": admin_url}
    subprocess.run(["uv", "run", "alembic", "upgrade", "head"], check=True, env=env)


@pytest.fixture(scope="session")
def session_env(
    run_migrations: None,
    postgres_container: PostgresContainer,
    redis_container: RedisContainer,
    minio_container: MinioContainer,
) -> None:
    """Set session-wide env vars so pyfly picks them up at startup."""
    async_url, admin_url, app_url = _build_urls(postgres_container)
    redis_host = redis_container.get_container_host_ip()
    redis_port = redis_container.get_exposed_port(redis_container.port)
    redis_url = f"redis://{redis_host}:{redis_port}/0"

    # Use admin URL so pyfly's EDA / DDL infra startup has DDL rights.
    # Per-test RLS isolation uses the app-role URL (set in configure_env).
    os.environ["FLYQUERY_DATABASE_URL"] = admin_url.replace("+psycopg", "+asyncpg")
    os.environ["FLYQUERY_DATABASE_URL_ADMIN"] = admin_url
    os.environ["FLYQUERY_REDIS_URL"] = redis_url
    os.environ["FLYQUERY_OBJECT_STORE"] = "local"
    os.environ["FLYQUERY_OBJECT_STORE_BASE"] = "/tmp/flyquery-test"
    os.environ["FLYQUERY_RUN_MIGRATIONS"] = "false"
    os.environ["AWS_ACCESS_KEY_ID"] = minio_container.access_key
    os.environ["AWS_SECRET_ACCESS_KEY"] = minio_container.secret_key


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def started_app(session_env: None) -> AsyncIterator[None]:
    """Start the pyfly application (run lifespan startup) once per session.

    ``httpx.ASGITransport`` does not trigger ASGI lifespan events, so the
    pyfly application context (including ``RelationalAutoConfiguration`` and
    all ``@auto_configuration`` beans) never gets started. This fixture
    drives the startup / shutdown lifecycle manually so every integration
    test sees a fully-initialised DI container.

    Must be async and share the session event loop so asyncpg connection
    pools are bound to the same loop that runs the tests.
    """
    from flyquery.main import _pyfly

    if not getattr(_pyfly.context, "_started", False):
        await _pyfly.startup()
    yield


@pytest.fixture(autouse=True)
def configure_env(
    monkeypatch: pytest.MonkeyPatch,
    postgres_container: PostgresContainer,
    redis_container: RedisContainer,
    minio_container: MinioContainer,
    started_app: None,
) -> None:
    async_url, admin_url, app_url = _build_urls(postgres_container)
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
    monkeypatch.setenv("FLYQUERY_DATABASE_URL", app_url)
