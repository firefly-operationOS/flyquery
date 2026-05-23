#!/usr/bin/env python
# Copyright 2026 Firefly Software Solutions Inc
"""Bulk file ingestion + per-file error reporting.

Demonstrates how the bulk endpoint surfaces per-file outcomes when
a mix of valid + invalid files is uploaded -- the failed files
DON'T abort the bulk.

Usage::

    uv run python sdks/python/examples/02_bulk_ingest.py
"""

from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path

from flyquery_sdk import FlyqueryClient

ROOT_FIXTURES = Path(__file__).resolve().parent.parent.parent.parent / "examples"


async def main() -> None:
    async with FlyqueryClient(
        base_url="http://127.0.0.1:8520",
        tenant_id="bulk-demo",
        workspace_id="bulk1",
    ) as fly:
        ws = await fly.find_or_create_workspace("bulk1", name="Bulk Demo")
        fly._workspace_id = str(ws.id)
        fly._http.headers["X-Workspace-Id"] = str(ws.id)
        fly._api_client.default_headers["X-Workspace-Id"] = str(ws.id)

        ds = await fly.find_or_create_dataset("bulk_demo", description="Bulk demo")

        # Mix of valid fixtures + a deliberately broken file so the
        # per-item error path is exercised.
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as bad:
            bad.write(b"this,is\nnot,parseable,csv,malformed\xff\xfe\x00")
            broken_path = Path(bad.name)

        paths = [
            ROOT_FIXTURES / "csv" / "customers.csv",
            ROOT_FIXTURES / "csv" / "sales_orders.csv",
            broken_path,  # invalid -- expect status=FAILED for this one
            ROOT_FIXTURES / "json" / "products.json",
        ]
        outcome = await fly.upload_bulk(str(ds.id), paths)

        print(f"summary: {outcome.succeeded}/{outcome.total_files} succeeded ({outcome.failed} failed)")
        for r in outcome.results:
            tag = "✓" if r.status == "OK" else "✗"
            print(f"  {tag} {r.original_filename}")
            if r.status == "OK":
                for t in r.tables:
                    print(f"       └─ {t.name} ({t.n_columns} cols)")
            else:
                print(f"       └─ ERROR: {r.error}")


if __name__ == "__main__":
    asyncio.run(main())
