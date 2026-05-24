# QueriesApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**getQuery**](QueriesApi.md#getQuery) | **GET** /api/v1/queries/{query_id} | Fetch a single query with every candidate, retry, and model id. |
| [**getQueryResult**](QueriesApi.md#getQueryResult) | **GET** /api/v1/queries/{query_id}/result | Re-download a previously-executed query&#39;s preview + parquet. |
| [**listQueries**](QueriesApi.md#listQueries) | **GET** /api/v1/queries | List queries for the caller&#39;s workspace, newest first. |



## getQuery

> QueryDetailRead getQuery(queryId, xTenantId, xWorkspaceId, xCorrelationId)

Fetch a single query with every candidate, retry, and model id.

Returns 404 if the query doesn&#39;t belong to the caller&#39;s &#x60;&#x60;(tenant, workspace)&#x60;&#x60; -- not just \&quot;not found\&quot;, but also \&quot;exists but wrong tenant\&quot; (cross-tenant probing is the same 404 as missing).

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.auth.*;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.QueriesApi;

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

        QueriesApi apiInstance = new QueriesApi(defaultClient);
        String queryId = "queryId_example"; // String | 
        String xTenantId = "acme-corp"; // String | Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
        String xWorkspaceId = "00000000-0000-0000-0000-000000000001"; // String | Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
        UUID xCorrelationId = UUID.fromString("550e8400-e29b-41d4-a716-446655440000"); // UUID | Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
        try {
            QueryDetailRead result = apiInstance.getQuery(queryId, xTenantId, xWorkspaceId, xCorrelationId);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling QueriesApi#getQuery");
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
| **queryId** | **String**|  | |
| **xTenantId** | **String**| Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present. | |
| **xWorkspaceId** | **String**| Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation. | |
| **xCorrelationId** | **UUID**| Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. | [optional] |

### Return type

[**QueryDetailRead**](QueryDetailRead.md)

### Authorization

[WorkspaceContext](../README.md#WorkspaceContext), [TenantContext](../README.md#TenantContext)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful response |  -  |


## getQueryResult

> QueryResultRead getQueryResult(queryId, xTenantId, xWorkspaceId, xCorrelationId)

Re-download a previously-executed query&#39;s preview + parquet.

The preview is always inlined. The presigned Parquet URL is &#x60;&#x60;None&#x60;&#x60; when the TTL has elapsed (default 24h) -- consumers must rerun the query in that case. The presign TTL itself is bounded by &#x60;&#x60;object_store_presign_ttl_s&#x60;&#x60; (default 24h).  Returns 404 if either the query OR its result row doesn&#39;t exist for this tenant.

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.auth.*;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.QueriesApi;

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

        QueriesApi apiInstance = new QueriesApi(defaultClient);
        String queryId = "queryId_example"; // String | 
        String xTenantId = "acme-corp"; // String | Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
        String xWorkspaceId = "00000000-0000-0000-0000-000000000001"; // String | Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
        UUID xCorrelationId = UUID.fromString("550e8400-e29b-41d4-a716-446655440000"); // UUID | Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
        try {
            QueryResultRead result = apiInstance.getQueryResult(queryId, xTenantId, xWorkspaceId, xCorrelationId);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling QueriesApi#getQueryResult");
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
| **queryId** | **String**|  | |
| **xTenantId** | **String**| Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present. | |
| **xWorkspaceId** | **String**| Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation. | |
| **xCorrelationId** | **UUID**| Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. | [optional] |

### Return type

[**QueryResultRead**](QueryResultRead.md)

### Authorization

[WorkspaceContext](../README.md#WorkspaceContext), [TenantContext](../README.md#TenantContext)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful response |  -  |


## listQueries

> PaginatedQueryHistoryItem listQueries(xTenantId, xWorkspaceId, datasetId, executionStatus, semanticPathTaken, dateFrom, dateTo, limit, offset, xCorrelationId)

List queries for the caller&#39;s workspace, newest first.

Filters ------- * &#x60;&#x60;dataset_id&#x60;&#x60;           -- restrict to one dataset * &#x60;&#x60;execution_status&#x60;&#x60;     -- &#x60;&#x60;OK&#x60;&#x60; / &#x60;&#x60;REJECTED_BY_FIREWALL&#x60;&#x60; / &#x60;&#x60;FAILED&#x60;&#x60; / ... * &#x60;&#x60;semantic_path_taken&#x60;&#x60;  -- e.g. &#x60;&#x60;\&quot;sql\&quot;&#x60;&#x60; vs &#x60;&#x60;\&quot;semantic-layer\&quot;&#x60;&#x60; * &#x60;&#x60;date_from&#x60;&#x60;            -- inclusive lower bound on &#x60;&#x60;created_at&#x60;&#x60; * &#x60;&#x60;date_to&#x60;&#x60;              -- exclusive upper bound on &#x60;&#x60;created_at&#x60;&#x60;  Page size is clamped to &#x60;&#x60;[1, 200]&#x60;&#x60;. Each item is the compact history shape (no heavy JSONB columns). Use &#x60;&#x60;GET /queries/{id}&#x60;&#x60; for the full row.

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.auth.*;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.QueriesApi;

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

        QueriesApi apiInstance = new QueriesApi(defaultClient);
        String xTenantId = "acme-corp"; // String | Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
        String xWorkspaceId = "00000000-0000-0000-0000-000000000001"; // String | Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
        String datasetId = "datasetId_example"; // String | 
        String executionStatus = "executionStatus_example"; // String | 
        String semanticPathTaken = "semanticPathTaken_example"; // String | 
        String dateFrom = "dateFrom_example"; // String | 
        String dateTo = "dateTo_example"; // String | 
        Integer limit = 50; // Integer | 
        Integer offset = 0; // Integer | 
        UUID xCorrelationId = UUID.fromString("550e8400-e29b-41d4-a716-446655440000"); // UUID | Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
        try {
            PaginatedQueryHistoryItem result = apiInstance.listQueries(xTenantId, xWorkspaceId, datasetId, executionStatus, semanticPathTaken, dateFrom, dateTo, limit, offset, xCorrelationId);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling QueriesApi#listQueries");
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
| **datasetId** | **String**|  | [optional] |
| **executionStatus** | **String**|  | [optional] |
| **semanticPathTaken** | **String**|  | [optional] |
| **dateFrom** | **String**|  | [optional] |
| **dateTo** | **String**|  | [optional] |
| **limit** | **Integer**|  | [optional] [default to 50] |
| **offset** | **Integer**|  | [optional] [default to 0] |
| **xCorrelationId** | **UUID**| Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. | [optional] |

### Return type

[**PaginatedQueryHistoryItem**](PaginatedQueryHistoryItem.md)

### Authorization

[WorkspaceContext](../README.md#WorkspaceContext), [TenantContext](../README.md#TenantContext)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful response |  -  |

