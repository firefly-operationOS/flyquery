# SqlApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**execute**](SqlApi.md#execute) | **POST** /api/v1/sql:execute | Execute a SQL statement directly against the workspace&#39;s dataset Parquet. |
| [**executeStream**](SqlApi.md#executeStream) | **POST** /api/v1/sql:execute/stream | Execute SQL and stream progress as Server-Sent Events. |



## execute

> SqlExecuteResponse execute(sqlExecuteRequest)

Execute a SQL statement directly against the workspace&#39;s dataset Parquet.

Requires the workspace flag &#x60;&#x60;allow_direct_sql&#x3D;true&#x60;&#x60;. The SQL is AST-classified and scope-checked; the agent pipeline is skipped.  :param http_request: Starlette request :param body: validated SqlExecuteRequest :return: SqlExecuteResponse with preview rows and execution metadata :raises DirectSqlForbidden: when workspace.allow_direct_sql is False

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.SqlApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        SqlApi apiInstance = new SqlApi(defaultClient);
        SqlExecuteRequest sqlExecuteRequest = new SqlExecuteRequest(); // SqlExecuteRequest | 
        try {
            SqlExecuteResponse result = apiInstance.execute(sqlExecuteRequest);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling SqlApi#execute");
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

Execute SQL and stream progress as Server-Sent Events.

Event sequence: 1. &#x60;&#x60;ast_classified&#x60;&#x60; — AST result + scope check outcome 2. &#x60;&#x60;executed&#x60;&#x60;       — DuckDB result 3. &#x60;&#x60;final&#x60;&#x60;          — full SqlExecuteResponse JSON  :param http_request: Starlette request :param body: validated SqlExecuteRequest :return: StreamingResponse with &#x60;&#x60;text/event-stream&#x60;&#x60;

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.SqlApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        SqlApi apiInstance = new SqlApi(defaultClient);
        SqlExecuteRequest sqlExecuteRequest = new SqlExecuteRequest(); // SqlExecuteRequest | 
        try {
            apiInstance.executeStream(sqlExecuteRequest);
        } catch (ApiException e) {
            System.err.println("Exception when calling SqlApi#executeStream");
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

