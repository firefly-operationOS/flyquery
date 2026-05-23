# Copyright 2026 Firefly Software Solutions Inc
"""Smoke test: app imports + actuator/health responds 200."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.integration
@pytest.mark.asyncio
async def test_app_boots_and_health_endpoint_responds() -> None:
    from flyquery.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as client:
        resp = await client.get("/actuator/health")
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("status") in ("UP", "OK")
