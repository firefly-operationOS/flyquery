# IngestApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**cancelJob**](IngestApi.md#cancelJob) | **POST** /api/v1/ingest-jobs/{job_id}:cancel | Cooperatively cancel a job (idempotent for terminal jobs). |
| [**createJob**](IngestApi.md#createJob) | **POST** /api/v1/ingest-jobs | Start a background ingestion job (REPARSE/SAMPLE_REFRESH/DESCRIBE_PASS/RELATION_PASS). |
| [**getJob**](IngestApi.md#getJob) | **GET** /api/v1/ingest-jobs/{job_id} | Get a single ingest job. |
| [**listEvents**](IngestApi.md#listEvents) | **GET** /api/v1/ingest-jobs/{job_id}/events | Paginated event ledger for a job. |
| [**listJobs**](IngestApi.md#listJobs) | **GET** /api/v1/ingest-jobs | List ingest jobs with optional filters. |
| [**streamJob**](IngestApi.md#streamJob) | **GET** /api/v1/ingest-jobs/{job_id}/stream | SSE stream for real-time job progress. |


<a id="cancelJob"></a>
# **cancelJob**
> CancelResponse cancelJob(jobId)

Cooperatively cancel a job (idempotent for terminal jobs).

### Example
```java
// Import classes:
import io.firefly.flyquery.ApiClient;
import io.firefly.flyquery.ApiException;
import io.firefly.flyquery.Configuration;
import io.firefly.flyquery.models.*;
import io.firefly.flyquery.api.IngestApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");

    IngestApi apiInstance = new IngestApi(defaultClient);
    String jobId = "jobId_example"; // String | 
    try {
      CancelResponse result = apiInstance.cancelJob(jobId);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling IngestApi#cancelJob");
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

### Return type

[**CancelResponse**](CancelResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful response |  -  |

<a id="createJob"></a>
# **createJob**
> IngestJobRead createJob()

Start a background ingestion job (REPARSE/SAMPLE_REFRESH/DESCRIBE_PASS/RELATION_PASS).

### Example
```java
// Import classes:
import io.firefly.flyquery.ApiClient;
import io.firefly.flyquery.ApiException;
import io.firefly.flyquery.Configuration;
import io.firefly.flyquery.models.*;
import io.firefly.flyquery.api.IngestApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");

    IngestApi apiInstance = new IngestApi(defaultClient);
    try {
      IngestJobRead result = apiInstance.createJob();
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling IngestApi#createJob");
      System.err.println("Status code: " + e.getCode());
      System.err.println("Reason: " + e.getResponseBody());
      System.err.println("Response headers: " + e.getResponseHeaders());
      e.printStackTrace();
    }
  }
}
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**IngestJobRead**](IngestJobRead.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful response |  -  |

<a id="getJob"></a>
# **getJob**
> IngestJobRead getJob(jobId)

Get a single ingest job.

### Example
```java
// Import classes:
import io.firefly.flyquery.ApiClient;
import io.firefly.flyquery.ApiException;
import io.firefly.flyquery.Configuration;
import io.firefly.flyquery.models.*;
import io.firefly.flyquery.api.IngestApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");

    IngestApi apiInstance = new IngestApi(defaultClient);
    String jobId = "jobId_example"; // String | 
    try {
      IngestJobRead result = apiInstance.getJob(jobId);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling IngestApi#getJob");
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

### Return type

[**IngestJobRead**](IngestJobRead.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful response |  -  |

<a id="listEvents"></a>
# **listEvents**
> IngestEventListResponse listEvents(jobId)

Paginated event ledger for a job.

### Example
```java
// Import classes:
import io.firefly.flyquery.ApiClient;
import io.firefly.flyquery.ApiException;
import io.firefly.flyquery.Configuration;
import io.firefly.flyquery.models.*;
import io.firefly.flyquery.api.IngestApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");

    IngestApi apiInstance = new IngestApi(defaultClient);
    String jobId = "jobId_example"; // String | 
    try {
      IngestEventListResponse result = apiInstance.listEvents(jobId);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling IngestApi#listEvents");
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

### Return type

[**IngestEventListResponse**](IngestEventListResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful response |  -  |

<a id="listJobs"></a>
# **listJobs**
> IngestJobListResponse listJobs()

List ingest jobs with optional filters.

### Example
```java
// Import classes:
import io.firefly.flyquery.ApiClient;
import io.firefly.flyquery.ApiException;
import io.firefly.flyquery.Configuration;
import io.firefly.flyquery.models.*;
import io.firefly.flyquery.api.IngestApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");

    IngestApi apiInstance = new IngestApi(defaultClient);
    try {
      IngestJobListResponse result = apiInstance.listJobs();
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling IngestApi#listJobs");
      System.err.println("Status code: " + e.getCode());
      System.err.println("Reason: " + e.getResponseBody());
      System.err.println("Response headers: " + e.getResponseHeaders());
      e.printStackTrace();
    }
  }
}
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**IngestJobListResponse**](IngestJobListResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful response |  -  |

<a id="streamJob"></a>
# **streamJob**
> streamJob(jobId)

SSE stream for real-time job progress.

Mirrors canon&#39;s ingest_jobs_controller SSE pattern: 1. Emit all existing events for the job (catch-up replay) 2. Poll for new events every 250ms 3. Close stream when a &#x60;&#x60;final&#x60;&#x60; or &#x60;&#x60;error&#x60;&#x60; event is emitted 4. Hard timeout at _SSE_MAX_SECONDS to avoid connection leak

### Example
```java
// Import classes:
import io.firefly.flyquery.ApiClient;
import io.firefly.flyquery.ApiException;
import io.firefly.flyquery.Configuration;
import io.firefly.flyquery.models.*;
import io.firefly.flyquery.api.IngestApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");

    IngestApi apiInstance = new IngestApi(defaultClient);
    String jobId = "jobId_example"; // String | 
    try {
      apiInstance.streamJob(jobId);
    } catch (ApiException e) {
      System.err.println("Exception when calling IngestApi#streamJob");
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

### Return type

null (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful response |  -  |

