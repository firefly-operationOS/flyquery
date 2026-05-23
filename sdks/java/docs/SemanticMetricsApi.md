# SemanticMetricsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**create**](SemanticMetricsApi.md#create) | **POST** /api/v1/semantic/metrics | Create a new semantic metric in DRAFT status. |
| [**getMetric**](SemanticMetricsApi.md#getMetric) | **GET** /api/v1/semantic/metrics/{metric_id} | Fetch a single semantic metric by id. |
| [**history**](SemanticMetricsApi.md#history) | **GET** /api/v1/semantic/metrics/{metric_id}/history | Return version history for a metric, oldest first. |
| [**listMetrics**](SemanticMetricsApi.md#listMetrics) | **GET** /api/v1/semantic/metrics | List all semantic metrics for the caller&#39;s workspace. |
| [**publish**](SemanticMetricsApi.md#publish) | **POST** /api/v1/semantic/metrics/{metric_id}:publish | Validate, compile, and publish a metric (status → PUBLISHED). |
| [**retire**](SemanticMetricsApi.md#retire) | **POST** /api/v1/semantic/metrics/{metric_id}:retire | Retire a metric (status → RETIRED). |
| [**update**](SemanticMetricsApi.md#update) | **PUT** /api/v1/semantic/metrics/{metric_id} | Sparse-update a metric; re-validates YAML if definition changes. |



## create

> SemanticMetricRead create(semanticMetricCreate)

Create a new semantic metric in DRAFT status.

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.SemanticMetricsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        SemanticMetricsApi apiInstance = new SemanticMetricsApi(defaultClient);
        SemanticMetricCreate semanticMetricCreate = new SemanticMetricCreate(); // SemanticMetricCreate | 
        try {
            SemanticMetricRead result = apiInstance.create(semanticMetricCreate);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling SemanticMetricsApi#create");
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
| **semanticMetricCreate** | [**SemanticMetricCreate**](SemanticMetricCreate.md)|  | |

### Return type

[**SemanticMetricRead**](SemanticMetricRead.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful response |  -  |
| **422** | Validation Error |  -  |


## getMetric

> SemanticMetricRead getMetric(metricId)

Fetch a single semantic metric by id.

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.SemanticMetricsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        SemanticMetricsApi apiInstance = new SemanticMetricsApi(defaultClient);
        String metricId = "metricId_example"; // String | 
        try {
            SemanticMetricRead result = apiInstance.getMetric(metricId);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling SemanticMetricsApi#getMetric");
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
| **metricId** | **String**|  | |

### Return type

[**SemanticMetricRead**](SemanticMetricRead.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful response |  -  |


## history

> history(metricId)

Return version history for a metric, oldest first.

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.SemanticMetricsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        SemanticMetricsApi apiInstance = new SemanticMetricsApi(defaultClient);
        String metricId = "metricId_example"; // String | 
        try {
            apiInstance.history(metricId);
        } catch (ApiException e) {
            System.err.println("Exception when calling SemanticMetricsApi#history");
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
| **metricId** | **String**|  | |

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


## listMetrics

> listMetrics(datasetId)

List all semantic metrics for the caller&#39;s workspace.

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.SemanticMetricsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        SemanticMetricsApi apiInstance = new SemanticMetricsApi(defaultClient);
        String datasetId = "datasetId_example"; // String | 
        try {
            apiInstance.listMetrics(datasetId);
        } catch (ApiException e) {
            System.err.println("Exception when calling SemanticMetricsApi#listMetrics");
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
| **datasetId** | **String**|  | [optional] |

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


## publish

> SemanticMetricRead publish(metricId)

Validate, compile, and publish a metric (status → PUBLISHED).

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.SemanticMetricsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        SemanticMetricsApi apiInstance = new SemanticMetricsApi(defaultClient);
        String metricId = "metricId_example"; // String | 
        try {
            SemanticMetricRead result = apiInstance.publish(metricId);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling SemanticMetricsApi#publish");
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
| **metricId** | **String**|  | |

### Return type

[**SemanticMetricRead**](SemanticMetricRead.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful response |  -  |


## retire

> SemanticMetricRead retire(metricId)

Retire a metric (status → RETIRED).

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.SemanticMetricsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        SemanticMetricsApi apiInstance = new SemanticMetricsApi(defaultClient);
        String metricId = "metricId_example"; // String | 
        try {
            SemanticMetricRead result = apiInstance.retire(metricId);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling SemanticMetricsApi#retire");
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
| **metricId** | **String**|  | |

### Return type

[**SemanticMetricRead**](SemanticMetricRead.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful response |  -  |


## update

> SemanticMetricRead update(metricId, semanticMetricUpdate)

Sparse-update a metric; re-validates YAML if definition changes.

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.SemanticMetricsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        SemanticMetricsApi apiInstance = new SemanticMetricsApi(defaultClient);
        String metricId = "metricId_example"; // String | 
        SemanticMetricUpdate semanticMetricUpdate = new SemanticMetricUpdate(); // SemanticMetricUpdate | 
        try {
            SemanticMetricRead result = apiInstance.update(metricId, semanticMetricUpdate);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling SemanticMetricsApi#update");
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
| **metricId** | **String**|  | |
| **semanticMetricUpdate** | [**SemanticMetricUpdate**](SemanticMetricUpdate.md)|  | |

### Return type

[**SemanticMetricRead**](SemanticMetricRead.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful response |  -  |
| **422** | Validation Error |  -  |

