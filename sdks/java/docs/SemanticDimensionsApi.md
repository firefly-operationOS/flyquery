# SemanticDimensionsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**create**](SemanticDimensionsApi.md#create) | **POST** /api/v1/semantic/dimensions | Create a new semantic dimension in DRAFT status. |
| [**getDimension**](SemanticDimensionsApi.md#getDimension) | **GET** /api/v1/semantic/dimensions/{dimension_id} | Fetch a single semantic dimension by id. |
| [**history**](SemanticDimensionsApi.md#history) | **GET** /api/v1/semantic/dimensions/{dimension_id}/history | Return version history for a dimension, oldest first. |
| [**listDimensions**](SemanticDimensionsApi.md#listDimensions) | **GET** /api/v1/semantic/dimensions | List all semantic dimensions for the caller&#39;s workspace. |
| [**publish**](SemanticDimensionsApi.md#publish) | **POST** /api/v1/semantic/dimensions/{dimension_id}:publish | Validate, compile, and publish a dimension (status → PUBLISHED). |
| [**retire**](SemanticDimensionsApi.md#retire) | **POST** /api/v1/semantic/dimensions/{dimension_id}:retire | Retire a dimension (status → RETIRED). |
| [**update**](SemanticDimensionsApi.md#update) | **PUT** /api/v1/semantic/dimensions/{dimension_id} | Sparse-update a dimension; re-validates YAML if definition changes. |



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
import com.firefly.flyquery.api.SemanticDimensionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        SemanticDimensionsApi apiInstance = new SemanticDimensionsApi(defaultClient);
        SemanticDimensionCreate semanticDimensionCreate = new SemanticDimensionCreate(); // SemanticDimensionCreate | 
        try {
            SemanticDimensionRead result = apiInstance.create(semanticDimensionCreate);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling SemanticDimensionsApi#create");
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
import com.firefly.flyquery.api.SemanticDimensionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        SemanticDimensionsApi apiInstance = new SemanticDimensionsApi(defaultClient);
        String dimensionId = "dimensionId_example"; // String | 
        try {
            SemanticDimensionRead result = apiInstance.getDimension(dimensionId);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling SemanticDimensionsApi#getDimension");
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
import com.firefly.flyquery.api.SemanticDimensionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        SemanticDimensionsApi apiInstance = new SemanticDimensionsApi(defaultClient);
        String dimensionId = "dimensionId_example"; // String | 
        try {
            apiInstance.history(dimensionId);
        } catch (ApiException e) {
            System.err.println("Exception when calling SemanticDimensionsApi#history");
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
import com.firefly.flyquery.api.SemanticDimensionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        SemanticDimensionsApi apiInstance = new SemanticDimensionsApi(defaultClient);
        String datasetId = "datasetId_example"; // String | 
        try {
            apiInstance.listDimensions(datasetId);
        } catch (ApiException e) {
            System.err.println("Exception when calling SemanticDimensionsApi#listDimensions");
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
import com.firefly.flyquery.api.SemanticDimensionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        SemanticDimensionsApi apiInstance = new SemanticDimensionsApi(defaultClient);
        String dimensionId = "dimensionId_example"; // String | 
        try {
            SemanticDimensionRead result = apiInstance.publish(dimensionId);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling SemanticDimensionsApi#publish");
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
import com.firefly.flyquery.api.SemanticDimensionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        SemanticDimensionsApi apiInstance = new SemanticDimensionsApi(defaultClient);
        String dimensionId = "dimensionId_example"; // String | 
        try {
            SemanticDimensionRead result = apiInstance.retire(dimensionId);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling SemanticDimensionsApi#retire");
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
import com.firefly.flyquery.api.SemanticDimensionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        SemanticDimensionsApi apiInstance = new SemanticDimensionsApi(defaultClient);
        String dimensionId = "dimensionId_example"; // String | 
        SemanticDimensionUpdate semanticDimensionUpdate = new SemanticDimensionUpdate(); // SemanticDimensionUpdate | 
        try {
            SemanticDimensionRead result = apiInstance.update(dimensionId, semanticDimensionUpdate);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling SemanticDimensionsApi#update");
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

