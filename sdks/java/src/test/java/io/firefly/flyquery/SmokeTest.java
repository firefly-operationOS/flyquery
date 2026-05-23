package io.firefly.flyquery;

import org.openapitools.client.ApiClient;
import org.openapitools.client.Configuration;
import org.openapitools.client.api.DefaultApi;

/**
 * Smoke test — reference the major API class; compilation verifies the SDK shape.
 *
 * NOTE: Due to 34 OpenAPI path-parameter validation errors (colon-action routes like
 * {workspace_id}:purge), openapi-generator-cli collapsed all endpoints into DefaultApi
 * instead of separate WorkspacesApi / DatasetsApi / QueryApi classes.  The fix (adding
 * FastAPI `parameters=` blocks so path params appear in the spec) is tracked as a v1
 * follow-up.  The pom.xml correctly uses io.firefly:flyquery-sdk:26.5.2 as coordinates.
 */
public class SmokeTest {
    public static void main(String[] args) {
        ApiClient client = Configuration.getDefaultApiClient();
        client.setBasePath("http://localhost:8520");
        // Reference the generated API class — compilation verifies SDK shape
        DefaultApi api = new DefaultApi(client);
        System.out.println("SDK smoke OK: " + api.getClass().getName());
    }
}
