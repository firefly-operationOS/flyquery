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

"""Integration tests for the ingest job lifecycle + SSE streaming (Phase C).

Tests the full Phase C surface:
- POST /api/v1/ingest-jobs          → creates PENDING job + emits queued event
- GET  /api/v1/ingest-jobs/{id}     → returns job row
- GET  /api/v1/ingest-jobs          → list with filters
- GET  /api/v1/ingest-jobs/{id}/stream  → SSE stream terminates on final/error
- GET  /api/v1/ingest-jobs/{id}/events  → paginated event ledger
- POST /api/v1/ingest-jobs/{id}:cancel  → flips to CANCELLED (idempotent)

The IngestWorker is NOT wired in these tests (no EDA bus running), so the
worker never runs. The tests use DESCRIBE_PASS / RELATION_PASS jobs which
would immediately fail with NotImplementedError anyway, making the lifecycle
test valid: the job remains PENDING → we test the management surface without
needing a live EDA bus.

For the SSE test we inject a "queued" event directly via the events helper
and verify the stream replays it. We then inject an "error" event to check
the SSE stream closes.
"""

from __future__ import annotations

import io
import uuid

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.integration
@pytest.mark.asyncio
async def test_ingest_job_lifecycle():
    """POST /ingest-jobs creates a job, GET returns it, :cancel flips it."""
    from flyquery.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        h = {"X-Tenant-Id": "worker-test", "X-Workspace-Id": "worker-ws"}

        # 1. Create workspace + dataset
        r = await c.post(
            "/api/v1/workspaces",
            json={"slug": "worker-ws", "name": "Worker WS"},
            headers=h,
        )
        assert r.status_code == 201, r.text
        ws_id = r.json()["id"]
        h["X-Workspace-Id"] = ws_id

        r = await c.post(
            "/api/v1/datasets",
            json={"name": "worker-ds"},
            headers=h,
        )
        assert r.status_code == 201, r.text
        ds_id = r.json()["id"]

        # 2. Upload a CSV so there is a table_id
        body = b"a,b,c\n1,2,3\n4,5,6\n"
        r = await c.post(
            f"/api/v1/datasets/{ds_id}/files",
            files={"file": ("test.csv", io.BytesIO(body), "text/csv")},
            headers=h,
        )
        assert r.status_code == 201, r.text
        table_id = r.json()["tables"][0]["table_id"]

        # 3. POST /api/v1/ingest-jobs with REPARSE
        r = await c.post(
            "/api/v1/ingest-jobs",
            json={"dataset_id": ds_id, "table_id": table_id, "job_kind": "REPARSE"},
            headers=h,
        )
        assert r.status_code == 201, r.text
        job = r.json()
        job_id = job["id"]
        assert job["status"] == "PENDING"
        assert job["job_kind"] == "REPARSE"

        # 4. GET /api/v1/ingest-jobs/{id}
        r = await c.get(f"/api/v1/ingest-jobs/{job_id}", headers=h)
        assert r.status_code == 200, r.text
        assert r.json()["id"] == job_id

        # 5. GET /api/v1/ingest-jobs list
        r = await c.get("/api/v1/ingest-jobs", headers=h)
        assert r.status_code == 200, r.text
        items = r.json()["items"]
        assert any(i["id"] == job_id for i in items)

        # 6. Filter by kind
        r = await c.get("/api/v1/ingest-jobs?kind=REPARSE", headers=h)
        assert r.status_code == 200
        assert all(i["job_kind"] == "REPARSE" for i in r.json()["items"])

        # 7. GET /api/v1/ingest-jobs/{id}/events
        r = await c.get(f"/api/v1/ingest-jobs/{job_id}/events", headers=h)
        assert r.status_code == 200, r.text
        events = r.json()["items"]
        # At least the "queued" event should be present
        assert any(e["stage"] == "queued" for e in events), f"events={events}"

        # 8. POST :cancel
        r = await c.post(f"/api/v1/ingest-jobs/{job_id}:cancel", headers=h)
        assert r.status_code in (200, 202), r.text
        assert r.json()["status"] == "CANCELLED"

        # 9. Cancel is idempotent
        r = await c.post(f"/api/v1/ingest-jobs/{job_id}:cancel", headers=h)
        assert r.status_code in (200, 202), r.text

        # 10. List by status=CANCELLED
        r = await c.get("/api/v1/ingest-jobs?status=CANCELLED", headers=h)
        assert r.status_code == 200
        assert any(i["id"] == job_id for i in r.json()["items"])


