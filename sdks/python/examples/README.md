# flyquery-sdk examples

Runnable scripts that exercise the [`FlyqueryClient`](../flyquery_sdk/client.py)
ergonomic wrapper. Every script targets ``http://127.0.0.1:8520`` so
spin up the service first:

```bash
docker compose up -d postgres redis minio ollama
uv sync
uv run alembic upgrade head
uv run uvicorn flyquery.main:app --host 127.0.0.1 --port 8520 &
```

| File | What it demonstrates |
|------|----------------------|
| `01_quickstart.py` | Idempotent workspace + dataset setup, `upload_directory` against the repo's synthetic fixtures, `ask_batch` with three NL questions. |
| `02_bulk_ingest.py` | Bulk upload mixing valid fixtures + an intentionally malformed file — proves per-file failures surface as `BulkFileResult.status="FAILED"` + `.error` without aborting the batch. |

Add your own scripts under this directory; the README is the only
file CI looks at when checking the example layout.
