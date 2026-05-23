# flyquery — Security

## Table of Contents

1. [Threat model summary](#1-threat-model-summary)
2. [Tenant and workspace isolation](#2-tenant-and-workspace-isolation)
3. [Postgres role split and RLS](#3-postgres-role-split-and-rls)
4. [Agent token model](#4-agent-token-model)
5. [Scope catalog and enforcement](#5-scope-catalog-and-enforcement)
6. [AST firewall](#6-ast-firewall)
7. [PII scanning and sample protection](#7-pii-scanning-and-sample-protection)
8. [Object storage security](#8-object-storage-security)
9. [Upload security](#9-upload-security)
10. [Audit trail](#10-audit-trail)
11. [Encryption](#11-encryption)
12. [Future: per-workspace KMS/CMEK](#12-future-per-workspace-kmscmek)

---

## 1. Threat model summary

flyquery is a multi-tenant service. The primary threats it defends against:

| Threat | Defence |
|--------|---------|
| Cross-tenant data leak | Postgres RLS on every multi-tenant table |
| Cross-workspace data leak | RLS workspace filter + agent-token workspace allowlist |
| Malicious uploaded file (zip bomb, polyglot, billion-laughs JSON) | Size cap + magic-byte format verify + per-reader hardening |
| Generated SQL exfiltrates host filesystem | AST firewall + DuckDB read-only mode + allowlisted extensions only |
| PII leaks via schema samples | PIIScanner gate before sample persistence; late-tag scrub |
| DuckDB cross-request contamination | New in-process connection per request; no shared ATTACH state |
| Object storage misconfig exposes raw URIs | Presigned URLs only; TTL-scoped; per-tenant prefix isolation |
| GDPR purge race with in-flight queries | Cooperative cancel + 30-day tombstone window |
| Atomic snapshot interrupted mid-flight | PARTIAL → READY only after stage 10; no half-ingested window |
| Schema KB blowup (10k+ columns) | `ingest_policy_json` include/exclude; embedding budget cap |

---

## 2. Tenant and workspace isolation

Every domain entity in flyquery carries two isolation keys:

```
tenant_id   — customer tenant slug (e.g. "acme")
workspace_id — workspace slug within the tenant (e.g. "analytics")
```

These are sourced from request headers `X-Tenant-Id` and `X-Workspace-Id`,
validated by `TenantContextMiddleware`, and bound to the Postgres session via
GUCs before any query executes:

```sql
SET LOCAL app.tenant_id = 'acme';
SET LOCAL app.workspace_id = 'analytics';
```

RLS policies on every table enforce that rows outside the current
`(tenant_id, workspace_id)` are invisible and unwritable. An application query
that attempts to read another tenant's data returns 0 rows — not an error —
because RLS filters silently.

---

## 3. Postgres role split and RLS

### Two required roles

| Role | BYPASSRLS | Purpose |
|------|-----------|---------|
| `flyquery_admin` | Yes | Alembic migrations, cross-workspace workers, retention sweeps |
| `flyquery_app` | No | All request-scoped database operations |

`flyquery_app` is the role in `FLYQUERY_DATABASE_URL` (the runtime URL).
`flyquery_admin` is the role in `FLYQUERY_DATABASE_URL_ADMIN` (migrations only).

**Never use `flyquery_admin` for request-scoped queries.** A misconfiguration
that uses the admin URL for the app URL silently bypasses RLS in production.

### FORCE ROW LEVEL SECURITY

All `flyquery_*` tables are created with:

```sql
ALTER TABLE flyquery_<name> ENABLE ROW LEVEL SECURITY;
ALTER TABLE flyquery_<name> FORCE ROW LEVEL SECURITY;
```

`FORCE ROW LEVEL SECURITY` ensures that even the table owner is subject to
policies. Without FORCE, a superuser or owner connection would bypass the
policies.

### Standard RLS policy shape

```sql
CREATE POLICY flyquery_<table>_tenant_workspace
    ON flyquery_<table>
    USING (
        tenant_id   = current_setting('app.tenant_id')
        AND workspace_id = current_setting('app.workspace_id')
    );
```

Postgres auto-derives `WITH CHECK = USING` when only `USING` is specified,
so cross-scope INSERTs are blocked outright.

### Special policies

`flyquery_workspaces`:
```sql
USING (tenant_id = current_setting('app.tenant_id')
       AND id = current_setting('app.workspace_id'))
```

`flyquery_agent_tokens`:
```sql
USING (tenant_id = current_setting('app.tenant_id'))
```
Workspace scope is enforced in application code against `workspace_allowlist_json`.

### Testing RLS

In integration tests (testcontainers), the default `test` Postgres user is
SUPERUSER (BYPASSRLS). Tests that validate isolation must create a non-superuser
`flyquery_app` role inside the container:

```sql
CREATE ROLE flyquery_app LOGIN PASSWORD 'test';
GRANT CONNECT ON DATABASE flyquery TO flyquery_app;
-- grant table permissions...
```

See `postgres_test_role_bypasses_rls` memory for the full recipe.

---

## 4. Agent token model

Agent tokens enable non-human callers (pipelines, other services, MCP tools)
to interact with flyquery without JWT.

**Format**: `agt_<8hex>_<32hex>`
- The `agt_<8hex>` prefix is the public lookup key (stored in clear).
- The `<32hex>` suffix is the secret; stored as `SHA-256(token)` in the
  database.

**Verification** (`AgentTokenService.verify`):
1. Extract prefix from the `X-Agent-Token` header.
2. Load the token row by prefix.
3. `secrets.compare_digest(SHA-256(presented_token), stored_hash)`.
4. Check `expires_at` (if set).
5. Check rate limit via per-token sliding 60-second counter.
6. Check `workspace_allowlist_json` vs `X-Workspace-Id`.
7. Return verified token record or raise `401 unauthorized`.

**Token fields** that affect scope:
- `scopes_json` — list of granted scope strings.
- `workspace_allowlist_json` — restricts to listed workspaces; null = all.
- `dataset_allowlist_json` — restricts to listed datasets; null = all.
- `rate_limit_rpm` — null or 0 = no limit.

`mark_used` writes are deduped to a 60-second window to avoid write amplification
on high-frequency agent calls.

---

## 5. Scope catalog and enforcement

The effective grant for any operation is the **intersection** of:

1. Token scopes (from `scopes_json`)
2. `workspace_allowlist_json`
3. `dataset_allowlist_json`
4. AST classification of the generated SQL
5. Target table kind

The executor refuses if any of these dimensions denies the operation.

**Table kind enforcement**:
- `UPLOADED` tables are read-only. Any INSERT/UPDATE/DELETE on an UPLOADED
  table is rejected regardless of scopes.
- `DERIVED` tables accept DML only under `flyquery.derived:write` scope.

**Direct SQL** (`POST /sql:execute`) requires **both**:
- Scope `flyquery.sql:execute`
- `workspace.allow_direct_sql = true`

If the workspace setting is `false`, the endpoint returns `422 Unprocessable`
even with the correct scope.

See [api-reference.md §7](api-reference.md#7-scope-catalog) for the full
scope list.

---

## 6. AST firewall

Every piece of SQL — whether generated by an AI agent or submitted directly —
passes through the AST firewall before execution.

### Rules (DuckDB dialect, via sqlglot + DuckDB parser)

| Rule | Effect on violation |
|------|-------------------|
| Single-statement only | `REJECTED_BY_FIREWALL` |
| No DDL (CREATE, DROP, ALTER, TRUNCATE) on any table | `REJECTED_BY_FIREWALL` |
| No INSERT/UPDATE/DELETE on UPLOADED tables | `REJECTED_BY_FIREWALL` |
| No DML on DERIVED tables without `flyquery.derived:write` | `REJECTED_BY_FIREWALL` |
| No references to tables outside the dataset_allowlist | `REJECTED_BY_FIREWALL` |
| No DuckDB extensions other than `httpfs`, `parquet`, `json`, `arrow` | `REJECTED_BY_FIREWALL` |
| No DuckDB functions that touch the host filesystem outside our prefix | `REJECTED_BY_FIREWALL` |
| No `COPY TO` or `EXPORT DATABASE` | `REJECTED_BY_FIREWALL` |

### DuckDB execution mode

The `DuckDBAdapter` opens a new in-process DuckDB connection per request in
**read-only mode** for ingested tables. This provides defence-in-depth: even
if the AST firewall misses a statement, DuckDB's read-only mode refuses any
writes to the Parquet files.

Only `httpfs`, `parquet`, `json`, and `arrow` extensions are loaded. The
`httpfs` extension is restricted to URLs matching the object storage prefix
configured in `FLYQUERY_OBJECT_STORE_BASE`.

### Double-check

After sqlglot AST classification, DuckDB parses the SQL a second time. If
DuckDB's parser disagrees with sqlglot's classification, the statement is
rejected with `error_code=AST_PARSE_CONFLICT`.

---

## 7. PII scanning and sample protection

### Pipeline placement

PII scanning has two gates:

1. **Stage 4 (sample)** — samples are tested before being persisted. A column
   that triggers a PII match at sampling time never has its values written to
   `sample_values_json`.

2. **Stage 8 (PII tag)** — the `PIIScanner` port classifies each column from
   `(name + description + sample_values)`. Sets `pii_tag` + `pii_source`.

### PII policies

Set globally via env vars or per-dataset via `ingest_policy_json`:

| Policy | `warn` | `redact` | `reject` |
|--------|--------|----------|---------|
| On PII detection | Log + continue | Purge `sample_values_json`; log | Set `is_active=false` on column; not queryable until reviewed |

### Late tag flip

If a human annotates `pii_tag` on a column that already has `sample_values_json`
persisted, the samples are scrubbed in-place in the same transaction:

```python
if update.pii_tag and update.pii_tag != "NONE":
    schema_object.sample_values_json = None
```

### PII in query results

`FLYQUERY_PII_POLICY_RESULTS` (default `warn`) applies to result rows that
pass through the explainer. At `warn`, a `pii_findings_json` field is
populated on the `flyquery_queries` row. At `redact`, matching cells are
replaced with `[REDACTED]` in the result preview.

---

## 8. Object storage security

### Per-tenant prefix isolation

All blobs are stored under `flyquery/{tenant_id}/{workspace_id}/`. A
misconfigured storage policy that grants broad bucket read access cannot expose
one tenant's files to another, because the prefix itself encodes the tenant
boundary. Object-store IAM policies should restrict to the service-account
key prefix.

### Presigned URLs

flyquery never returns raw storage URIs in API responses. All download links
are presigned URLs with a configurable TTL (`FLYQUERY_OBJECT_STORE_PRESIGN_TTL_S`,
default 86400 s = 24 h). The presigned URL:
- Is scoped to a single object key.
- Expires after TTL.
- Does not embed tenant credentials in a replayable form.

### Encryption at rest

Default: storage-native SSE (server-side encryption managed by the object
storage provider — S3 SSE-S3, GCS default encryption, Azure Storage Service
Encryption).

Per-workspace CMK/CMEK override: set `workspace.kms_key_uri` to a KMS key URI.
The `ObjectStore.put` call passes `kms_key_uri` to the adapter:
- S3: `ServerSideEncryption=SSE-KMS`, `SSEKMSKeyId=<key_arn>`
- GCS: `kmsKeyName` in the object metadata
- Azure: Customer-provided key header

See [§12](#12-future-per-workspace-kmscmek) for the roadmap.

---

## 9. Upload security

### Size caps

| Limit | Default | Config key |
|-------|---------|-----------|
| Per-file | 2 GiB | `FLYQUERY_MAX_FILE_MB` |
| Per-workspace total | 200 GiB | `FLYQUERY_MAX_WORKSPACE_GB` |

Files exceeding the per-file cap are rejected at the upload endpoint with
`413 Content Too Large` before bytes are written to object storage.

### Malicious archive defence

| Vector | Defence |
|--------|---------|
| Zip bomb | Decompressed-size check during decompression; capped at 2× the compressed size or `FLYQUERY_MAX_FILE_MB`, whichever is smaller |
| ZIP with multiple entries | Rejected immediately with `error_code=ZIP_MULTI_ENTRY` |
| Polyglot file (valid magic bytes for two formats) | Stage 1 verifies magic bytes match declared extension; mismatch → `FORMAT_MISMATCH` |
| Billion-laughs JSON | DuckDB parser memory cap (`FLYQUERY_DUCKDB_MEMORY_LIMIT`) + statement timeout; worker cgroup memory limit |

### GDPR purge

`DELETE /workspaces/{id}:purge` initiates a hard-delete sequence:
1. Workspace marked as tombstoned (30-day grace period).
2. After 30 days, a background job cooperatively cancels all in-flight queries
   for the workspace.
3. All `{tenant_id}/{workspace_id}/` object-storage keys are deleted.
4. All `flyquery_*` rows for the workspace are hard-deleted from Postgres.

The 30-day tombstone allows accidental-purge recovery before bytes vanish.

---

## 10. Audit trail

Every significant mutation is recorded in `flyquery_audit_events` (append-only,
never updated or deleted):

| Event type | What triggers it |
|------------|-----------------|
| `workspace.created` / `workspace.updated` / `workspace.purge_scheduled` | Workspace lifecycle |
| `dataset.created` / `dataset.archived` | Dataset lifecycle |
| `file.uploaded` / `file.deleted` | Upload lifecycle |
| `snapshot.ready` | Stage 10 of ingestion |
| `schema_object.annotated` | Human annotation |
| `relation.approved` / `relation.rejected` | Relation lifecycle |
| `agent_token.created` / `agent_token.revoked` | Token lifecycle |
| `query.executed` / `query.rejected_by_firewall` | Query lifecycle |
| `sql.executed` | Direct SQL lifecycle |
| `pii.tag_set` / `pii.samples_redacted` | PII events |

Access the audit trail via `GET /api/v1/audit` (scope `flyquery.audit:read`).
All events carry `(tenant_id, workspace_id, actor, created_at)`.

---

## 11. Encryption

| What | How | Configurable? |
|------|-----|--------------|
| Data at rest in object storage | Storage-native SSE | Yes, via `workspace.kms_key_uri` |
| Data in transit | TLS (terminated at the load balancer or service mesh) | Deployment responsibility |
| Database at rest | Postgres host-level encryption (deployment responsibility) | No flyquery-specific config |
| Agent token secrets | SHA-256 hash of the token; never stored in clear | No |
| Presigned URL secrets | Storage-provider managed; short-lived | TTL via `FLYQUERY_OBJECT_STORE_PRESIGN_TTL_S` |

flyquery does not own connection strings to customer databases (no DSN model),
so there is no DSN encryption requirement to address.

---

## 12. Future: per-workspace KMS/CMEK

v0 supports setting `workspace.kms_key_uri` to override storage-native SSE
with a customer-managed key. However, the key is used only for new
`ObjectStore.put` calls after the field is set; existing blobs are not
re-encrypted automatically.

v1+ planned work:
- **Key rotation** — re-encrypt all blobs for a workspace under a new key URI.
- **KEK/DEK envelope** — derive a per-object DEK from the workspace KEK so
  that key revocation can be implemented via DEK tombstoning without re-
  encrypting every blob.
- **GDPR-safe key revocation** — revoking the workspace KMS key logically
  destroys all blob contents without deleting the bytes, satisfying GDPR
  erasure requirements for encrypted data.
