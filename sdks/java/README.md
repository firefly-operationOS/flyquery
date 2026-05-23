# flyquery Java SDK

Auto-generated from `flyquery/openapi.json` via `openapi-generator-cli`.

## Install (Maven)

```xml
<dependency>
    <groupId>io.firefly</groupId>
    <artifactId>flyquery-sdk</artifactId>
    <version>26.5.2</version>
</dependency>
```

## Quick start

```java
import io.firefly.flyquery.ApiClient;
import io.firefly.flyquery.Configuration;
import io.firefly.flyquery.api.WorkspacesApi;

public class Demo {
    public static void main(String[] args) throws Exception {
        ApiClient client = Configuration.getDefaultApiClient();
        client.setBasePath("http://localhost:8520");
        WorkspacesApi api = new WorkspacesApi(client);
        // ... call api.createWorkspace(...)
    }
}
```

## License

Apache-2.0.
