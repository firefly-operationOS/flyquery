# AgentVersionApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**version**](AgentVersionApi.md#version) | **GET** /api/v1/agent/version | Return service name + CalVer version tag. |



## version

> version()

Return service name + CalVer version tag.

Requires a valid &#x60;&#x60;X-Agent-Token&#x60;&#x60; with &#x60;&#x60;flyquery.audit:read&#x60;&#x60; scope. Missing or invalid tokens return 401 / 403 respectively.

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.AgentVersionApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentVersionApi apiInstance = new AgentVersionApi(defaultClient);
        try {
            apiInstance.version();
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentVersionApi#version");
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

