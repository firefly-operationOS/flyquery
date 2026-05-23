# Copyright 2026 Firefly Software Solutions Inc
"""Ergonomic high-level Python client for flyquery.

The generated ``flyquery_sdk.api.*`` classes are accurate but verbose
-- every call needs explicit ``x_tenant_id`` + ``x_workspace_id``
arguments, separate API instances, and the bulk + batch endpoints
need hand-built multipart bodies (openapi-generator can't see the
multi-part ``files`` field). This module wraps the generated API
into a single ``FlyqueryClient`` that:

* Carries the tenant + workspace context once per client (no
  repeating headers per call).
* Exposes ergonomic helpers: ``upload(path)``,
  ``upload_directory(path)``, ``upload_bulk(paths)``,
  ``ask(question)``, ``ask_batch(questions)``,
  ``find_workspace(slug)``, ``find_dataset(name)``.
* Returns the same generated Pydantic models so callers keep full
  type safety + can drop down to the underlying ``ApiClient`` when
  they need a knob the wrapper doesn't expose.

Threading
---------
The wrapper is async-first (matches the generated client). Sync
mirrors (``upload_sync`` / ``ask_sync``) wrap ``asyncio.run`` for
notebooks, CLIs, and tests that don't want to manage a loop.
"""

from __future__ import annotations

import asyncio
import json as _json
import mimetypes
from pathlib import Path
from typing import Any
from urllib.parse import quote

import httpx

from flyquery_sdk.api.datasets_api import DatasetsApi
from flyquery_sdk.api.files_api import FilesApi
from flyquery_sdk.api.query_api import QueryApi
from flyquery_sdk.api.tables_api import TablesApi
from flyquery_sdk.api.workspaces_api import WorkspacesApi
from flyquery_sdk.api_client import ApiClient
from flyquery_sdk.configuration import Configuration

__all__ = ["FlyqueryClient", "BulkFileResult", "BulkUploadOutcome"]


# Generated model re-exports so callers don't have to chase the deep
# ``flyquery_sdk.models.*`` paths just to access the response shape.
from flyquery_sdk.models.answer_response import AnswerResponse  # noqa: E402
from flyquery_sdk.models.batch_query_response import BatchQueryResponse  # noqa: E402
from flyquery_sdk.models.batch_query_result_item import (  # noqa: E402, F401  -- re-exported
    BatchQueryResultItem,
)
from flyquery_sdk.models.bulk_file_result import BulkFileResult  # noqa: E402
from flyquery_sdk.models.bulk_file_upload_response import BulkFileUploadResponse  # noqa: E402
from flyquery_sdk.models.dataset_read import DatasetRead  # noqa: E402
from flyquery_sdk.models.file_upload_response import FileUploadResponse  # noqa: E402
from flyquery_sdk.models.workspace_read import WorkspaceRead  # noqa: E402

BulkUploadOutcome = BulkFileUploadResponse


