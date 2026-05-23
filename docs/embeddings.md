# Embeddings

flyquery's grounding pipeline mixes **BM25** full-text retrieval over
`flyquery_schema_objects.content_tsv` with **dense vector** retrieval
over the `embedding` column. The embedding provider is pluggable --
the implementation lives in
`src/flyquery/core/services/retrieval/embedder.py` and delegates the
actual provider call to
[`fireflyframework_agentic.embeddings`](https://github.com/fireflyframework/fireflyframework-agentic),
so any embedder shipped there is available here.

## Supported providers

| Provider | Env var | Default model | Native dim |
|---|---|---|---|
| `ollama`  | (none -- runs locally via docker compose) | `nomic-embed-text` | 768 |
| `openai`  | `OPENAI_API_KEY` | `text-embedding-3-small` | 1536 (configurable to 256-3072) |
| `cohere`  | `COHERE_API_KEY` | `embed-english-v3.0` | 1024 |
| `voyage`  | `VOYAGE_API_KEY` | `voyage-3` | 1024 |
| `azure`   | `AZURE_OPENAI_*`  | deployment-specific | depends on deployment |
| `google`  | `GOOGLE_APPLICATION_CREDENTIALS` | `text-embedding-004` | 768 |
| `mistral` | `MISTRAL_API_KEY` | `mistral-embed` | 1024 |
| `bedrock` | AWS creds | `amazon.titan-embed-text-v2:0` | 1024 |
| `null`    | (none) | -- | 0 |

The default for a fresh `docker compose up` is **`ollama` +
`nomic-embed-text`** so the stack works end-to-end without an
external API key. The `ollama` service in
[`docker-compose.yml`](../docker-compose.yml) exposes
`http://localhost:11552` to the host; pull the model with
`docker compose exec ollama ollama pull nomic-embed-text` if you
want to warm it before the first ingest.

## Configuration

All four knobs live in `FlyquerySettings` (see
[`src/flyquery/config.py`](../src/flyquery/config.py)) and can be
overridden via env var with the `FLYQUERY_` prefix:

```bash
FLYQUERY_EMBEDDING_PROVIDER=ollama       # one of the table above
FLYQUERY_EMBEDDING_MODEL=nomic-embed-text
FLYQUERY_EMBEDDING_NATIVE_DIM=768        # provider's native output dim
FLYQUERY_EMBEDDING_DIMENSIONS=1536       # column dim (zero-padded if larger)
FLYQUERY_EMBEDDING_BASE_URL=http://localhost:11552   # Ollama endpoint
```

### Column dim and zero-padding

The schema column is `vector(<embedding_dimensions>)` (default 1536,
matching the canon migration). When the provider's native vector is
smaller, the persistence helper **zero-pads** to the column dim.
Cosine similarity is preserved across the padding because the extra
zero coordinates add zero to both the dot product and the L2 norms;
`ORDER BY embedding <=> :query_vec` rankings are stable.

When the provider's native dim is **larger** than the column dim,
the helper truncates -- this is rare (only OpenAI configured with a
non-default dim) and information loss is documented in the warning
log.

### Graceful degradation

If the configured provider is unreachable (Ollama not running,
missing API key, network outage, etc.) the factory returns a
**`NullEmbedder`** rather than raising. The embed stage still
refreshes `content_tsv` so BM25 retrieval keeps working -- the
grounding agent uses BM25 as its first pass and falls back to
vector reranking only when an embedding exists. The pipeline
**never fails** because of an embedding problem.

## Async + sync API

`Embedder` is async-first. For CLIs / notebooks / sync test
helpers, each implementation also exposes `embed_sync` /
`embed_batch_sync` that wrap `asyncio.run` -- safe to call from any
thread without a running event loop.

```python
from flyquery.config import FlyquerySettings
from flyquery.core.services.retrieval.embedder import build_embedder

settings = FlyquerySettings()
e = build_embedder(settings)

# Async (the path used by the embed stage)
vec = await e.embed("activos totales")
batch = await e.embed_batch(["activos", "pasivo", "patrimonio"])

# Sync (for tools)
vec = e.embed_sync("activos totales")
```

## Tests

* Unit -- [`tests/unit/test_embedder.py`](../tests/unit/test_embedder.py)
  covers Null fallback, FireflyEmbedder padding (smaller / exact /
  larger native dim), batch + empty-batch paths, exception ->
  None fallback, sync helpers, and the build_embedder factory's
  behavior on null / unknown / missing-API-key / Ollama paths.
* Integration -- the stage runs against a real Ollama server in
  `tests/integration/test_e2e_*.py`; if the Ollama container is not
  up, the assertions on `embeddings_written>0` are skipped (the
  pipeline still passes via BM25).
