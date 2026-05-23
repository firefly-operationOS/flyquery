# MetaApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**version**](MetaApi.md#version) | **GET** /api/v1/agent/version | Return service name + CalVer version tag. |
| [**version_0**](MetaApi.md#version_0) | **GET** /api/v1/version | Return service name + CalVer version tag. |


<a id="version"></a>
# **version**
> version()

Return service name + CalVer version tag.

Requires a valid &#x60;&#x60;X-Agent-Token&#x60;&#x60; with &#x60;&#x60;flyquery.audit:read&#x60;&#x60; scope. Missing or invalid tokens return 401 / 403 respectively.

### Example
```java
// Import classes:
import io.firefly.flyquery.ApiClient;
import io.firefly.flyquery.ApiException;
import io.firefly.flyquery.Configuration;
import io.firefly.flyquery.models.*;
import io.firefly.flyquery.api.MetaApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");

    MetaApi apiInstance = new MetaApi(defaultClient);
    try {
      apiInstance.version();
    } catch (ApiException e) {
      System.err.println("Exception when calling MetaApi#version");
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

<a id="version_0"></a>
# **version_0**
> version_0()

Return service name + CalVer version tag.

### Example
```java
// Import classes:
import io.firefly.flyquery.ApiClient;
import io.firefly.flyquery.ApiException;
import io.firefly.flyquery.Configuration;
import io.firefly.flyquery.models.*;
import io.firefly.flyquery.api.MetaApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");

    MetaApi apiInstance = new MetaApi(defaultClient);
    try {
      apiInstance.version_0();
    } catch (ApiException e) {
      System.err.println("Exception when calling MetaApi#version_0");
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

