# SemanticApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**create**](SemanticApi.md#create) | **POST** /api/v1/semantic/dimensions | Create a new semantic dimension in DRAFT status. |
| [**create_0**](SemanticApi.md#create_0) | **POST** /api/v1/semantic/metrics | Create a new semantic metric in DRAFT status. |
| [**getDimension**](SemanticApi.md#getDimension) | **GET** /api/v1/semantic/dimensions/{dimension_id} | Fetch a single semantic dimension by id. |
| [**getMetric**](SemanticApi.md#getMetric) | **GET** /api/v1/semantic/metrics/{metric_id} | Fetch a single semantic metric by id. |
| [**history**](SemanticApi.md#history) | **GET** /api/v1/semantic/dimensions/{dimension_id}/history | Return version history for a dimension, oldest first. |
| [**history_0**](SemanticApi.md#history_0) | **GET** /api/v1/semantic/metrics/{metric_id}/history | Return version history for a metric, oldest first. |
| [**listDimensions**](SemanticApi.md#listDimensions) | **GET** /api/v1/semantic/dimensions | List all semantic dimensions for the caller&#39;s workspace. |
| [**listMetrics**](SemanticApi.md#listMetrics) | **GET** /api/v1/semantic/metrics | List all semantic metrics for the caller&#39;s workspace. |
| [**publish**](SemanticApi.md#publish) | **POST** /api/v1/semantic/dimensions/{dimension_id}:publish | Validate, compile, and publish a dimension (status → PUBLISHED). |
| [**publish_0**](SemanticApi.md#publish_0) | **POST** /api/v1/semantic/metrics/{metric_id}:publish | Validate, compile, and publish a metric (status → PUBLISHED). |
| [**retire**](SemanticApi.md#retire) | **POST** /api/v1/semantic/dimensions/{dimension_id}:retire | Retire a dimension (status → RETIRED). |
| [**retire_0**](SemanticApi.md#retire_0) | **POST** /api/v1/semantic/metrics/{metric_id}:retire | Retire a metric (status → RETIRED). |
| [**update**](SemanticApi.md#update) | **PUT** /api/v1/semantic/dimensions/{dimension_id} | Sparse-update a dimension; re-validates YAML if definition changes. |
| [**update_0**](SemanticApi.md#update_0) | **PUT** /api/v1/semantic/metrics/{metric_id} | Sparse-update a metric; re-validates YAML if definition changes. |



## create

> SemanticDimensionRead create(semanticDimensionCreate)

Create a new semantic dimension in DRAFT status.

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.SemanticApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        SemanticApi apiInstance = new SemanticApi(defaultClient);
        SemanticDimensionCreate semanticDimensionCreate = new SemanticDimensionCreate(); // SemanticDimensionCreate | 
        try {
            SemanticDimensionRead result = apiInstance.create(semanticDimensionCreate);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling SemanticApi#create");
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
| **semanticDimensionCreate** | [**SemanticDimensionCreate**](SemanticDimensionCreate.md)|  | |

### Return type

[**SemanticDimensionRead**](SemanticDimensionRead.md)

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


## create_0

> SemanticMetricRead create_0(semanticMetricCreate)

Create a new semantic metric in DRAFT status.

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.SemanticApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        SemanticApi apiInstance = new SemanticApi(defaultClient);
        SemanticMetricCreate semanticMetricCreate = new SemanticMetricCreate(); // SemanticMetricCreate | 
        try {
            SemanticMetricRead result = apiInstance.create_0(semanticMetricCreate);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling SemanticApi#create_0");
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


## getDimension

> SemanticDimensionRead getDimension(dimensionId)

Fetch a single semantic dimension by id.

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.SemanticApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        SemanticApi apiInstance = new SemanticApi(defaultClient);
        String dimensionId = "dimensionId_example"; // String | 
        try {
            SemanticDimensionRead result = apiInstance.getDimension(dimensionId);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling SemanticApi#getDimension");
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
| **dimensionId** | **String**|  | |

### Return type

[**SemanticDimensionRead**](SemanticDimensionRead.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful response |  -  |


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
import com.firefly.flyquery.api.SemanticApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        SemanticApi apiInstance = new SemanticApi(defaultClient);
        String metricId = "metricId_example"; // String | 
        try {
            SemanticMetricRead result = apiInstance.getMetric(metricId);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling SemanticApi#getMetric");
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

> history(dimensionId)

Return version history for a dimension, oldest first.

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.SemanticApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        SemanticApi apiInstance = new SemanticApi(defaultClient);
        String dimensionId = "dimensionId_example"; // String | 
        try {
            apiInstance.history(dimensionId);
        } catch (ApiException e) {
            System.err.println("Exception when calling SemanticApi#history");
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
| **dimensionId** | **String**|  | |

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


## history_0

> history_0(metricId)

Return version history for a metric, oldest first.

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.SemanticApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        SemanticApi apiInstance = new SemanticApi(defaultClient);
        String metricId = "metricId_example"; // String | 
        try {
            apiInstance.history_0(metricId);
        } catch (ApiException e) {
            System.err.println("Exception when calling SemanticApi#history_0");
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


## listDimensions

> listDimensions(datasetId)

List all semantic dimensions for the caller&#39;s workspace.

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.SemanticApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        SemanticApi apiInstance = new SemanticApi(defaultClient);
        String datasetId = "datasetId_example"; // String | 
        try {
            apiInstance.listDimensions(datasetId);
        } catch (ApiException e) {
            System.err.println("Exception when calling SemanticApi#listDimensions");
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
import com.firefly.flyquery.api.SemanticApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        SemanticApi apiInstance = new SemanticApi(defaultClient);
        String datasetId = "datasetId_example"; // String | 
        try {
            apiInstance.listMetrics(datasetId);
        } catch (ApiException e) {
            System.err.println("Exception when calling SemanticApi#listMetrics");
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

> SemanticDimensionRead publish(dimensionId)

Validate, compile, and publish a dimension (status → PUBLISHED).

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.SemanticApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        SemanticApi apiInstance = new SemanticApi(defaultClient);
        String dimensionId = "dimensionId_example"; // String | 
        try {
            SemanticDimensionRead result = apiInstance.publish(dimensionId);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling SemanticApi#publish");
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
| **dimensionId** | **String**|  | |

### Return type

[**SemanticDimensionRead**](SemanticDimensionRead.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful response |  -  |


## publish_0

> SemanticMetricRead publish_0(metricId)

Validate, compile, and publish a metric (status → PUBLISHED).

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.SemanticApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        SemanticApi apiInstance = new SemanticApi(defaultClient);
        String metricId = "metricId_example"; // String | 
        try {
            SemanticMetricRead result = apiInstance.publish_0(metricId);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling SemanticApi#publish_0");
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

> SemanticDimensionRead retire(dimensionId)

Retire a dimension (status → RETIRED).

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.SemanticApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        SemanticApi apiInstance = new SemanticApi(defaultClient);
        String dimensionId = "dimensionId_example"; // String | 
        try {
            SemanticDimensionRead result = apiInstance.retire(dimensionId);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling SemanticApi#retire");
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
| **dimensionId** | **String**|  | |

### Return type

[**SemanticDimensionRead**](SemanticDimensionRead.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful response |  -  |


## retire_0

> SemanticMetricRead retire_0(metricId)

Retire a metric (status → RETIRED).

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.SemanticApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        SemanticApi apiInstance = new SemanticApi(defaultClient);
        String metricId = "metricId_example"; // String | 
        try {
            SemanticMetricRead result = apiInstance.retire_0(metricId);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling SemanticApi#retire_0");
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

> SemanticDimensionRead update(dimensionId, semanticDimensionUpdate)

Sparse-update a dimension; re-validates YAML if definition changes.

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.SemanticApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        SemanticApi apiInstance = new SemanticApi(defaultClient);
        String dimensionId = "dimensionId_example"; // String | 
        SemanticDimensionUpdate semanticDimensionUpdate = new SemanticDimensionUpdate(); // SemanticDimensionUpdate | 
        try {
            SemanticDimensionRead result = apiInstance.update(dimensionId, semanticDimensionUpdate);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling SemanticApi#update");
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
| **dimensionId** | **String**|  | |
| **semanticDimensionUpdate** | [**SemanticDimensionUpdate**](SemanticDimensionUpdate.md)|  | |

### Return type

[**SemanticDimensionRead**](SemanticDimensionRead.md)

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


## update_0

> SemanticMetricRead update_0(metricId, semanticMetricUpdate)

Sparse-update a metric; re-validates YAML if definition changes.

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.SemanticApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        SemanticApi apiInstance = new SemanticApi(defaultClient);
        String metricId = "metricId_example"; // String | 
        SemanticMetricUpdate semanticMetricUpdate = new SemanticMetricUpdate(); // SemanticMetricUpdate | 
        try {
            SemanticMetricRead result = apiInstance.update_0(metricId, semanticMetricUpdate);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling SemanticApi#update_0");
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

