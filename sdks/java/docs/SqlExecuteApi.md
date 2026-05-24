# SqlExecuteApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**execute**](SqlExecuteApi.md#execute) | **POST** /api/v1/sql:execute | Execute a SQL statement directly against the workspace&#39;s dataset Parquet. |
| [**executeStream**](SqlExecuteApi.md#executeStream) | **POST** /api/v1/sql:execute/stream | Execute SQL and stream progress as Server-Sent Events. |



## execute

> SqlExecuteResponse execute(xTenantId, xWorkspaceId, sqlExecuteRequest, xCorrelationId, idempotencyKey)

Execute a SQL statement directly against the workspace&#39;s dataset Parquet.

Requires the workspace flag &#x60;&#x60;allow_direct_sql&#x3D;true&#x60;&#x60;. The SQL is AST-classified and scope-checked; the agent pipeline is skipped.  :param http_request: Starlette request :param body: validated SqlExecuteRequest :return: SqlExecuteResponse with preview rows and execution metadata :raises DirectSqlForbidden: when workspace.allow_direct_sql is False

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.auth.*;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.SqlExecuteApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");
        
        // Configure API key authorization: WorkspaceContext
        ApiKeyAuth WorkspaceContext = (ApiKeyAuth) defaultClient.getAuthentication("WorkspaceContext");
        WorkspaceContext.setApiKey("YOUR API KEY");
        // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
        //WorkspaceContext.setApiKeyPrefix("Token");

        // Configure API key authorization: TenantContext
        ApiKeyAuth TenantContext = (ApiKeyAuth) defaultClient.getAuthentication("TenantContext");
        TenantContext.setApiKey("YOUR API KEY");
        // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
        //TenantContext.setApiKeyPrefix("Token");

        SqlExecuteApi apiInstance = new SqlExecuteApi(defaultClient);
        String xTenantId = "acme-corp"; // String | Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
        String xWorkspaceId = "00000000-0000-0000-0000-000000000001"; // String | Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
        SqlExecuteRequest sqlExecuteRequest = new SqlExecuteRequest(); // SqlExecuteRequest | 
        UUID xCorrelationId = UUID.fromString("550e8400-e29b-41d4-a716-446655440000"); // UUID | Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
        String idempotencyKey = "ingest-2026-05-23-abc123"; // String | Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
        try {
            SqlExecuteResponse result = apiInstance.execute(xTenantId, xWorkspaceId, sqlExecuteRequest, xCorrelationId, idempotencyKey);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling SqlExecuteApi#execute");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **xTenantId** | **String**| Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present. | |
| **xWorkspaceId** | **String**| Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation. | |
| **sqlExecuteRequest** | [**SqlExecuteRequest**](SqlExecuteRequest.md)|  | |
| **xCorrelationId** | **UUID**| Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. | [optional] |
| **idempotencyKey** | **String**| Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h. | [optional] |

### Return type

[**SqlExecuteResponse**](SqlExecuteResponse.md)

### Authorization

[WorkspaceContext](../README.md#WorkspaceContext), [TenantContext](../README.md#TenantContext)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful response |  -  |
| **422** | Validation Error |  -  |


## executeStream

> String executeStream(xTenantId, xWorkspaceId, sqlExecuteRequest, xCorrelationId, idempotencyKey)

Execute SQL and stream progress as Server-Sent Events.

Event sequence: 1. &#x60;&#x60;ast_classified&#x60;&#x60; — AST result + scope check outcome 2. &#x60;&#x60;executed&#x60;&#x60;       — DuckDB result 3. &#x60;&#x60;final&#x60;&#x60;          — full SqlExecuteResponse JSON  :param http_request: Starlette request :param body: validated SqlExecuteRequest :return: StreamingResponse with &#x60;&#x60;text/event-stream&#x60;&#x60;

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.auth.*;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.SqlExecuteApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");
        
        // Configure API key authorization: WorkspaceContext
        ApiKeyAuth WorkspaceContext = (ApiKeyAuth) defaultClient.getAuthentication("WorkspaceContext");
        WorkspaceContext.setApiKey("YOUR API KEY");
        // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
        //WorkspaceContext.setApiKeyPrefix("Token");

        // Configure API key authorization: TenantContext
        ApiKeyAuth TenantContext = (ApiKeyAuth) defaultClient.getAuthentication("TenantContext");
        TenantContext.setApiKey("YOUR API KEY");
        // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
        //TenantContext.setApiKeyPrefix("Token");

        SqlExecuteApi apiInstance = new SqlExecuteApi(defaultClient);
        String xTenantId = "acme-corp"; // String | Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
        String xWorkspaceId = "00000000-0000-0000-0000-000000000001"; // String | Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
        SqlExecuteRequest sqlExecuteRequest = new SqlExecuteRequest(); // SqlExecuteRequest | 
        UUID xCorrelationId = UUID.fromString("550e8400-e29b-41d4-a716-446655440000"); // UUID | Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
        String idempotencyKey = "ingest-2026-05-23-abc123"; // String | Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
        try {
            String result = apiInstance.executeStream(xTenantId, xWorkspaceId, sqlExecuteRequest, xCorrelationId, idempotencyKey);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling SqlExecuteApi#executeStream");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **xTenantId** | **String**| Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present. | |
| **xWorkspaceId** | **String**| Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation. | |
| **sqlExecuteRequest** | [**SqlExecuteRequest**](SqlExecuteRequest.md)|  | |
| **xCorrelationId** | **UUID**| Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. | [optional] |
| **idempotencyKey** | **String**| Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h. | [optional] |

### Return type

**String**

### Authorization

[WorkspaceContext](../README.md#WorkspaceContext), [TenantContext](../README.md#TenantContext)

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: text/event-stream, application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Server-Sent Events stream. Each frame follows the SSE wire format &#x60;&#x60;event: &lt;name&gt;\\ndata: &lt;json&gt;\\n\\n&#x60;&#x60;. See &#x60;&#x60;docs/api-reference.md&#x60;&#x60; section 8 for the per-endpoint event catalogue. |  -  |
| **422** | Validation Error |  -  |

