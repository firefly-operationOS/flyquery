# flyquery Java SDK

Auto-generated from `flyquery/openapi.json` via `openapi-generator-cli`.

**Runtime:** Java 25 | **HTTP client:** Spring WebFlux (reactive) | **Spring Boot:** 3.5.9

## Maven coordinates

```xml
<dependency>
    <groupId>com.firefly</groupId>
    <artifactId>flyquery-sdk</artifactId>
    <version>26.5.2</version>
</dependency>
```

## Requirements

- Java 25+
- Spring Boot 3.5.9+ (or import the BOM manually)

If you are not using Spring Boot as your parent, add the Spring BOM explicitly:

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
import com.firefly.flyquery.model.WorkspaceCreate;

public class Demo {
    public static void main(String[] args) {
        ApiClient client = new ApiClient();
        client.setBasePath("http://localhost:8520");

        WorkspacesApi workspaces = new WorkspacesApi(client);
        WorkspaceCreate create = new WorkspaceCreate()
            .name("analytics")
            .description("My analytics workspace");

        // Reactive — subscribe to the Mono
        workspaces.createWorkspace("acme", create)
            .doOnNext(ws -> System.out.println("Created: " + ws.getId()))
            .block();
    }
}
```

## Query a workspace

```java
import com.firefly.flyquery.api.QueryApi;
import com.firefly.flyquery.model.QueryRequest;

QueryApi query = new QueryApi(client);
QueryRequest req = new QueryRequest()
    .question("Total revenue by region for Q1")
    .datasetId("ds_01");

query.queryAnswer("acme", "ws_01", req)
    .doOnNext(answer -> {
        System.out.println(answer.getAnswer());
        System.out.println(answer.getExecutedSql());
    })
    .block();
```

## Authentication (agent tokens)

```java
client.addDefaultHeader("X-Agent-Token", "fq_tok_...");
client.addDefaultHeader("Idempotency-Key", "my-unique-request-id");
```

## License

Apache-2.0. See [LICENSE](LICENSE).
