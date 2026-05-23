# AgentQueryApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**explain**](AgentQueryApi.md#explain) | **POST** /api/v1/agent/query:explain | Run Grounding + Generation only (agent-tier). |
| [**query**](AgentQueryApi.md#query) | **POST** /api/v1/agent/query | Run the full NL → SQL → result pipeline (agent-tier). |
| [**stream**](AgentQueryApi.md#stream) | **POST** /api/v1/agent/query/stream | Run the pipeline as SSE stream (agent-tier). |
| [**validate**](AgentQueryApi.md#validate) | **POST** /api/v1/agent/query:validate | Run Grounding + Generation + AST + ScopeGuard (agent-tier). |


<a id="explain"></a>
# **explain**
> ExplainResponse explain(queryRequest)

Run Grounding + Generation only (agent-tier).

:param http_request: Starlette request :param body: validated QueryRequest :return: ExplainResponse with candidate SQL and reasoning

### Example
```java
// Import classes:
import io.firefly.flyquery.ApiClient;
import io.firefly.flyquery.ApiException;
import io.firefly.flyquery.Configuration;
import io.firefly.flyquery.models.*;
import io.firefly.flyquery.api.AgentQueryApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");

    AgentQueryApi apiInstance = new AgentQueryApi(defaultClient);
    QueryRequest queryRequest = new QueryRequest(); // QueryRequest | 
    try {
      ExplainResponse result = apiInstance.explain(queryRequest);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling AgentQueryApi#explain");
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

<a id="query"></a>
# **query**
> AnswerResponse query(queryRequest)

Run the full NL → SQL → result pipeline (agent-tier).

:param http_request: Starlette request (provides tenant context + agent token) :param body: validated QueryRequest :return: AnswerResponse

### Example
```java
// Import classes:
import io.firefly.flyquery.ApiClient;
import io.firefly.flyquery.ApiException;
import io.firefly.flyquery.Configuration;
import io.firefly.flyquery.models.*;
import io.firefly.flyquery.api.AgentQueryApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");

    AgentQueryApi apiInstance = new AgentQueryApi(defaultClient);
    QueryRequest queryRequest = new QueryRequest(); // QueryRequest | 
    try {
      AnswerResponse result = apiInstance.query(queryRequest);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling AgentQueryApi#query");
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

<a id="stream"></a>
# **stream**
> stream(queryRequest)

Run the pipeline as SSE stream (agent-tier).

:param http_request: Starlette request :param body: validated QueryRequest :return: StreamingResponse with text/event-stream

### Example
```java
// Import classes:
import io.firefly.flyquery.ApiClient;
import io.firefly.flyquery.ApiException;
import io.firefly.flyquery.Configuration;
import io.firefly.flyquery.models.*;
import io.firefly.flyquery.api.AgentQueryApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");

    AgentQueryApi apiInstance = new AgentQueryApi(defaultClient);
    QueryRequest queryRequest = new QueryRequest(); // QueryRequest | 
    try {
      apiInstance.stream(queryRequest);
    } catch (ApiException e) {
      System.err.println("Exception when calling AgentQueryApi#stream");
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

<a id="validate"></a>
# **validate**
> ValidateResponse validate(queryRequest)

Run Grounding + Generation + AST + ScopeGuard (agent-tier).

:param http_request: Starlette request :param body: validated QueryRequest :return: ValidateResponse

### Example
```java
// Import classes:
import io.firefly.flyquery.ApiClient;
import io.firefly.flyquery.ApiException;
import io.firefly.flyquery.Configuration;
import io.firefly.flyquery.models.*;
import io.firefly.flyquery.api.AgentQueryApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");

    AgentQueryApi apiInstance = new AgentQueryApi(defaultClient);
    QueryRequest queryRequest = new QueryRequest(); // QueryRequest | 
    try {
      ValidateResponse result = apiInstance.validate(queryRequest);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling AgentQueryApi#validate");
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

