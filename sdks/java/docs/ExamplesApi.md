# ExamplesApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**approve**](ExamplesApi.md#approve) | **POST** /api/v1/examples/{example_id}:approve | Approve an example (quality → APPROVED). |
| [**create**](ExamplesApi.md#create) | **POST** /api/v1/examples | Create an example; defaults to source&#x3D;USER_CURATED, quality&#x3D;PROPOSED. |
| [**listExamples**](ExamplesApi.md#listExamples) | **GET** /api/v1/examples | List examples for the caller&#39;s workspace, with optional filters. |
| [**reject**](ExamplesApi.md#reject) | **POST** /api/v1/examples/{example_id}:reject | Reject an example (quality → REJECTED). |


<a id="approve"></a>
# **approve**
> ExampleRead approve(exampleId)

Approve an example (quality → APPROVED).

### Example
```java
// Import classes:
import io.firefly.flyquery.ApiClient;
import io.firefly.flyquery.ApiException;
import io.firefly.flyquery.Configuration;
import io.firefly.flyquery.models.*;
import io.firefly.flyquery.api.ExamplesApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");

    ExamplesApi apiInstance = new ExamplesApi(defaultClient);
    String exampleId = "exampleId_example"; // String | 
    try {
      ExampleRead result = apiInstance.approve(exampleId);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling ExamplesApi#approve");
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
| **exampleId** | **String**|  | |

### Return type

[**ExampleRead**](ExampleRead.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful response |  -  |

<a id="create"></a>
# **create**
> ExampleRead create(exampleCreate)

Create an example; defaults to source&#x3D;USER_CURATED, quality&#x3D;PROPOSED.

### Example
```java
// Import classes:
import io.firefly.flyquery.ApiClient;
import io.firefly.flyquery.ApiException;
import io.firefly.flyquery.Configuration;
import io.firefly.flyquery.models.*;
import io.firefly.flyquery.api.ExamplesApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");

    ExamplesApi apiInstance = new ExamplesApi(defaultClient);
    ExampleCreate exampleCreate = new ExampleCreate(); // ExampleCreate | 
    try {
      ExampleRead result = apiInstance.create(exampleCreate);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling ExamplesApi#create");
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
| **exampleCreate** | [**ExampleCreate**](ExampleCreate.md)|  | |

### Return type

[**ExampleRead**](ExampleRead.md)

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

<a id="listExamples"></a>
# **listExamples**
> listExamples(quality, datasetId)

List examples for the caller&#39;s workspace, with optional filters.

### Example
```java
// Import classes:
import io.firefly.flyquery.ApiClient;
import io.firefly.flyquery.ApiException;
import io.firefly.flyquery.Configuration;
import io.firefly.flyquery.models.*;
import io.firefly.flyquery.api.ExamplesApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");

    ExamplesApi apiInstance = new ExamplesApi(defaultClient);
    String quality = "quality_example"; // String | 
    String datasetId = "datasetId_example"; // String | 
    try {
      apiInstance.listExamples(quality, datasetId);
    } catch (ApiException e) {
      System.err.println("Exception when calling ExamplesApi#listExamples");
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
| **quality** | **String**|  | [optional] |
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

<a id="reject"></a>
# **reject**
> ExampleRead reject(exampleId)

Reject an example (quality → REJECTED).

### Example
```java
// Import classes:
import io.firefly.flyquery.ApiClient;
import io.firefly.flyquery.ApiException;
import io.firefly.flyquery.Configuration;
import io.firefly.flyquery.models.*;
import io.firefly.flyquery.api.ExamplesApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");

    ExamplesApi apiInstance = new ExamplesApi(defaultClient);
    String exampleId = "exampleId_example"; // String | 
    try {
      ExampleRead result = apiInstance.reject(exampleId);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling ExamplesApi#reject");
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
| **exampleId** | **String**|  | |

### Return type

[**ExampleRead**](ExampleRead.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful response |  -  |

