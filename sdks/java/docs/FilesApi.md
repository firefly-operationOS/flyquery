# FilesApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**reuploadFile**](FilesApi.md#reuploadFile) | **PUT** /api/v1/datasets/{dataset_id}/tables/{table_id}:upload | Re-upload into an existing table slot; creates a new snapshot. |
| [**uploadFile**](FilesApi.md#uploadFile) | **POST** /api/v1/datasets/{dataset_id}/files | Accept a multipart file upload and run the synchronous ingestion pipeline. |
| [**uploadFileAsync**](FilesApi.md#uploadFileAsync) | **POST** /api/v1/datasets/{dataset_id}/files:async | Async alternative to &#x60;&#x60;POST /datasets/{ds}/files&#x60;&#x60;. |
| [**uploadFilesBulk**](FilesApi.md#uploadFilesBulk) | **POST** /api/v1/datasets/{dataset_id}/files:bulk | Accept multiple files in one multipart request and ingest each. |



## reuploadFile

> ReuploadResponse reuploadFile(datasetId, tableId, xTenantId, xWorkspaceId, xCorrelationId, idempotencyKey)

Re-upload into an existing table slot; creates a new snapshot.

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.auth.*;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.FilesApi;

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

        FilesApi apiInstance = new FilesApi(defaultClient);
        String datasetId = "datasetId_example"; // String | 
        String tableId = "tableId_example"; // String | 
        String xTenantId = "acme-corp"; // String | Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
        String xWorkspaceId = "00000000-0000-0000-0000-000000000001"; // String | Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
        UUID xCorrelationId = UUID.fromString("550e8400-e29b-41d4-a716-446655440000"); // UUID | Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
        String idempotencyKey = "ingest-2026-05-23-abc123"; // String | Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
        try {
            ReuploadResponse result = apiInstance.reuploadFile(datasetId, tableId, xTenantId, xWorkspaceId, xCorrelationId, idempotencyKey);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling FilesApi#reuploadFile");
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
| **datasetId** | **String**|  | |
| **tableId** | **String**|  | |
| **xTenantId** | **String**| Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present. | |
| **xWorkspaceId** | **String**| Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation. | |
| **xCorrelationId** | **UUID**| Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. | [optional] |
| **idempotencyKey** | **String**| Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h. | [optional] |

### Return type

[**ReuploadResponse**](ReuploadResponse.md)

### Authorization

[WorkspaceContext](../README.md#WorkspaceContext), [TenantContext](../README.md#TenantContext)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful response |  -  |


## uploadFile

> FileUploadResponse uploadFile(datasetId, xTenantId, xWorkspaceId, xCorrelationId, idempotencyKey)

Accept a multipart file upload and run the synchronous ingestion pipeline.

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.auth.*;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.FilesApi;

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

        FilesApi apiInstance = new FilesApi(defaultClient);
        String datasetId = "datasetId_example"; // String | 
        String xTenantId = "acme-corp"; // String | Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
        String xWorkspaceId = "00000000-0000-0000-0000-000000000001"; // String | Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
        UUID xCorrelationId = UUID.fromString("550e8400-e29b-41d4-a716-446655440000"); // UUID | Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
        String idempotencyKey = "ingest-2026-05-23-abc123"; // String | Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
        try {
            FileUploadResponse result = apiInstance.uploadFile(datasetId, xTenantId, xWorkspaceId, xCorrelationId, idempotencyKey);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling FilesApi#uploadFile");
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
| **datasetId** | **String**|  | |
| **xTenantId** | **String**| Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present. | |
| **xWorkspaceId** | **String**| Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation. | |
| **xCorrelationId** | **UUID**| Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. | [optional] |
| **idempotencyKey** | **String**| Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h. | [optional] |

### Return type

[**FileUploadResponse**](FileUploadResponse.md)

### Authorization

[WorkspaceContext](../README.md#WorkspaceContext), [TenantContext](../README.md#TenantContext)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful response |  -  |


## uploadFileAsync

> uploadFileAsync(datasetId, xTenantId, xWorkspaceId, xCorrelationId, idempotencyKey)

Async alternative to &#x60;&#x60;POST /datasets/{ds}/files&#x60;&#x60;.

Stage 1 (receive: caps check, hash, format detect, store bytes, write &#x60;&#x60;flyquery_files&#x60;&#x60; row, track workspace storage) runs *synchronously* -- it&#39;s bounded by IO + a single Postgres insert, not by parse/profile/describe cost. Stages 2-10 are queued as a &#x60;&#x60;PARSE_AND_INGEST&#x60;&#x60; ingest job that the worker consumes; the response 202 carries the &#x60;&#x60;job_id&#x60;&#x60; plus a &#x60;&#x60;Location&#x60;&#x60; header so clients can poll &#x60;&#x60;GET /ingest-jobs/{job_id}&#x60;&#x60; or stream &#x60;&#x60;GET /ingest-jobs/{job_id}/stream&#x60;&#x60;.  Use this in place of the synchronous endpoint when a single file exceeds the request-timeout budget of the deployment (typically anything above a few MB with cold-cache LLM describe calls).  Stage 1&#39;s SHA-256 content hash provides natural dedup at the file level -- re-uploading the same bytes is detected at &#x60;&#x60;flyquery_files&#x60;&#x60; UNIQUE-on-(tenant, dataset, content_hash) -- so we do NOT layer Idempotency-Key replay caching here; the underlying &#x60;&#x60;IngestJobService&#x60;&#x60; is also idempotent by construction.

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.auth.*;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.FilesApi;

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

        FilesApi apiInstance = new FilesApi(defaultClient);
        String datasetId = "datasetId_example"; // String | 
        String xTenantId = "acme-corp"; // String | Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
        String xWorkspaceId = "00000000-0000-0000-0000-000000000001"; // String | Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
        UUID xCorrelationId = UUID.fromString("550e8400-e29b-41d4-a716-446655440000"); // UUID | Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
        String idempotencyKey = "ingest-2026-05-23-abc123"; // String | Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
        try {
            apiInstance.uploadFileAsync(datasetId, xTenantId, xWorkspaceId, xCorrelationId, idempotencyKey);
        } catch (ApiException e) {
            System.err.println("Exception when calling FilesApi#uploadFileAsync");
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
| **datasetId** | **String**|  | |
| **xTenantId** | **String**| Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present. | |
| **xWorkspaceId** | **String**| Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation. | |
| **xCorrelationId** | **UUID**| Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. | [optional] |
| **idempotencyKey** | **String**| Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h. | [optional] |

### Return type

null (empty response body)

### Authorization

[WorkspaceContext](../README.md#WorkspaceContext), [TenantContext](../README.md#TenantContext)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: Not defined


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **202** | Successful response |  -  |


## uploadFilesBulk

> BulkFileUploadResponse uploadFilesBulk(datasetId, xTenantId, xWorkspaceId, xCorrelationId, idempotencyKey)

Accept multiple files in one multipart request and ingest each.

Each &#x60;&#x60;files&#x60;&#x60; part is processed through the same per-file pipeline as &#x60;&#x60;POST /files&#x60;&#x60; (receive -&gt; parse -&gt; reconcile -&gt; sample -&gt; profile -&gt; describe -&gt; embed -&gt; publish), and the per-file results run **in parallel** through &#x60;&#x60;asyncio.gather&#x60;&#x60; -- a 5-file upload finishes in roughly the time of a single file.  Per-file failures do NOT abort the bulk. The response carries one &#x60;&#x60;BulkFileResult&#x60;&#x60; per submitted file with either &#x60;&#x60;status&#x3D;\&quot;OK\&quot;&#x60;&#x60; + &#x60;&#x60;file_id&#x60;&#x60; + &#x60;&#x60;tables&#x60;&#x60; or &#x60;&#x60;status&#x3D;\&quot;FAILED\&quot;&#x60;&#x60; + &#x60;&#x60;error&#x60;&#x60;. Aggregate &#x60;&#x60;succeeded&#x60;&#x60; / &#x60;&#x60;failed&#x60;&#x60; counts let a UI render progress without scanning the list.  Replay-dedup&#39;d via &#x60;&#x60;Idempotency-Key&#x60;&#x60; when present (optional on user tier). A retried bulk upload with the same key returns the cached envelope without re-ingesting -- important because the pipeline is heavy (parse + profile + describe + embed per file) and a duplicate run would double-write Parquet snapshots.

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.auth.*;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.FilesApi;

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

        FilesApi apiInstance = new FilesApi(defaultClient);
        String datasetId = "datasetId_example"; // String | 
        String xTenantId = "acme-corp"; // String | Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
        String xWorkspaceId = "00000000-0000-0000-0000-000000000001"; // String | Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
        UUID xCorrelationId = UUID.fromString("550e8400-e29b-41d4-a716-446655440000"); // UUID | Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
        String idempotencyKey = "ingest-2026-05-23-abc123"; // String | Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
        try {
            BulkFileUploadResponse result = apiInstance.uploadFilesBulk(datasetId, xTenantId, xWorkspaceId, xCorrelationId, idempotencyKey);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling FilesApi#uploadFilesBulk");
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
| **datasetId** | **String**|  | |
| **xTenantId** | **String**| Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present. | |
| **xWorkspaceId** | **String**| Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation. | |
| **xCorrelationId** | **UUID**| Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. | [optional] |
| **idempotencyKey** | **String**| Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h. | [optional] |

### Return type

[**BulkFileUploadResponse**](BulkFileUploadResponse.md)

### Authorization

[WorkspaceContext](../README.md#WorkspaceContext), [TenantContext](../README.md#TenantContext)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful response |  -  |

