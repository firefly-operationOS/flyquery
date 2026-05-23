<div align="center">

<img src="../../docs/assets/logo.png" alt="flyquery" width="380" />

### **Java SDK** &nbsp;&middot;&nbsp; Spring Boot 3.5.9 &nbsp;&middot;&nbsp; Java 25 &nbsp;&middot;&nbsp; WebFlux

</div>

---

Spring-Boot-native Java client for the
[flyquery](https://github.com/firefly-operationOS/flyquery) Tabular
Intelligence service — Text-to-SQL over user-uploaded structured
files.

- **Java 25** (LTS) / **Spring Boot 3.5.9** / **Spring Framework 6.2**.
- **Reactive HTTP client** built on `WebClient` + Reactor Netty —
  returns `Mono<T>` for unary methods and is ready to compose into
  any WebFlux pipeline.
- Carries the firefly four-header wire contract
  (`X-Tenant-Id` / `X-Workspace-Id` / `X-Correlation-Id` /
  `X-Agent-Token`) on every outbound request.
- **18 split API classes** under `com.firefly.flyquery.api.*` — one
  per resource family (workspaces, datasets, files, tables, schema,
  relations, semantic, glossary, examples, query, conversations,
  ingest, sql, agent-tokens, meta, agent-query, agent-sql,
  agent-examples).
- `groupId = com.firefly`, `artifactId = flyquery-sdk`. Apache-2.0.
- Auto-generated from `flyquery/openapi.json` via
  [`openapi-generator-cli`](https://openapi-generator.tech/).

## Wire-contract compatibility

Compatible with **flyquery service version `26.5.x`**.

| SDK | Service |
|-----|---------|
| `26.5.4` | `26.5.x` |

## Install

```xml
<dependency>
    <groupId>com.firefly</groupId>
    <artifactId>flyquery-sdk</artifactId>
    <version>26.5.4</version>
</dependency>
```

The SDK declares `spring-boot-starter-webflux` + `reactor-netty-http`
as compile dependencies, so a Spring Boot 3.5.x WebFlux application
picks up everything it needs transitively.

If you aren't using Spring Boot as your parent, import the BOM
explicitly:

```xml
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-dependencies</artifactId>
            <version>3.5.9</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>
```

## Quick start

```java
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.api.WorkspacesApi;
import com.firefly.flyquery.api.DatasetsApi;
import com.firefly.flyquery.api.QueryApi;
import com.firefly.flyquery.model.WorkspaceCreate;
import com.firefly.flyquery.model.DatasetCreate;
import com.firefly.flyquery.model.QueryRequest;
import reactor.core.publisher.Mono;

public class Demo {
    public static void main(String[] args) {
        ApiClient client = new ApiClient();
        client.setBasePath("https://flyquery.example.com");

        WorkspacesApi workspaces = new WorkspacesApi(client);
        DatasetsApi   datasets   = new DatasetsApi(client);
        QueryApi      query      = new QueryApi(client);

        // Reactive chain: create workspace → create dataset → ask a question
        Mono<Void> pipeline = workspaces
            .createWorkspace("demo", "alpha", new WorkspaceCreate()
                .slug("alpha")
                .name("Alpha"))
            .flatMap(ws -> datasets
                .createDataset("demo", ws.getId().toString(), new DatasetCreate()
                    .name("Sales 2026"))
                .flatMap(ds -> query.postQuery(
                    "demo",
                    ws.getId().toString(),
                    new QueryRequest()
                        .datasetId(ds.getId())
                        .question("what is total revenue by region?")))
                .doOnNext(answer -> {
                    System.out.println("SQL:    " + answer.getSql());
                    System.out.println("rows:   " + answer.getRowCount());
                    System.out.println("chart:  " + answer.getChartHint());
                }))
            .then();

        // Block at the edge of the world; in a real Spring WebFlux app you'd
        // chain this into the controller's Mono<ResponseEntity<…>>.
        pipeline.block();
    }
}
```

## Authentication

The flyquery service accepts either a user-tier JWT bearer (on
`/api/v1/*`) or an agent-tier `X-Agent-Token` (on `/api/v1/agent/*`):

```java
// User-tier (JWT)
client.setBearerToken("eyJhbGciOiJSUzI1NiIs...");

// Agent-tier (long-lived token agt_<8hex>_<32hex>)
client.addDefaultHeader("X-Agent-Token",
    "agt_aabbccdd_eeff00112233445566778899aabbccddeeff");
```

For agent-tier write endpoints, pass an idempotency key per request:

```java
client.addDefaultHeader("Idempotency-Key",
    java.util.UUID.randomUUID().toString());
```

The service deduplicates on the (token-prefix, key) pair for 24 hours.

## Streaming endpoints (SSE)

`/query/stream` and `/ingest-jobs/{id}/stream` are Server-Sent
Events. WebClient exposes them as a streaming `Flux`. The generated
methods return `Flux<ServerSentEvent<JsonNode>>`-style frames; the
event sequence is documented in
[`docs/pipeline.md`](https://github.com/firefly-operationOS/flyquery/blob/main/docs/pipeline.md):
`schema_linked → sql_generated → executed → explained → final`,
with an optional `clarification` frame when Grounding confidence is
below threshold.

## Error handling

All API methods complete with `WebClientResponseException` on
non-2xx responses. The service emits
[RFC 7807](https://www.rfc-editor.org/rfc/rfc7807) ProblemDetails;
parse `WebClientResponseException.getResponseBodyAsString()` to read
the `code`, `title`, `detail`, and per-field `errors[]`.

```java
query.postQuery("demo", workspaceId, req)
    .doOnError(WebClientResponseException.class, exc -> {
        int status = exc.getStatusCode().value();
        String body = exc.getResponseBodyAsString();
        // parse the RFC 7807 envelope; branch on body["code"]
    });
```

Common error codes:

| Status | `code`                      | Meaning                                            |
|--------|-----------------------------|----------------------------------------------------|
| 400    | `validation_error`          | Request body failed validation                     |
| 401    | `unauthenticated`           | Missing/invalid token                              |
| 403    | `scope_denied`              | Token scope insufficient for this operation        |
| 404    | `resource_not_found`        | Dataset / table / workspace not visible under RLS  |
| 409    | `conflict`                  | Slug / name collision (per workspace)              |
| 413    | `file_too_large`            | Upload exceeds `FLYQUERY_MAX_FILE_MB`              |
| 507    | `workspace_quota_exceeded`  | Workspace storage cap reached                      |
| 503    | `rate_limited`              | Per-token rate limit exceeded                      |

## API reference

The 18 API classes mirror the resource families exposed by the
service. Per-family methods cover the endpoints documented in
[`docs/api-reference.md`](https://github.com/firefly-operationOS/flyquery/blob/main/docs/api-reference.md).

| Java class                | Resource family                  |
|---------------------------|----------------------------------|
| `WorkspacesApi`           | `/api/v1/workspaces`             |
| `DatasetsApi`             | `/api/v1/datasets`               |
| `FilesApi`                | `/api/v1/datasets/{id}/files`    |
| `TablesApi`               | `/api/v1/tables`                 |
| `SchemaApi`               | `/api/v1/schema-objects`         |
| `RelationsApi`            | `/api/v1/datasets/{id}/relations`|
| `SemanticApi`             | `/api/v1/semantic/*`             |
| `GlossaryApi`             | `/api/v1/glossary`               |
| `ExamplesApi`             | `/api/v1/examples`               |
| `QueryApi`                | `/api/v1/query/*`                |
| `ConversationsApi`        | `/api/v1/conversations`          |
| `IngestApi`               | `/api/v1/ingest-jobs`            |
| `SqlApi`                  | `/api/v1/sql:execute`            |
| `AgentTokensApi`          | `/api/v1/agent-tokens`           |
| `MetaApi`                 | `/actuator/health`, `/version`   |
| `AgentQueryApi`           | `/api/v1/agent/query/*`          |
| `AgentSqlApi`             | `/api/v1/agent/sql:execute`      |
| `AgentExamplesApi`        | `/api/v1/agent/examples`         |

## Regenerating

The SDK is auto-generated from the service's OpenAPI spec. To pull
the latest:

```bash
# From the flyquery repo root:
task openapi-snapshot   # writes openapi.json
task sdk:java           # regenerates this directory
```

Hand-written files (`README.md`, `pom.xml`) are preserved across
regeneration via `.openapi-generator-ignore`.

## Development

```bash
cd sdks/java
mvn clean test          # unit + smoke tests
mvn javadoc:javadoc     # generated API docs under target/site/apidocs
```

## License

Apache-2.0. See [LICENSE](LICENSE).

The upstream **flyquery service** is proprietary and licensed
separately; the SDK is the Apache-licensed wire-protocol client.

## Links

- Service repo: <https://github.com/firefly-operationOS/flyquery>
- Documentation index: [`docs/README.md`](https://github.com/firefly-operationOS/flyquery/blob/main/docs/README.md)
- API reference: [`docs/api-reference.md`](https://github.com/firefly-operationOS/flyquery/blob/main/docs/api-reference.md)
- Wire payloads: [`docs/payload-reference.md`](https://github.com/firefly-operationOS/flyquery/blob/main/docs/payload-reference.md)
- Changelog: [`CHANGELOG.md`](https://github.com/firefly-operationOS/flyquery/blob/main/CHANGELOG.md)
