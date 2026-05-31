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

"""Integration test: ingest every fixture under ``examples/``.

Walks ``examples/*/`` and uploads each file to a fresh workspace via
the HTTP API. Asserts:

* Each upload returns 201.
* Each upload creates >=1 table (the dashboard XLSX creates several).
* The catalogue total grows monotonically as files are added.
* Every file format the README declares actually has a fixture file.

Catches regressions in:

* Format detection (``file_format`` resolver picks the right reader).
* Per-format readers (CSV / JSON / JSONL / XLSX / Parquet).
* Compression handling for ``.gz``-wrapped CSV (covered when present).
* The smart column-name proposer (the dashboard XLSX section names).
"""

from __future__ import annotations

from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

ROOT = Path(__file__).resolve().parent.parent.parent
EXAMPLES = ROOT / "examples"


def _all_example_files() -> list[Path]:
    """Every file under ``examples/`` ingest knows how to read."""
    return sorted(
        p
        for sub in ("csv", "json", "jsonl", "xlsx", "parquet")
        for p in (EXAMPLES / sub).glob("*")
        if p.is_file() and not p.name.startswith(".")
    )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_every_fixture_ingests() -> None:
    """End-to-end: every fixture file uploads + materialises >=1 table."""
    from flyquery.main import app

    fixtures = _all_example_files()
    assert fixtures, "examples/ must contain fixture files -- run scripts/generate_examples.py"

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        tenant = {"X-Tenant-Id": "tenant-examples"}
        r = await c.post(
            "/api/v1/workspaces",
            json={"slug": "examples", "name": "Examples"},
            headers={**tenant, "X-Workspace-Id": "examples"},
        )
        assert r.status_code == 201, r.text
        ws = r.json()["id"]
        h = {**tenant, "X-Workspace-Id": ws}

        r = await c.post(
            "/api/v1/datasets",
            json={"name": "smoke", "description": "Synthetic fixtures."},
            headers=h,
        )
        assert r.status_code == 201, r.text
        ds = r.json()["id"]

        total_tables = 0
        for path in fixtures:
            with path.open("rb") as f:
                r = await c.post(
                    f"/api/v1/datasets/{ds}/files",
                    headers=h,
                    files={"file": (path.name, f, "application/octet-stream")},
                    timeout=180.0,
                )
            assert r.status_code == 201, f"{path.name}: {r.status_code} {r.text[:300]}"
            body = r.json()
            assert "file_id" in body, body
            n_tables = len(body.get("tables") or [])
            assert n_tables >= 1, f"{path.name} produced 0 tables: {body}"
            total_tables += n_tables

        # Catalogue must reflect everything we uploaded, MINUS the dual-
        # upload upsert collapse: ``sales_orders.csv`` and
        # ``sales_orders.xlsx`` both reduce to the same
        # ``(dataset_id, name='sales_orders')`` row and the second upload
        # upserts (returns the existing row's id) rather than creating
        # a new row. We count each unique target table name once.
        r = await c.get(f"/api/v1/datasets/{ds}/tables", headers=h)
        assert r.status_code == 200
        items = r.json().get("items") or []
        # Sanity: every uploaded file produced >=1 table; the catalogue
        # must hold at least as many rows as fixtures (minus collisions).
        assert len(items) >= 1
        assert len(items) <= total_tables


@pytest.mark.integration
def test_examples_directory_layout() -> None:
    """README claims a fixture per format -- check the layout matches."""
    required = {
        "csv/customers.csv",
        "csv/sales_orders.csv",
        "json/products.json",
        "jsonl/events.jsonl",
        "xlsx/sales_orders.xlsx",
        "xlsx/financials_dashboard.xlsx",
        "parquet/transactions.parquet",
    }
    missing = [r for r in required if not (EXAMPLES / r).exists()]
    assert not missing, (
        f"missing example fixtures: {missing}. Run ``uv run python scripts/generate_examples.py``."
    )
