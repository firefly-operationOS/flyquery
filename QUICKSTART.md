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

## 5. Upload data

```bash
DS=$(curl -s -X POST http://localhost:8520/api/v1/datasets \
  -H 'Content-Type: application/json' \
  -H "X-Tenant-Id: demo" -H "X-Workspace-Id: $WS" \
  -d '{"name":"Sales 2026"}' | jq -r .id)
echo "dataset=$DS"

curl -s -X POST "http://localhost:8520/api/v1/datasets/$DS/files" \
  -H "X-Tenant-Id: demo" -H "X-Workspace-Id: $WS" \
  -F "file=@orders.csv"
```

## Asking questions

```bash
# Ask a question via POST /api/v1/query
curl -X POST http://localhost:8520/api/v1/query \
  -H 'Content-Type: application/json' \
  -H "X-Tenant-Id: demo" -H "X-Workspace-Id: $WS" \
  -d "{\"dataset_id\":\"$DS\",\"question\":\"what is total revenue by region?\"}"

# Stream the pipeline stages
curl -X POST -N http://localhost:8520/api/v1/query/stream \
  -H 'Content-Type: application/json' \
  -H "X-Tenant-Id: demo" -H "X-Workspace-Id: $WS" \
  -d "{\"dataset_id\":\"$DS\",\"question\":\"what is total revenue by region?\"}"

# Drill-down via conversation
CONV=$(curl -s -X POST http://localhost:8520/api/v1/conversations \
  -H "X-Tenant-Id: demo" -H "X-Workspace-Id: $WS" \
  -H 'Content-Type: application/json' -d '{}' | jq -r .id)
curl -X POST "http://localhost:8520/api/v1/conversations/$CONV/turn" \
  -H 'Content-Type: application/json' \
  -H "X-Tenant-Id: demo" -H "X-Workspace-Id: $WS" \
  -d "{\"dataset_id\":\"$DS\",\"question\":\"show me total revenue by region\"}"
curl -X POST "http://localhost:8520/api/v1/conversations/$CONV/turn" \
  -H 'Content-Type: application/json' \
  -H "X-Tenant-Id: demo" -H "X-Workspace-Id: $WS" \
  -d "{\"dataset_id\":\"$DS\",\"question\":\"now for orders in May 2026 only\"}"
```
