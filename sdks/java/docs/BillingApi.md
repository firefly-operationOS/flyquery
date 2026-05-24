# BillingApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**rollup**](BillingApi.md#rollup) | **GET** /api/v1/billing | Aggregate LLM cost into &#x60;&#x60;day&#x60;&#x60; / &#x60;&#x60;week&#x60;&#x60; / &#x60;&#x60;month&#x60;&#x60; buckets. |



## rollup

> BillingRollup rollup(xTenantId, xWorkspaceId, period, dateFrom, dateTo, xCorrelationId)

Aggregate LLM cost into &#x60;&#x60;day&#x60;&#x60; / &#x60;&#x60;week&#x60;&#x60; / &#x60;&#x60;month&#x60;&#x60; buckets.

Query params ------------ * &#x60;&#x60;period&#x60;&#x60;    -- &#x60;&#x60;day&#x60;&#x60; (default) / &#x60;&#x60;week&#x60;&#x60; / &#x60;&#x60;month&#x60;&#x60; * &#x60;&#x60;date_from&#x60;&#x60; -- inclusive lower bound on &#x60;&#x60;created_at&#x60;&#x60; * &#x60;&#x60;date_to&#x60;&#x60;   -- exclusive upper bound on &#x60;&#x60;created_at&#x60;&#x60;  Response shape: :class:&#x60;BillingRollup&#x60;. Buckets with zero cost are omitted from the breakdown (no empty days).

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.auth.*;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.BillingApi;

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

        BillingApi apiInstance = new BillingApi(defaultClient);
        String xTenantId = "acme-corp"; // String | Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
        String xWorkspaceId = "00000000-0000-0000-0000-000000000001"; // String | Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
        String period = "day"; // String | 
        String dateFrom = "dateFrom_example"; // String | 
        String dateTo = "dateTo_example"; // String | 
        UUID xCorrelationId = UUID.fromString("550e8400-e29b-41d4-a716-446655440000"); // UUID | Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
        try {
            BillingRollup result = apiInstance.rollup(xTenantId, xWorkspaceId, period, dateFrom, dateTo, xCorrelationId);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling BillingApi#rollup");
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
| **period** | **String**|  | [optional] [default to day] |
| **dateFrom** | **String**|  | [optional] |
| **dateTo** | **String**|  | [optional] |
| **xCorrelationId** | **UUID**| Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. | [optional] |

### Return type

[**BillingRollup**](BillingRollup.md)

### Authorization

[WorkspaceContext](../README.md#WorkspaceContext), [TenantContext](../README.md#TenantContext)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful response |  -  |

