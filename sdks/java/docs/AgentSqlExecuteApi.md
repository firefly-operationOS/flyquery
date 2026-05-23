# AgentSqlExecuteApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**execute**](AgentSqlExecuteApi.md#execute) | **POST** /api/v1/agent/sql:execute | Execute SQL directly (agent-tier). |
| [**executeStream**](AgentSqlExecuteApi.md#executeStream) | **POST** /api/v1/agent/sql:execute/stream | Execute SQL as SSE stream (agent-tier). |



## execute

> SqlExecuteResponse execute(sqlExecuteRequest)

Execute SQL directly (agent-tier).

:param http_request: Starlette request :param body: validated SqlExecuteRequest :return: SqlExecuteResponse

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.AgentSqlExecuteApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSqlExecuteApi apiInstance = new AgentSqlExecuteApi(defaultClient);
        SqlExecuteRequest sqlExecuteRequest = new SqlExecuteRequest(); // SqlExecuteRequest | 
        try {
            SqlExecuteResponse result = apiInstance.execute(sqlExecuteRequest);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSqlExecuteApi#execute");
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
| **sqlExecuteRequest** | [**SqlExecuteRequest**](SqlExecuteRequest.md)|  | |

### Return type

[**SqlExecuteResponse**](SqlExecuteResponse.md)

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


## executeStream

> executeStream(sqlExecuteRequest)

Execute SQL as SSE stream (agent-tier).

:param http_request: Starlette request :param body: validated SqlExecuteRequest :return: StreamingResponse with text/event-stream

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.AgentSqlExecuteApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSqlExecuteApi apiInstance = new AgentSqlExecuteApi(defaultClient);
        SqlExecuteRequest sqlExecuteRequest = new SqlExecuteRequest(); // SqlExecuteRequest | 
        try {
            apiInstance.executeStream(sqlExecuteRequest);
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSqlExecuteApi#executeStream");
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
| **sqlExecuteRequest** | [**SqlExecuteRequest**](SqlExecuteRequest.md)|  | |

### Return type

null (empty response body)

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

