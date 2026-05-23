# QueryApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**explain**](QueryApi.md#explain) | **POST** /api/v1/query:explain | Run Grounding + Generation but stop before AST/execution. |
| [**query**](QueryApi.md#query) | **POST** /api/v1/query | Run the full NL → SQL → result pipeline and return a synchronous answer. |
| [**stream**](QueryApi.md#stream) | **POST** /api/v1/query/stream | Run the full pipeline as a Server-Sent Events stream. |
| [**validate**](QueryApi.md#validate) | **POST** /api/v1/query:validate | Run Grounding + Generation + AST classification + ScopeGuard check. |



## explain

> ExplainResponse explain(queryRequest)

Run Grounding + Generation but stop before AST/execution.

Useful for previewing the generated SQL without paying execution costs.  :param http_request: Starlette request :param body: validated QueryRequest :return: ExplainResponse with candidate SQL and reasoning

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.QueryApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        QueryApi apiInstance = new QueryApi(defaultClient);
        QueryRequest queryRequest = new QueryRequest(); // QueryRequest | 
        try {
            ExplainResponse result = apiInstance.explain(queryRequest);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling QueryApi#explain");
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
| **queryRequest** | [**QueryRequest**](QueryRequest.md)|  | |

### Return type

[**ExplainResponse**](ExplainResponse.md)

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


## query

> AnswerResponse query(queryRequest)

Run the full NL → SQL → result pipeline and return a synchronous answer.

:param http_request: Starlette request (provides tenant context headers) :param body: validated QueryRequest :return: AnswerResponse with SQL, preview rows, chart hint, and explanation

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.QueryApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        QueryApi apiInstance = new QueryApi(defaultClient);
        QueryRequest queryRequest = new QueryRequest(); // QueryRequest | 
        try {
            AnswerResponse result = apiInstance.query(queryRequest);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling QueryApi#query");
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
| **queryRequest** | [**QueryRequest**](QueryRequest.md)|  | |

### Return type

[**AnswerResponse**](AnswerResponse.md)

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


## stream

> stream(queryRequest)

Run the full pipeline as a Server-Sent Events stream.

Event sequence: 1. &#x60;&#x60;schema_linked&#x60;&#x60;   — after grounding completes 2. &#x60;&#x60;clarification&#x60;&#x60;   — (optional) when confidence &lt; threshold + missing_info 3. &#x60;&#x60;sql_generated&#x60;&#x60;   — after generation 4. &#x60;&#x60;executed&#x60;&#x60;        — after DuckDB execution 5. &#x60;&#x60;explained&#x60;&#x60;       — after ExplainerAgent 6. &#x60;&#x60;final&#x60;&#x60;           — full AnswerResponse JSON  :param http_request: Starlette request :param body: validated QueryRequest (body already consumed by pyfly) :return: StreamingResponse with &#x60;&#x60;text/event-stream&#x60;&#x60; content type

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.QueryApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        QueryApi apiInstance = new QueryApi(defaultClient);
        QueryRequest queryRequest = new QueryRequest(); // QueryRequest | 
        try {
            apiInstance.stream(queryRequest);
        } catch (ApiException e) {
            System.err.println("Exception when calling QueryApi#stream");
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
| **queryRequest** | [**QueryRequest**](QueryRequest.md)|  | |

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


## validate

> ValidateResponse validate(queryRequest)

Run Grounding + Generation + AST classification + ScopeGuard check.

Returns the classification and any scope error without executing the SQL.  :param http_request: Starlette request :param body: validated QueryRequest :return: ValidateResponse with AST classification and optional scope_error

### Example

```java
// Import classes:
import com.firefly.flyquery.ApiClient;
import com.firefly.flyquery.ApiException;
import com.firefly.flyquery.Configuration;
import com.firefly.flyquery.models.*;
import com.firefly.flyquery.api.QueryApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        QueryApi apiInstance = new QueryApi(defaultClient);
        QueryRequest queryRequest = new QueryRequest(); // QueryRequest | 
        try {
            ValidateResponse result = apiInstance.validate(queryRequest);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling QueryApi#validate");
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
| **queryRequest** | [**QueryRequest**](QueryRequest.md)|  | |

### Return type

[**ValidateResponse**](ValidateResponse.md)

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

