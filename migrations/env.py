# Copyright 2024-2026 Firefly Software Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Alembic env -- sync runner that delegates to the project's ORM metadata.

The application uses async SQLAlchemy, but Alembic always runs sync;
we strip the async driver suffix to make the URL synchronous for the
migration step. Production migrations are usually run as a one-shot
container, not from inside the API process.

The :data:`target_metadata` import is lazy because the entities package
ships in later commits -- this keeps the bootstrap commit alembic-clean
while still letting ``alembic upgrade head`` resolve once the ORM is
in place. Falling back to ``None`` makes Alembic operate purely on the
SQL emitted by hand-written migrations until then.
"""

from __future__ import annotations

import importlib
import os
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import MetaData, engine_from_config, pool

# Make ``src`` importable.
_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "src"))


def _resolve_metadata() -> MetaData | None:
    """Import the ORM metadata if present; ``None`` otherwise.

    The bootstrap skeleton has no entities yet; later commits land
    ``flyquery.models.entities`` and this function picks them up
    transparently.
    """
    try:
        entities = importlib.import_module("flyquery.models.entities")
    except ImportError:
        return None
    base = getattr(entities, "Base", None)
    return getattr(base, "metadata", None)


config = context.config

# Resolve the connection URL. Precedence:
#   1. ``sqlalchemy.url`` already set on the alembic.Config object --
#      callers that build the config in-process (tests / programmatic
#      runs) set this explicitly and MUST win.
#   2. ``FLYQUERY_DATABASE_URL_ADMIN`` env var -- preferred for migrations
#      (admin role with BYPASSRLS).
#   3. ``FLYQUERY_DATABASE_URL`` env var -- fallback to app role.
#
# The previous ordering (env > config) caused test-isolation bleed when
# another test (e.g. test_openapi_snapshot) called
# ``os.environ.setdefault("FLYQUERY_DATABASE_URL", ...)`` to a tempfile-
# backed SQLite at module-import time; subsequent migration smoke
# tests that built their own alembic.Config with
# ``cfg.set_main_option("sqlalchemy.url", ...)`` were silently
# retargeted at the openapi test's database and saw stale tables.
admin_url = os.environ.get("FLYQUERY_DATABASE_URL_ADMIN")
app_url = os.environ.get("FLYQUERY_DATABASE_URL")
url = config.get_main_option("sqlalchemy.url") or admin_url or app_url
if url:
    sync_url = url.replace("+asyncpg", "+psycopg").replace("+aiosqlite", "")
    config.set_main_option("sqlalchemy.url", sync_url)

if config.config_file_name is not None:
    # disable_existing_loggers=False: running migrations must not silently
    # disable loggers the application already created at import time
    # (alembic/fileConfig defaults to True, which otherwise mutes them).
    fileConfig(config.config_file_name, disable_existing_loggers=False)

target_metadata = _resolve_metadata()


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