class FlyqueryClient:
    """Tenant + workspace-scoped flyquery client.

    Construct once per ``(tenant_id, workspace_id)`` pair; reuse for
    every call within that scope. Async-first; ``__aenter__`` /
    ``__aexit__`` close the underlying HTTP pool.

    Examples
    --------
    Single-file upload + a query::

        async with FlyqueryClient(
            base_url="https://flyquery.example.com",
            tenant_id="acme",
            workspace_id="finance",
        ) as fly:
            ds = await fly.find_or_create_dataset("orders", description="...")
            await fly.upload(ds.id, "examples/csv/sales_orders.csv")
            ans = await fly.ask(ds.id, "What's the total revenue?")
            print(ans.sql, ans.preview)

    Bulk upload + batch query::

        async with FlyqueryClient(...) as fly:
            outcome = await fly.upload_directory(ds.id, "examples/")
            print(f"uploaded {outcome.succeeded}/{outcome.total_files}")

            batch = await fly.ask_batch(
                ds.id,
                ["Top 5 customers?", "Total revenue?", "Refund rate?"],
            )
            for r in batch.results:
                print(r.status, r.sql)
    """

    def __init__(
        self,
        *,
        base_url: str,
        tenant_id: str,
        workspace_id: str,
        agent_token: str | None = None,
        timeout: float = 120.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._tenant_id = tenant_id
        self._workspace_id = workspace_id
        self._agent_token = agent_token

        config = Configuration(host=self._base_url)
        self._api_client = ApiClient(config)
        # The OpenAPI generator doesn't model the tenant + workspace +
        # agent-token headers (the server reads them out-of-band from
        # the request rather than as declared per-route parameters),
        # so we set them as ApiClient defaults so every generated
        # method that calls ``api_client.call_api(...)`` carries them.
        self._api_client.default_headers["X-Tenant-Id"] = self._tenant_id
        self._api_client.default_headers["X-Workspace-Id"] = self._workspace_id
        if self._agent_token:
            self._api_client.default_headers["X-Agent-Token"] = self._agent_token
        self._workspaces = WorkspacesApi(self._api_client)
        self._datasets = DatasetsApi(self._api_client)
        self._files = FilesApi(self._api_client)
        self._tables = TablesApi(self._api_client)
        self._query = QueryApi(self._api_client)

        # Separate raw httpx client for the multipart bulk + custom
        # endpoints the generated client can't model.
        headers = {
            "X-Tenant-Id": self._tenant_id,
            "X-Workspace-Id": self._workspace_id,
        }
        if self._agent_token:
            headers["X-Agent-Token"] = self._agent_token
        self._http = httpx.AsyncClient(
            base_url=self._base_url,
            headers=headers,
            timeout=timeout,
        )

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def __aenter__(self) -> FlyqueryClient:
        return self

    async def __aexit__(self, *exc: Any) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self._http.aclose()
        await self._api_client.close()

    # ------------------------------------------------------------------
    # Accessors -- drop down to raw generated API when needed
    # ------------------------------------------------------------------

    @property
    def workspaces(self) -> WorkspacesApi:
        return self._workspaces

    @property
    def datasets(self) -> DatasetsApi:
        return self._datasets

    @property
    def files(self) -> FilesApi:
        return self._files

    @property
    def tables(self) -> TablesApi:
        return self._tables

    @property
    def query(self) -> QueryApi:
        return self._query

    # ------------------------------------------------------------------
    # Workspace + dataset helpers
    # ------------------------------------------------------------------

    async def find_or_create_workspace(
        self,
        slug: str,
        *,
        name: str | None = None,
    ) -> WorkspaceRead:
        """Idempotent workspace lookup-or-create by slug."""
        try:
            return await self._workspaces.read_by_slug(slug=slug)
        except Exception:  # noqa: BLE001  -- 404 -> create
            from flyquery_sdk.models.workspace_create import WorkspaceCreate

            return await self._workspaces.create(
                workspace_create=WorkspaceCreate(slug=slug, name=name or slug),
            )

    async def find_or_create_dataset(
        self,
        name: str,
        *,
        description: str | None = None,
    ) -> DatasetRead:
        """Idempotent dataset lookup-or-create by ``(workspace, name)``."""
        try:
            return await self._datasets.read_by_name(name=name)
        except Exception:  # noqa: BLE001  -- 404 -> create
            from flyquery_sdk.models.dataset_create import DatasetCreate

            return await self._datasets.create(
                dataset_create=DatasetCreate(name=name, description=description),
            )

    # ------------------------------------------------------------------
    # File ingestion (single + bulk + directory)
    # ------------------------------------------------------------------

    async def upload(
        self,
        dataset_id: str,
        path: str | Path,
    ) -> FileUploadResponse:
        """Upload a single file to ``dataset_id``.

        Uses raw httpx because the generated client's
        ``upload_file`` requires a ``StrictBytes`` object that's
        finicky to construct from a Path.
        """
        p = Path(path)
        content_type = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
        files = {"file": (p.name, p.read_bytes(), content_type)}
        r = await self._http.post(
            f"/api/v1/datasets/{quote(dataset_id)}/files",
            files=files,
        )
        r.raise_for_status()
        return FileUploadResponse.model_validate(r.json())

    async def upload_bulk(
        self,
        dataset_id: str,
        paths: list[str | Path],
    ) -> BulkFileUploadResponse:
        """Upload many files in a single bulk multipart request.

        Per-file failures do NOT abort the bulk -- inspect the
        ``results[i].status`` field. Aggregate counts are in
        ``total_files`` / ``succeeded`` / ``failed``.
        """
        files = []
        for raw in paths:
            p = Path(raw)
            content_type = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
            files.append(("files", (p.name, p.read_bytes(), content_type)))
        r = await self._http.post(
            f"/api/v1/datasets/{quote(dataset_id)}/files:bulk",
            files=files,
        )
        r.raise_for_status()
        return BulkFileUploadResponse.model_validate(r.json())

    async def upload_directory(
        self,
        dataset_id: str,
        directory: str | Path,
        *,
        recursive: bool = True,
        extensions: tuple[str, ...] = (
            ".csv",
            ".tsv",
            ".json",
            ".jsonl",
            ".xlsx",
            ".xls",
            ".ods",
            ".parquet",
            ".avro",
            ".orc",
            ".arrow",
            ".feather",
        ),
    ) -> BulkFileUploadResponse:
        """Walk ``directory`` and bulk-upload every matching file."""
        root = Path(directory)
        if not root.is_dir():
            raise NotADirectoryError(root)
        glob = "**/*" if recursive else "*"
        paths = sorted(p for p in root.glob(glob) if p.is_file() and p.suffix.lower() in extensions)
        if not paths:
            raise FileNotFoundError(f"no ingestable files under {root} (extensions={extensions})")
        return await self.upload_bulk(dataset_id, paths)

    # ------------------------------------------------------------------
    # NL query (single + batch)
    # ------------------------------------------------------------------

    async def ask(
        self,
        dataset_id: str,
        question: str,
        *,
        conversation_id: str | None = None,
    ) -> AnswerResponse:
        """Run a single NL question through the query pipeline."""
        payload: dict[str, Any] = {"question": question, "dataset_id": dataset_id}
        if conversation_id is not None:
            payload["conversation_id"] = conversation_id
        r = await self._http.post(
            "/api/v1/query",
            content=_json.dumps(payload),
            headers={"Content-Type": "application/json"},
        )
        r.raise_for_status()
        return AnswerResponse.model_validate(r.json())

    async def ask_batch(
        self,
        dataset_id: str,
        questions: list[str],
    ) -> BatchQueryResponse:
        """Run many NL questions in parallel against ``dataset_id``."""
        payload = {
            "queries": [{"question": q, "dataset_id": dataset_id} for q in questions],
        }
        r = await self._http.post(
            "/api/v1/query:batch",
            content=_json.dumps(payload),
            headers={"Content-Type": "application/json"},
        )
        r.raise_for_status()
        return BatchQueryResponse.model_validate(r.json())

    # ------------------------------------------------------------------
    # Sync mirrors -- for notebooks, CLIs, tests
    # ------------------------------------------------------------------

    def upload_sync(self, dataset_id: str, path: str | Path) -> FileUploadResponse:
        return asyncio.run(self.upload(dataset_id, path))

    def upload_bulk_sync(
        self,
        dataset_id: str,
        paths: list[str | Path],
    ) -> BulkFileUploadResponse:
        return asyncio.run(self.upload_bulk(dataset_id, paths))

    def ask_sync(self, dataset_id: str, question: str) -> AnswerResponse:
        return asyncio.run(self.ask(dataset_id, question))

    def ask_batch_sync(self, dataset_id: str, questions: list[str]) -> BatchQueryResponse:
        return asyncio.run(self.ask_batch(dataset_id, questions))
