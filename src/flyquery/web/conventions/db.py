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

"""Session-level GUC helpers for tenant + workspace scope.

Postgres RLS policies (migration ``0006``) match rows by the
``app.tenant_id`` + ``app.workspace_id`` GUCs. The application must
set these per-transaction or every read returns the empty set (and
every write fails the WITH-CHECK).

This module exposes two collaborating primitives:

* :func:`set_tenant_guc` -- coroutine that issues ``SET LOCAL`` on
  an open :class:`AsyncSession`. Postgres-only; SQLite is a no-op.
  Used directly by tests and by anyone who needs to apply the GUCs
  outside the standard request flow.
* :func:`install_tenant_guc_hook` -- registers an SQLAlchemy
  ``after_begin`` listener on the (sync) session class behind every
  :class:`AsyncSession` checked out from the wired engine. The
  listener reads the request-scoped :class:`TenantContext` from the
  ContextVar and applies ``SET LOCAL`` so every transaction inside a
  request automatically picks up the right scope. Worker
  transactions (no bound context) get nothing, preserving their
  cross-workspace access.

The ``SET LOCAL`` values are validated slugs (alnum + hyphen,
fixed max length) coming through :class:`TenantContext`, so embedding
them as a SQL literal is safe -- ``SET LOCAL`` does not accept bind
parameters, so we string-format rather than pass ``execute()``
params. The slug validator is the security boundary; this module
trusts it.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session as SyncSession

from flyquery.web.conventions.context import (
    TenantContext,
    current_tenant_context,
)


async def set_tenant_guc(session: AsyncSession, ctx: TenantContext) -> None:
    """Apply ``SET LOCAL app.{tenant,workspace}_id`` for the current txn.

    Postgres-only -- on SQLite (or any other dialect that doesn't
    speak Postgres GUCs) this is a no-op so unit tests against
    ``sqlite+aiosqlite`` work transparently.
    """
    bind = session.get_bind()
    dialect = bind.dialect.name if bind is not None else ""
    if dialect != "postgresql":
        return
    # SET LOCAL does NOT accept bind parameters (it's parsed before
    # parameter binding happens). The values are already validated
    # slugs so the literal embed is safe.
    await session.execute(text(f"SET LOCAL app.tenant_id = '{ctx.tenant_id}'"))
    await session.execute(text(f"SET LOCAL app.workspace_id = '{ctx.workspace_id}'"))


def install_tenant_guc_hook() -> None:
    """Register the ``after_begin`` listener that auto-applies GUCs.

    Called once at boot. The listener fires for every transaction
    SQLAlchemy begins on the synchronous :class:`Session` underlying
    every :class:`AsyncSession` -- which is every transaction in the
    service. When no :class:`TenantContext` is bound (the worker
    path, the retention reaper, the boot-time migration runner) the
    listener is a no-op and the transaction proceeds without GUCs,
    matching the cross-workspace access pattern those callers expect.

    Idempotent: registering the listener twice is harmless --
    SQLAlchemy dedupes by callable identity on the same class.
    """
    if getattr(install_tenant_guc_hook, "_installed", False):
        return

    @event.listens_for(SyncSession, "after_begin")
    def _set_guc_on_begin(
        session: SyncSession,
        transaction: Any,
        connection: Any,
    ) -> None:
        # Postgres-only -- skip cleanly on SQLite + any non-pg dialect
        # so the boot-time migration runner and the SQLite-backed
        # tests are unaffected.
        if connection.dialect.name != "postgresql":
            return
        ctx = current_tenant_context()
        if ctx is None:
            # No request-scope context bound -- worker / migration /
            # boot path. Skip silently so cross-workspace queries keep
            # working (workers genuinely need to read across tenants).
            return
        connection.execute(text(f"SET LOCAL app.tenant_id = '{ctx.tenant_id}'"))
        connection.execute(text(f"SET LOCAL app.workspace_id = '{ctx.workspace_id}'"))

    install_tenant_guc_hook._installed = True  # type: ignore[attr-defined]
