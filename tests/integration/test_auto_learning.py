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

"""Integration tests for /api/v1/examples CRUD + :approve/:reject."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.integration
@pytest.mark.asyncio
async def test_examples_crud(started_app: None) -> None:  # noqa: ARG001
    from flyquery.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        # First create a workspace so workspace_id is a real UUID
        r = await c.post(
            "/api/v1/workspaces",
            json={"slug": "exws", "name": "Examples WS"},
            headers={"X-Tenant-Id": "ten-a", "X-Workspace-Id": "placeholder"},
        )
        assert r.status_code == 201, r.text
        ws_id = r.json()["id"]
        h = {"X-Tenant-Id": "ten-a", "X-Workspace-Id": ws_id}

        # Create example
        r = await c.post(
            "/api/v1/examples",
            json={"question": "total revenue", "generated_sql": "SELECT sum(total) FROM orders"},
            headers=h,
        )
        assert r.status_code == 201, r.text
        ex_id = r.json()["id"]
        assert r.json()["source"] == "USER_CURATED"
        assert r.json()["quality"] == "PROPOSED"

        # Approve
        r = await c.post(f"/api/v1/examples/{ex_id}:approve", headers=h)
        assert r.status_code == 200, r.text
        assert r.json()["quality"] == "APPROVED"

        # List with quality filter
        r = await c.get("/api/v1/examples?quality=APPROVED", headers=h)
        assert r.status_code == 200, r.text
        assert len(r.json()["items"]) >= 1

        # Create another and reject
        r2 = await c.post(
            "/api/v1/examples",
            json={"question": "count orders", "generated_sql": "SELECT count(*) FROM orders"},
            headers=h,
        )
        assert r2.status_code == 201, r2.text
        ex_id2 = r2.json()["id"]

        r = await c.post(f"/api/v1/examples/{ex_id2}:reject", headers=h)
        assert r.status_code == 200, r.text
        assert r.json()["quality"] == "REJECTED"

        # List only PROPOSED → should be empty (we created 2, both processed)
        r = await c.get("/api/v1/examples?quality=PROPOSED", headers=h)
        assert r.status_code == 200, r.text
        assert len(r.json()["items"]) == 0
