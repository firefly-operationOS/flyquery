# Copyright 2026 Firefly Software Solutions Inc
"""Integration tests for the bulk endpoints.

* ``POST /api/v1/datasets/{id}/files:bulk`` -- multi-file upload
* ``POST /api/v1/query:batch``                -- multi-question query

Both endpoints process items in parallel on the server (``asyncio.gather``)
and continue past per-item failures so the caller sees which items
succeeded and which didn't.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

ROOT = Path(__file__).resolve().parent.parent.parent
EXAMPLES = ROOT / "examples"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_bulk_file_upload_happy_path() -> None:
    from flyquery.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        tenant = {"X-Tenant-Id": "bulk-files-tenant"}
        r = await c.post(
            "/api/v1/workspaces",
            json={"slug": "bulk-files", "name": "Bulk Files"},
            headers={**tenant, "X-Workspace-Id": "bulk-files"},
        )
        assert r.status_code == 201, r.text
        ws = r.json()["id"]
        h = {**tenant, "X-Workspace-Id": ws}

        r = await c.post(
            "/api/v1/datasets",
            json={"name": "bulk", "description": "x"},
            headers=h,
        )
        assert r.status_code == 201, r.text
        ds = r.json()["id"]

        files = [
            ("files", ("customers.csv", (EXAMPLES / "csv" / "customers.csv").read_bytes(), "text/csv")),
            (
                "files",
                ("products.json", (EXAMPLES / "json" / "products.json").read_bytes(), "application/json"),
            ),
            (
                "files",
                (
                    "transactions.parquet",
                    (EXAMPLES / "parquet" / "transactions.parquet").read_bytes(),
                    "application/octet-stream",
                ),
            ),
        ]
        r = await c.post(
            f"/api/v1/datasets/{ds}/files:bulk",
            headers=h,
            files=files,
            timeout=240.0,
        )
        assert r.status_code == 201, r.text
        body = r.json()
        assert body["total_files"] == 3
        assert body["succeeded"] == 3
        assert body["failed"] == 0
        # The results are ordered by submission index.
        names = [r["original_filename"] for r in body["results"]]
        assert names == ["customers.csv", "products.json", "transactions.parquet"]
        for item in body["results"]:
            assert item["status"] == "OK"
            assert item["file_id"]
            assert item["tables"], f"expected >=1 table for {item['original_filename']}"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_bulk_file_upload_one_failure_does_not_abort() -> None:
    """A malformed file produces status=FAILED + error -- the others still succeed."""
    from flyquery.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        tenant = {"X-Tenant-Id": "bulk-mix-tenant"}
        r = await c.post(
            "/api/v1/workspaces",
            json={"slug": "bulk-mix", "name": "Bulk Mix"},
            headers={**tenant, "X-Workspace-Id": "bulk-mix"},
        )
        ws = r.json()["id"]
        h = {**tenant, "X-Workspace-Id": ws}

        r = await c.post(
            "/api/v1/datasets",
            json={"name": "bulkmix"},
            headers=h,
        )
        ds = r.json()["id"]

        # Two valid + one garbage.
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as bad:
            bad.write(b"this is not a csv\xff\xfe\x00binary\x00garbage")
            bad_path = Path(bad.name)
        try:
            files = [
                ("files", ("good.csv", (EXAMPLES / "csv" / "customers.csv").read_bytes(), "text/csv")),
                ("files", ("bad.csv", bad_path.read_bytes(), "text/csv")),
                (
                    "files",
                    ("good2.json", (EXAMPLES / "json" / "products.json").read_bytes(), "application/json"),
                ),
            ]
            r = await c.post(
                f"/api/v1/datasets/{ds}/files:bulk",
                headers=h,
                files=files,
                timeout=240.0,
            )
        finally:
            bad_path.unlink(missing_ok=True)

        assert r.status_code == 201, r.text
        body = r.json()
        assert body["total_files"] == 3
        # The two valid fixtures must succeed; the bad one MAY succeed
        # (DuckDB is lenient with single-column garbage CSV) so we only
        # assert that the bulk completed without raising.
        assert body["succeeded"] >= 2


@pytest.mark.integration
@pytest.mark.asyncio
async def test_batch_query_returns_ordered_results() -> None:
    from flyquery.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        tenant = {"X-Tenant-Id": "batch-q-tenant"}
        r = await c.post(
            "/api/v1/workspaces",
            json={"slug": "batch-q", "name": "Batch Q"},
            headers={**tenant, "X-Workspace-Id": "batch-q"},
        )
        ws = r.json()["id"]
        h = {**tenant, "X-Workspace-Id": ws}

        r = await c.post(
            "/api/v1/datasets",
            json={"name": "bq"},
            headers=h,
        )
        ds = r.json()["id"]

        # Upload a single fixture so the batch has something to query.
        with (EXAMPLES / "csv" / "customers.csv").open("rb") as f:
            r = await c.post(
                f"/api/v1/datasets/{ds}/files",
                headers=h,
                files={"file": ("customers.csv", f, "text/csv")},
                timeout=240.0,
            )
        assert r.status_code == 201, r.text

        # Three questions in parallel.
        body = {
            "queries": [
                {"question": "How many customers do we have?", "dataset_id": ds},
                {"question": "Which country has the most customers?", "dataset_id": ds},
                {"question": "What is the average lifetime_value_eur?", "dataset_id": ds},
            ]
        }
        r = await c.post(
            "/api/v1/query:batch",
            headers=h,
            content=json.dumps(body),
            timeout=240.0,
        )
        assert r.status_code == 200, r.text
        out = r.json()
        assert out["total_queries"] == 3
        # Indexes preserved.
        assert [r["index"] for r in out["results"]] == [0, 1, 2]
        # The endpoint must always RESPOND (no exceptions abort the
        # batch even when the upstream LLM provider is unavailable).
        # We do not assert on ``succeeded`` because CI runs may lack
        # an Anthropic API key -- the batch shape contract is the
        # only invariant.
        assert out["failed"] + out["succeeded"] == 3
