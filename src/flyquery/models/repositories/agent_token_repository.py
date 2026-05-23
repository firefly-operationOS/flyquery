# Copyright 2026 Firefly Software Solutions Inc
"""``AgentTokenRepository`` -- async SQLAlchemy data-access for agent tokens."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine


class AgentTokenRepository:
    """Repository over ``flyquery_agent_tokens``.

    Can be constructed from an ``async_sessionmaker`` (DI injection path) or
    via the ``from_url`` classmethod (configuration @bean path), identical to
    the canon pattern.

    Returns plain ``dict`` rows so the service layer never imports SQLAlchemy.
    Every write + read filters by ``tenant_id`` at SQL level as defense-in-depth
    alongside the ``tenant_isolation`` RLS policy on ``flyquery_agent_tokens``.
    """

    def __init__(
        self,
        session: async_sessionmaker[AsyncSession],
        *,
        engine: AsyncEngine | None = None,
    ) -> None:
        self._factory = session
        self._engine = engine

    @property
    def engine(self) -> AsyncEngine | None:
        """Underlying ``AsyncEngine`` -- consumed by the actuator probe."""
        return self._engine

    @classmethod
    def from_url(cls, database_url: str, *, echo: bool = False) -> "AgentTokenRepository":
        """Build a repository from a database URL (configuration @bean path)."""
        from flyquery.web.conventions.db import install_tenant_guc_hook

        install_tenant_guc_hook()
        engine = create_async_engine(database_url, echo=echo, future=True, pool_pre_ping=True)
        factory = async_sessionmaker(engine, expire_on_commit=False)
        return cls(factory, engine=engine)

    async def insert(self, row: dict[str, Any]) -> None:
        """Insert a new token row. ``scopes_json`` and ``workspace_allowlist_json`` are JSON arrays."""
        import json

        scopes = row.get("scopes_json") or []
        allowlist = row.get("workspace_allowlist_json")

        async with self._factory() as s, s.begin():
            await s.execute(
                sa.text(
                    """
                    INSERT INTO flyquery_agent_tokens
                        (id, tenant_id, name, prefix, secret_hash,
                         workspace_allowlist_json, scopes_json,
                         rate_limit_rpm, expires_at,
                         created_at, created_by,
                         revoked_at, last_used_at)
                    VALUES
                        (:id, :tenant_id, :name, :prefix, :secret_hash,
                         CAST(:workspace_allowlist_json AS jsonb),
                         CAST(:scopes_json AS jsonb),
                         :rate_limit_rpm, :expires_at,
                         :created_at, :created_by,
                         :revoked_at, :last_used_at)
                    """
                ),
                {
                    "id": str(row["id"]),
                    "tenant_id": row["tenant_id"],
                    "name": row["name"],
                    "prefix": row["prefix"],
                    "secret_hash": row["secret_hash"],
                    "workspace_allowlist_json": json.dumps(allowlist) if allowlist is not None else "null",
                    "scopes_json": json.dumps(scopes),
                    "rate_limit_rpm": row.get("rate_limit_rpm"),
                    "expires_at": row.get("expires_at"),
                    "created_at": row["created_at"],
                    "created_by": row["created_by"],
                    "revoked_at": row.get("revoked_at"),
                    "last_used_at": row.get("last_used_at"),
                },
            )

    async def get_by_prefix(self, prefix: str, *, tenant_id: str) -> dict[str, Any] | None:
        async with self._factory() as s:
            result = await s.execute(
                sa.text(
                    """
                    SELECT * FROM flyquery_agent_tokens
                    WHERE prefix = :prefix
                      AND tenant_id = :tenant_id
                      AND revoked_at IS NULL
                    """
                ),
                {"prefix": prefix, "tenant_id": tenant_id},
            )
            row = result.mappings().one_or_none()
            return _normalise(dict(row)) if row else None

    async def list_for_tenant(self, tenant_id: str) -> list[dict[str, Any]]:
        async with self._factory() as s:
            result = await s.execute(
                sa.text(
                    """
                    SELECT * FROM flyquery_agent_tokens
                    WHERE tenant_id = :tenant_id
                    ORDER BY created_at DESC
                    """
                ),
                {"tenant_id": tenant_id},
            )
            return [_normalise(dict(row)) for row in result.mappings().all()]

    async def revoke(self, token_id: str, *, tenant_id: str, at: datetime) -> bool:
        async with self._factory() as s, s.begin():
            result = await s.execute(
                sa.text(
                    """
                    UPDATE flyquery_agent_tokens
                    SET revoked_at = :at
                    WHERE id = :id
                      AND tenant_id = :tenant_id
                      AND revoked_at IS NULL
                    """
                ),
                {"id": token_id, "tenant_id": tenant_id, "at": at},
            )
            rowcount = result.rowcount or 0
            return rowcount > 0

    async def mark_used(self, token_id: str, *, tenant_id: str, at: datetime) -> None:
        async with self._factory() as s, s.begin():
            await s.execute(
                sa.text(
                    """
                    UPDATE flyquery_agent_tokens
                    SET last_used_at = :at
                    WHERE id = :id
                      AND tenant_id = :tenant_id
                    """
                ),
                {"id": token_id, "tenant_id": tenant_id, "at": at},
            )


def _normalise(row: dict[str, Any]) -> dict[str, Any]:
    """Coerce Postgres-native types to the plain types the service layer expects.

    asyncpg returns UUID columns as :class:`uuid.UUID` objects and JSONB
    columns as Python dicts/lists.  The service layer stores ``id`` as ``str``
    (the ``AgentTokenSummary.id`` field is ``str``) so we normalise the ``id``
    field to its hex string (no hyphens) so that the comparison
    ``row["id"] == minted.id`` in :class:`AgentTokenService` always succeeds.
    """
    out: dict[str, Any] = {}
    for k, v in row.items():
        if isinstance(v, uuid.UUID):
            out[k] = v.hex  # match AgentTokenService's uuid4().hex format
        else:
            out[k] = v
    return out
