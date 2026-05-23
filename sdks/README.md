# flyquery SDKs

The SDKs in this directory are Apache-2.0-licensed (the upstream service is proprietary).

- **Python**: [`sdks/python/`](./python/) — install via `pip install flyquery-sdk` (or `pip install -e ./sdks/python` from a sibling checkout)
- **Java**: [`sdks/java/`](./java/) — install via Maven (`io.firefly:flyquery-sdk:26.5.2`)

Both are auto-generated from `openapi.json` via [`openapi-generator-cli`](https://openapi-generator.tech/). Regenerate via:

```bash
task openapi-snapshot
task sdk:python
task sdk:java
```
