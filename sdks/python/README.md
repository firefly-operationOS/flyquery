# flyquery Python SDK

Auto-generated from `flyquery/openapi.json` via `openapi-generator-cli`.

## Install

```bash
pip install flyquery-sdk
```

Or from source (sibling-checkout):

```bash
pip install -e ./sdks/python
```

## Quick start

```python
from flyquery_sdk import ApiClient, Configuration
from flyquery_sdk.api import WorkspacesApi

config = Configuration(host="http://localhost:8520")
client = ApiClient(config)
ws_api = WorkspacesApi(client)
ws = ws_api.create_workspace(
    workspace_create={"slug": "alpha", "name": "Alpha"},
    x_tenant_id="demo", x_workspace_id="alpha",
)
print(ws.id)
```

## Regenerating

The SDK regenerates whenever `openapi.json` changes. Run `task sdk:python` from the repo root.

## License

Apache-2.0 (the SDK is Apache; the upstream flyquery service is proprietary).