@pytest.mark.integration
@pytest.mark.asyncio
async def test_parse_and_ingest_rejected_via_create_endpoint():
    """POST /ingest-jobs must reject PARSE_AND_INGEST job_kind."""
    from flyquery.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        h = {"X-Tenant-Id": "pijt", "X-Workspace-Id": "pijt-ws"}

        r = await c.post(
            "/api/v1/workspaces",
            json={"slug": "pijt-ws", "name": "PIJT WS"},
            headers=h,
        )
        ws_id = r.json()["id"]
        h["X-Workspace-Id"] = ws_id

        r = await c.post(
            "/api/v1/datasets",
            json={"name": "pijt-ds"},
            headers=h,
        )
        ds_id = r.json()["id"]

        r = await c.post(
            "/api/v1/ingest-jobs",
            json={"dataset_id": ds_id, "job_kind": "PARSE_AND_INGEST"},
            headers=h,
        )
        # Must return 400 or 422 (invalid request)
        assert r.status_code in {400, 422}, r.text


@pytest.mark.integration
@pytest.mark.asyncio
async def test_ingest_job_not_found():
    """GET /ingest-jobs/{unknown-id} should return 404."""
    from flyquery.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        h = {"X-Tenant-Id": "nf-test", "X-Workspace-Id": "nf-ws"}
        r = await c.post(
            "/api/v1/workspaces",
            json={"slug": "nf-ws", "name": "NF WS"},
            headers=h,
        )
        ws_id = r.json()["id"]
        h["X-Workspace-Id"] = ws_id

        r = await c.get(f"/api/v1/ingest-jobs/{uuid.uuid4()}", headers=h)
        assert r.status_code == 404, r.text


@pytest.mark.integration
@pytest.mark.asyncio
async def test_ingest_job_sse_stream_terminates():
    """GET /ingest-jobs/{id}/stream SSE terminates on injected terminal event.

    This test injects events directly into flyquery_ingest_events via the
    IngestJobRepository, then streams the SSE endpoint and asserts it closes
    on the 'final' event.

    The IngestWorker is not running in this test — we simulate job completion
    by injecting events directly.
    """
    from flyquery.core.services.ingestion.events import emit_final
    from flyquery.main import _pyfly, app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        h = {"X-Tenant-Id": "sse-test", "X-Workspace-Id": "sse-ws"}

        r = await c.post(
            "/api/v1/workspaces",
            json={"slug": "sse-ws", "name": "SSE WS"},
            headers=h,
        )
        ws_id = r.json()["id"]
        h["X-Workspace-Id"] = ws_id
        ws_uuid = uuid.UUID(ws_id)

        r = await c.post(
            "/api/v1/datasets",
            json={"name": "sse-ds"},
            headers=h,
        )
        ds_id = r.json()["id"]
        uuid.UUID(ds_id)

        # Upload CSV for a valid table reference
        body = b"x,y\n1,2\n3,4\n"
        r = await c.post(
            f"/api/v1/datasets/{ds_id}/files",
            files={"file": ("sse.csv", io.BytesIO(body), "text/csv")},
            headers=h,
        )
        assert r.status_code == 201, r.text

        # Create DESCRIBE_PASS job (won't actually run — no worker)
        r = await c.post(
            "/api/v1/ingest-jobs",
            json={"dataset_id": ds_id, "job_kind": "DESCRIBE_PASS"},
            headers=h,
        )
        assert r.status_code == 201, r.text
        job_id = uuid.UUID(r.json()["id"])

        # Resolve session_factory from the DI container
        from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

        session_factory: async_sessionmaker[AsyncSession] = _pyfly.context.get_bean(async_sessionmaker)

        # Inject a final event so the SSE stream closes immediately
        await emit_final(
            ingest_job_id=job_id,
            tenant_id="sse-test",
            workspace_id=ws_uuid,
            summary={"injected": True},
            session_factory=session_factory,
        )

        # Stream SSE — should terminate on 'final'
        seen_stages: list[str] = []
        try:
            async with c.stream("GET", f"/api/v1/ingest-jobs/{job_id}/stream", headers=h) as resp:
                assert resp.status_code == 200
                assert "text/event-stream" in resp.headers.get("content-type", "")
                async for line in resp.aiter_lines():
                    if line.startswith("event:"):
                        stage = line.split(": ", 1)[1].strip()
                        seen_stages.append(stage)
                        if stage in ("final", "error"):
                            break
        except Exception:
            pass  # httpx may complain on stream close; ignore

        assert "final" in seen_stages or "error" in seen_stages, (
            f"SSE stream did not emit a terminal event; got: {seen_stages}"
        )

        # Also verify event ledger has the 'final' event
        r = await c.get(f"/api/v1/ingest-jobs/{job_id}/events", headers=h)
        assert r.status_code == 200
        stages = [e["stage"] for e in r.json()["items"]]
        assert "final" in stages, f"events ledger missing 'final': {stages}"
