# AgentIngestJobsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**cancelJob**](AgentIngestJobsApi.md#cancelJob) | **POST** /api/v1/agent/ingest-jobs/{job_id}:cancel | Cooperatively cancel a running job. |
| [**createJob**](AgentIngestJobsApi.md#createJob) | **POST** /api/v1/agent/ingest-jobs | Start a background ingestion job (REPARSE/SAMPLE_REFRESH/...). |
| [**getJob**](AgentIngestJobsApi.md#getJob) | **GET** /api/v1/agent/ingest-jobs/{job_id} |  |
| [**listEvents**](AgentIngestJobsApi.md#listEvents) | **GET** /api/v1/agent/ingest-jobs/{job_id}/events |  |
| [**listJobs**](AgentIngestJobsApi.md#listJobs) | **GET** /api/v1/agent/ingest-jobs |  |
| [**streamJob**](AgentIngestJobsApi.md#streamJob) | **GET** /api/v1/agent/ingest-jobs/{job_id}/stream | SSE progress stream. The underlying delegate handles framing, |



## cancelJob

> CancelResponse cancelJob(jobId, xAgentToken, xCorrelationId, idempotencyKey)

Cooperatively cancel a running job.

Replay-dedup&#39;d via &#x60;&#x60;Idempotency-Key&#x60;&#x60; (required). The underlying service is itself idempotent on terminal jobs, but we still cache the response so a retried cancel returns the same wire envelope (same &#x60;&#x60;status&#x60;&#x60; field).

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.auth.*;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.AgentIngestJobsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");
        
        // Configure API key authorization: AgentToken
        ApiKeyAuth AgentToken = (ApiKeyAuth) defaultClient.getAuthentication("AgentToken");
        AgentToken.setApiKey("YOUR API KEY");
        // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
        //AgentToken.setApiKeyPrefix("Token");

        AgentIngestJobsApi apiInstance = new AgentIngestJobsApi(defaultClient);
        String jobId = "jobId_example"; // String | 
        String xAgentToken = "fqt_live_aBcDeF1234567890aBcDeF1234567890"; // String | Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token's claims encode the tenant + workspace + scopes. Issue via ``POST /api/v1/agent-tokens``.
        UUID xCorrelationId = UUID.fromString("550e8400-e29b-41d4-a716-446655440000"); // UUID | Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
        String idempotencyKey = "ingest-2026-05-23-abc123"; // String | Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
        try {
            CancelResponse result = apiInstance.cancelJob(jobId, xAgentToken, xCorrelationId, idempotencyKey);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentIngestJobsApi#cancelJob");
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
| **jobId** | **String**|  | |
| **xAgentToken** | **String**| Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;. | |
| **xCorrelationId** | **UUID**| Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. | [optional] |
| **idempotencyKey** | **String**| Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h. | [optional] |

### Return type

[**CancelResponse**](CancelResponse.md)

### Authorization

[AgentToken](../README.md#AgentToken)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful response |  -  |


## createJob

> createJob(xAgentToken, xCorrelationId, idempotencyKey)

Start a background ingestion job (REPARSE/SAMPLE_REFRESH/...).

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.auth.*;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.AgentIngestJobsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");
        
        // Configure API key authorization: AgentToken
        ApiKeyAuth AgentToken = (ApiKeyAuth) defaultClient.getAuthentication("AgentToken");
        AgentToken.setApiKey("YOUR API KEY");
        // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
        //AgentToken.setApiKeyPrefix("Token");

        AgentIngestJobsApi apiInstance = new AgentIngestJobsApi(defaultClient);
        String xAgentToken = "fqt_live_aBcDeF1234567890aBcDeF1234567890"; // String | Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token's claims encode the tenant + workspace + scopes. Issue via ``POST /api/v1/agent-tokens``.
        UUID xCorrelationId = UUID.fromString("550e8400-e29b-41d4-a716-446655440000"); // UUID | Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
        String idempotencyKey = "ingest-2026-05-23-abc123"; // String | Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
        try {
            apiInstance.createJob(xAgentToken, xCorrelationId, idempotencyKey);
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentIngestJobsApi#createJob");
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
| **xAgentToken** | **String**| Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;. | |
| **xCorrelationId** | **UUID**| Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. | [optional] |
| **idempotencyKey** | **String**| Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h. | [optional] |

### Return type

null (empty response body)

### Authorization

[AgentToken](../README.md#AgentToken)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: Not defined


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful response |  -  |


## getJob

> IngestJobRead getJob(jobId, xAgentToken, xCorrelationId)



### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.auth.*;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.AgentIngestJobsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");
        
        // Configure API key authorization: AgentToken
        ApiKeyAuth AgentToken = (ApiKeyAuth) defaultClient.getAuthentication("AgentToken");
        AgentToken.setApiKey("YOUR API KEY");
        // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
        //AgentToken.setApiKeyPrefix("Token");

        AgentIngestJobsApi apiInstance = new AgentIngestJobsApi(defaultClient);
        String jobId = "jobId_example"; // String | 
        String xAgentToken = "fqt_live_aBcDeF1234567890aBcDeF1234567890"; // String | Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token's claims encode the tenant + workspace + scopes. Issue via ``POST /api/v1/agent-tokens``.
        UUID xCorrelationId = UUID.fromString("550e8400-e29b-41d4-a716-446655440000"); // UUID | Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
        try {
            IngestJobRead result = apiInstance.getJob(jobId, xAgentToken, xCorrelationId);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentIngestJobsApi#getJob");
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
| **jobId** | **String**|  | |
| **xAgentToken** | **String**| Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;. | |
| **xCorrelationId** | **UUID**| Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. | [optional] |

### Return type

[**IngestJobRead**](IngestJobRead.md)

### Authorization

[AgentToken](../README.md#AgentToken)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful response |  -  |


## listEvents

> IngestEventListResponse listEvents(jobId, xAgentToken, xCorrelationId)



### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.auth.*;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.AgentIngestJobsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");
        
        // Configure API key authorization: AgentToken
        ApiKeyAuth AgentToken = (ApiKeyAuth) defaultClient.getAuthentication("AgentToken");
        AgentToken.setApiKey("YOUR API KEY");
        // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
        //AgentToken.setApiKeyPrefix("Token");

        AgentIngestJobsApi apiInstance = new AgentIngestJobsApi(defaultClient);
        String jobId = "jobId_example"; // String | 
        String xAgentToken = "fqt_live_aBcDeF1234567890aBcDeF1234567890"; // String | Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token's claims encode the tenant + workspace + scopes. Issue via ``POST /api/v1/agent-tokens``.
        UUID xCorrelationId = UUID.fromString("550e8400-e29b-41d4-a716-446655440000"); // UUID | Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
        try {
            IngestEventListResponse result = apiInstance.listEvents(jobId, xAgentToken, xCorrelationId);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentIngestJobsApi#listEvents");
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
| **jobId** | **String**|  | |
| **xAgentToken** | **String**| Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;. | |
| **xCorrelationId** | **UUID**| Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. | [optional] |

### Return type

[**IngestEventListResponse**](IngestEventListResponse.md)

### Authorization

[AgentToken](../README.md#AgentToken)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful response |  -  |


## listJobs

> IngestJobListResponse listJobs(xAgentToken, xCorrelationId)



### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.auth.*;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.AgentIngestJobsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");
        
        // Configure API key authorization: AgentToken
        ApiKeyAuth AgentToken = (ApiKeyAuth) defaultClient.getAuthentication("AgentToken");
        AgentToken.setApiKey("YOUR API KEY");
        // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
        //AgentToken.setApiKeyPrefix("Token");

        AgentIngestJobsApi apiInstance = new AgentIngestJobsApi(defaultClient);
        String xAgentToken = "fqt_live_aBcDeF1234567890aBcDeF1234567890"; // String | Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token's claims encode the tenant + workspace + scopes. Issue via ``POST /api/v1/agent-tokens``.
        UUID xCorrelationId = UUID.fromString("550e8400-e29b-41d4-a716-446655440000"); // UUID | Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
        try {
            IngestJobListResponse result = apiInstance.listJobs(xAgentToken, xCorrelationId);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentIngestJobsApi#listJobs");
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
| **xAgentToken** | **String**| Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;. | |
| **xCorrelationId** | **UUID**| Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. | [optional] |

### Return type

[**IngestJobListResponse**](IngestJobListResponse.md)

### Authorization

[AgentToken](../README.md#AgentToken)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful response |  -  |


## streamJob

> streamJob(jobId, xAgentToken, xCorrelationId)

SSE progress stream. The underlying delegate handles framing,

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.auth.*;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.AgentIngestJobsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");
        
        // Configure API key authorization: AgentToken
        ApiKeyAuth AgentToken = (ApiKeyAuth) defaultClient.getAuthentication("AgentToken");
        AgentToken.setApiKey("YOUR API KEY");
        // Uncomment the following line to set a prefix for the API key, e.g. "Token" (defaults to null)
        //AgentToken.setApiKeyPrefix("Token");

        AgentIngestJobsApi apiInstance = new AgentIngestJobsApi(defaultClient);
        String jobId = "jobId_example"; // String | 
        String xAgentToken = "fqt_live_aBcDeF1234567890aBcDeF1234567890"; // String | Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token's claims encode the tenant + workspace + scopes. Issue via ``POST /api/v1/agent-tokens``.
        UUID xCorrelationId = UUID.fromString("550e8400-e29b-41d4-a716-446655440000"); // UUID | Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
        try {
            apiInstance.streamJob(jobId, xAgentToken, xCorrelationId);
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentIngestJobsApi#streamJob");
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
| **jobId** | **String**|  | |
| **xAgentToken** | **String**| Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;. | |
| **xCorrelationId** | **UUID**| Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. | [optional] |

### Return type

null (empty response body)

### Authorization

[AgentToken](../README.md#AgentToken)

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: Not defined


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful response |  -  |

