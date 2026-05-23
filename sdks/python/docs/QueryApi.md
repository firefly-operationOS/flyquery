# flyquery_sdk.QueryApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**batch**](QueryApi.md#batch) | **POST** /api/v1/query:batch | Run multiple NL questions in parallel through the full pipeline.
[**explain**](QueryApi.md#explain) | **POST** /api/v1/query:explain | Run Grounding + Generation but stop before AST/execution.
[**query**](QueryApi.md#query) | **POST** /api/v1/query | Run the full NL → SQL → result pipeline and return a synchronous answer.
[**stream**](QueryApi.md#stream) | **POST** /api/v1/query/stream | Run the full pipeline as a Server-Sent Events stream.
[**validate**](QueryApi.md#validate) | **POST** /api/v1/query:validate | Run Grounding + Generation + AST classification + ScopeGuard check.


# **batch**
> BatchQueryResponse batch(batch_query_request)

Run multiple NL questions in parallel through the full pipeline.

Each item runs the same pipeline as ``POST /api/v1/query``, fanned
out via ``asyncio.gather`` with a Semaphore-style concurrency cap
(mirrors the bulk-file endpoint). Per-question failures do NOT
abort the batch -- failed items carry ``status="FAILED"`` +
``error`` and the response aggregates ``succeeded`` / ``failed``
counts.

Use this for dashboard refreshes (one batch with N panel queries),
comparison reports (same question against M datasets), or SDK
callers that want to amortise auth + tenant context across many
questions.

### Example


```python
import flyquery_sdk
from flyquery_sdk.models.batch_query_request import BatchQueryRequest
from flyquery_sdk.models.batch_query_response import BatchQueryResponse
from flyquery_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = flyquery_sdk.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
async with flyquery_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = flyquery_sdk.QueryApi(api_client)
    batch_query_request = flyquery_sdk.BatchQueryRequest() # BatchQueryRequest | 

    try:
        # Run multiple NL questions in parallel through the full pipeline.
        api_response = await api_instance.batch(batch_query_request)
        print("The response of QueryApi->batch:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling QueryApi->batch: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **batch_query_request** | [**BatchQueryRequest**](BatchQueryRequest.md)|  | 

### Return type

[**BatchQueryResponse**](BatchQueryResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **explain**
> ExplainResponse explain(query_request)

Run Grounding + Generation but stop before AST/execution.

Useful for previewing the generated SQL without paying execution costs.

:param http_request: Starlette request
:param body: validated QueryRequest
:return: ExplainResponse with candidate SQL and reasoning

### Example


```python
import flyquery_sdk
from flyquery_sdk.models.explain_response import ExplainResponse
from flyquery_sdk.models.query_request import QueryRequest
from flyquery_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = flyquery_sdk.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
async with flyquery_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = flyquery_sdk.QueryApi(api_client)
    query_request = flyquery_sdk.QueryRequest() # QueryRequest | 

    try:
        # Run Grounding + Generation but stop before AST/execution.
        api_response = await api_instance.explain(query_request)
        print("The response of QueryApi->explain:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling QueryApi->explain: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **query_request** | [**QueryRequest**](QueryRequest.md)|  | 

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
**200** | Successful response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **query**
> AnswerResponse query(query_request)

Run the full NL → SQL → result pipeline and return a synchronous answer.

:param http_request: Starlette request (provides tenant context headers)
:param body: validated QueryRequest
:return: AnswerResponse with SQL, preview rows, chart hint, and explanation

### Example


```python
import flyquery_sdk
from flyquery_sdk.models.answer_response import AnswerResponse
from flyquery_sdk.models.query_request import QueryRequest
from flyquery_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = flyquery_sdk.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
async with flyquery_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = flyquery_sdk.QueryApi(api_client)
    query_request = flyquery_sdk.QueryRequest() # QueryRequest | 

    try:
        # Run the full NL → SQL → result pipeline and return a synchronous answer.
        api_response = await api_instance.query(query_request)
        print("The response of QueryApi->query:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling QueryApi->query: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **query_request** | [**QueryRequest**](QueryRequest.md)|  | 

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
**200** | Successful response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **stream**
> stream(query_request)

Run the full pipeline as a Server-Sent Events stream.

Event sequence:
1. ``schema_linked``   — after grounding completes
2. ``clarification``   — (optional) when confidence < threshold + missing_info
3. ``sql_generated``   — after generation
4. ``executed``        — after DuckDB execution
5. ``explained``       — after ExplainerAgent
6. ``final``           — full AnswerResponse JSON

:param http_request: Starlette request
:param body: validated QueryRequest (body already consumed by pyfly)
:return: StreamingResponse with ``text/event-stream`` content type

### Example


```python
import flyquery_sdk
from flyquery_sdk.models.query_request import QueryRequest
from flyquery_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = flyquery_sdk.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
async with flyquery_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = flyquery_sdk.QueryApi(api_client)
    query_request = flyquery_sdk.QueryRequest() # QueryRequest | 

    try:
        # Run the full pipeline as a Server-Sent Events stream.
        await api_instance.stream(query_request)
    except Exception as e:
        print("Exception when calling QueryApi->stream: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **query_request** | [**QueryRequest**](QueryRequest.md)|  | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **validate**
> ValidateResponse validate(query_request)

Run Grounding + Generation + AST classification + ScopeGuard check.

Returns the classification and any scope error without executing the SQL.

:param http_request: Starlette request
:param body: validated QueryRequest
:return: ValidateResponse with AST classification and optional scope_error

### Example


```python
import flyquery_sdk
from flyquery_sdk.models.query_request import QueryRequest
from flyquery_sdk.models.validate_response import ValidateResponse
from flyquery_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = flyquery_sdk.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
async with flyquery_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = flyquery_sdk.QueryApi(api_client)
    query_request = flyquery_sdk.QueryRequest() # QueryRequest | 

    try:
        # Run Grounding + Generation + AST classification + ScopeGuard check.
        api_response = await api_instance.validate(query_request)
        print("The response of QueryApi->validate:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling QueryApi->validate: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **query_request** | [**QueryRequest**](QueryRequest.md)|  | 

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
**200** | Successful response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

