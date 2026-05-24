# CostEventsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**listEvents**](CostEventsApi.md#listEvents) | **GET** /api/v1/cost-events | List cost events for the caller&#39;s workspace, newest first. |



## listEvents

> PaginatedCostEventRead listEvents(xTenantId, xWorkspaceId, actor, model, operation, dateFrom, dateTo, limit, offset, xCorrelationId)

List cost events for the caller&#39;s workspace, newest first.

Filters ------- * &#x60;&#x60;actor&#x60;&#x60;     -- exact match * &#x60;&#x60;model&#x60;&#x60;     -- exact match (&#x60;&#x60;anthropic:claude-sonnet-4-6&#x60;&#x60; etc.) * &#x60;&#x60;operation&#x60;&#x60; -- exact match (&#x60;&#x60;grounding&#x60;&#x60; / &#x60;&#x60;generation&#x60;&#x60; / ...) * &#x60;&#x60;date_from&#x60;&#x60; -- inclusive lower bound on &#x60;&#x60;created_at&#x60;&#x60; * &#x60;&#x60;date_to&#x60;&#x60;   -- exclusive upper bound on &#x60;&#x60;created_at&#x60;&#x60;

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.auth.*;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.CostEventsApi;

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

        CostEventsApi apiInstance = new CostEventsApi(defaultClient);
        String xTenantId = "acme-corp"; // String | Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
        String xWorkspaceId = "00000000-0000-0000-0000-000000000001"; // String | Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
        String actor = "actor_example"; // String | 
        String model = "model_example"; // String | 
        String operation = "operation_example"; // String | 
        String dateFrom = "dateFrom_example"; // String | 
        String dateTo = "dateTo_example"; // String | 
        Integer limit = 100; // Integer | 
        Integer offset = 0; // Integer | 
        UUID xCorrelationId = UUID.fromString("550e8400-e29b-41d4-a716-446655440000"); // UUID | Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
        try {
            PaginatedCostEventRead result = apiInstance.listEvents(xTenantId, xWorkspaceId, actor, model, operation, dateFrom, dateTo, limit, offset, xCorrelationId);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling CostEventsApi#listEvents");
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
| **actor** | **String**|  | [optional] |
| **model** | **String**|  | [optional] |
| **operation** | **String**|  | [optional] |
| **dateFrom** | **String**|  | [optional] |
| **dateTo** | **String**|  | [optional] |
| **limit** | **Integer**|  | [optional] [default to 100] |
| **offset** | **Integer**|  | [optional] [default to 0] |
| **xCorrelationId** | **UUID**| Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. | [optional] |

### Return type

[**PaginatedCostEventRead**](PaginatedCostEventRead.md)

### Authorization

[WorkspaceContext](../README.md#WorkspaceContext), [TenantContext](../README.md#TenantContext)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful response |  -  |

