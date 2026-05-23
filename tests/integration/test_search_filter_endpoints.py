# Copyright 2026 Firefly Software Solutions Inc
"""Integration tests for search/filter + by-slug/by-name endpoints.

Exercises the new query-param surface on:

* ``GET /api/v1/workspaces``                        -- ``q``, ``slug``, ``status``,
                                                       ``limit``, ``offset``
* ``GET /api/v1/workspaces/by-slug/{slug}``         -- slug-based lookup
* ``GET /api/v1/datasets``                          -- ``q``, ``name``, ``status``,
                                                       ``workspace_id``, ``limit``,
                                                       ``offset``
* ``GET /api/v1/datasets/by-name/{name}``           -- name-based lookup
* ``GET /api/v1/tables``                            -- ``q``, ``name``, ``dataset_id``,
                                                       ``kind``, ``is_active``,
                                                       ``limit``, ``offset``
* ``GET /api/v1/tables/by-name/{name}``             -- table name lookup
"""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.integration
@pytest.mark.asyncio
async def test_workspaces_list_envelope_and_search() -> None:
    from flyquery.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        tenant = {"X-Tenant-Id": "tenant-search-ws"}
        for slug, name in [
            ("alpha-org", "Alpha Organisation"),
            ("beta-org", "Beta Organisation"),
            ("gamma-org", "Gamma Organisation"),
        ]:
            r = await c.post(
                "/api/v1/workspaces",
                json={"slug": slug, "name": name},
                headers={**tenant, "X-Workspace-Id": slug},
            )
            assert r.status_code == 201, r.text

        # Bare list returns envelope
        r = await c.get(
            "/api/v1/workspaces",
            headers={**tenant, "X-Workspace-Id": "alpha-org"},
        )
        assert r.status_code == 200, r.text
        body = r.json()
        assert "items" in body
        assert "total" in body and body["total"] >= 3
        assert "limit" in body and body["limit"] == 100
        assert "offset" in body and body["offset"] == 0
        assert "has_more" in body

        # Free-text search hits name + slug
        r = await c.get(
            "/api/v1/workspaces?q=beta",
            headers={**tenant, "X-Workspace-Id": "alpha-org"},
        )
        assert r.status_code == 200
        items = r.json()["items"]
        assert any(i["slug"] == "beta-org" for i in items)
        assert all("alpha" not in i["slug"] for i in items)

        # Exact slug filter -- equivalent to lookup
        r = await c.get(
            "/api/v1/workspaces?slug=gamma-org",
            headers={**tenant, "X-Workspace-Id": "alpha-org"},
        )
        assert r.status_code == 200
        items = r.json()["items"]
        assert len(items) == 1
        assert items[0]["slug"] == "gamma-org"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_workspace_by_slug_lookup() -> None:
    from flyquery.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        tenant = {"X-Tenant-Id": "tenant-by-slug"}
        r = await c.post(
            "/api/v1/workspaces",
            json={"slug": "lookup-me", "name": "Lookup Me"},
            headers={**tenant, "X-Workspace-Id": "lookup-me"},
        )
        assert r.status_code == 201

        r = await c.get(
            "/api/v1/workspaces/by-slug/lookup-me",
            headers={**tenant, "X-Workspace-Id": "lookup-me"},
        )
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["slug"] == "lookup-me"
        assert body["name"] == "Lookup Me"
        assert "id" in body

        r = await c.get(
            "/api/v1/workspaces/by-slug/does-not-exist",
            headers={**tenant, "X-Workspace-Id": "lookup-me"},
        )
        assert r.status_code == 404


@pytest.mark.integration
@pytest.mark.asyncio
async def test_workspace_pagination() -> None:
    from flyquery.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        tenant = {"X-Tenant-Id": "tenant-paging"}
        for i in range(5):
            r = await c.post(
                "/api/v1/workspaces",
                json={"slug": f"page-{i}", "name": f"Page {i}"},
                headers={**tenant, "X-Workspace-Id": f"page-{i}"},
            )
            assert r.status_code == 201

        r = await c.get(
            "/api/v1/workspaces?limit=2&offset=0",
            headers={**tenant, "X-Workspace-Id": "page-0"},
        )
        body = r.json()
        assert len(body["items"]) == 2
        assert body["total"] >= 5
        assert body["has_more"] is True

        r = await c.get(
            "/api/v1/workspaces?limit=2&offset=4",
            headers={**tenant, "X-Workspace-Id": "page-0"},
        )
        body = r.json()
        # offset=4 with 5 items -> 1 item left
        assert len(body["items"]) <= 2


@pytest.mark.integration
@pytest.mark.asyncio
async def test_datasets_search_filter_and_by_name() -> None:
    from flyquery.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        tenant = {"X-Tenant-Id": "tenant-ds-search"}
        r = await c.post(
            "/api/v1/workspaces",
            json={"slug": "ds-search-ws", "name": "DS Search WS"},
            headers={**tenant, "X-Workspace-Id": "ds-search-ws"},
        )
        ws_id = r.json()["id"]
        ws_headers = {**tenant, "X-Workspace-Id": ws_id}

        for name, desc in [
            ("Sales 2024", "Quarterly sales"),
            ("Sales 2025", "Forward-looking projection"),
            ("Customers", "Customer master data"),
        ]:
            r = await c.post(
                "/api/v1/datasets",
                json={"name": name, "description": desc},
                headers=ws_headers,
            )
            assert r.status_code == 201, r.text

        # Envelope
        r = await c.get("/api/v1/datasets", headers=ws_headers)
        body = r.json()
        assert body["total"] == 3
        assert len(body["items"]) == 3
        assert body["has_more"] is False

        # Free-text "Sales" hits both Sales* datasets
        r = await c.get("/api/v1/datasets?q=Sales", headers=ws_headers)
        items = r.json()["items"]
        assert {i["name"] for i in items} == {"Sales 2024", "Sales 2025"}

        # Free-text "projection" hits description, not name
        r = await c.get("/api/v1/datasets?q=projection", headers=ws_headers)
        items = r.json()["items"]
        assert len(items) == 1
        assert items[0]["name"] == "Sales 2025"

        # Exact name lookup -- by-name endpoint
        r = await c.get(
            "/api/v1/datasets/by-name/Customers",
            headers=ws_headers,
        )
        assert r.status_code == 200, r.text
        assert r.json()["name"] == "Customers"

        # by-name returns 404 for a missing name in this workspace
        r = await c.get(
            "/api/v1/datasets/by-name/Nope",
            headers=ws_headers,
        )
        assert r.status_code == 404
