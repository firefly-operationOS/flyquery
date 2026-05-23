# QUICKSTART

This walks the first call against a local flyquery v0.1 (Plan 1).

## 1. Boot the stack

```bash
docker compose up -d postgres redis minio
task install
task migrate
task serve   # listens on :8520
```

## 2. Sanity checks

```bash
curl http://localhost:8520/actuator/health
curl http://localhost:8520/api/v1/version
```

## 3. Create a workspace + dataset

```bash
WS=$(curl -s -X POST http://localhost:8520/api/v1/workspaces \
  -H 'Content-Type: application/json' \
  -H 'X-Tenant-Id: demo' -H 'X-Workspace-Id: alpha' \
  -d '{"slug":"alpha","name":"Alpha"}' | jq -r .id)
echo "workspace=$WS"

curl -s -X POST http://localhost:8520/api/v1/datasets \
  -H 'Content-Type: application/json' \
  -H "X-Tenant-Id: demo" -H "X-Workspace-Id: $WS" \
  -d '{"name":"Sales 2026"}'
```

## 4. Mint an agent token

```bash
TOK=$(curl -s -X POST http://localhost:8520/api/v1/agent-tokens \
  -H 'Content-Type: application/json' \
  -H "X-Tenant-Id: demo" -H "X-Workspace-Id: $WS" \
  -d '{"name":"dev","scopes":["flyquery.datasets:read","flyquery.query:read"],"workspace_allowlist":["'$WS'"]}' \
  | jq -r .token)
echo "token=$TOK"   # agt_<8hex>_<32hex>
```

## 5. What you cannot do yet

- Upload files (`POST /datasets/{id}/files`) — ships in Plan 2.
- Ask `/query` — ships in Plan 3.

See `docs/superpowers/plans/` for the next plans.
