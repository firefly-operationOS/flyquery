# flyquery_sdk.AgentQueryApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**explain**](AgentQueryApi.md#explain) | **POST** /api/v1/agent/query:explain | Run Grounding + Generation only (agent-tier).
[**query**](AgentQueryApi.md#query) | **POST** /api/v1/agent/query | Run the full NL → SQL → result pipeline (agent-tier).
[**stream**](AgentQueryApi.md#stream) | **POST** /api/v1/agent/query/stream | Run the pipeline as SSE stream (agent-tier).
[**validate**](AgentQueryApi.md#validate) | **POST** /api/v1/agent/query:validate | Run Grounding + Generation + AST + ScopeGuard (agent-tier).


# **explain**
> ExplainResponse explain(query_request)

Run Grounding + Generation only (agent-tier).

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
    api_instance = flyquery_sdk.AgentQueryApi(api_client)
    query_request = flyquery_sdk.QueryRequest() # QueryRequest | 

    try:
        # Run Grounding + Generation only (agent-tier).
        api_response = await api_instance.explain(query_request)
        print("The response of AgentQueryApi->explain:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentQueryApi->explain: %s\n" % e)
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

Run the full NL → SQL → result pipeline (agent-tier).

:param http_request: Starlette request (provides tenant context + agent token)
:param body: validated QueryRequest
:return: AnswerResponse

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
    api_instance = flyquery_sdk.AgentQueryApi(api_client)
    query_request = flyquery_sdk.QueryRequest() # QueryRequest | 

    try:
        # Run the full NL → SQL → result pipeline (agent-tier).
        api_response = await api_instance.query(query_request)
        print("The response of AgentQueryApi->query:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentQueryApi->query: %s\n" % e)
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

Run the pipeline as SSE stream (agent-tier).

:param http_request: Starlette request
:param body: validated QueryRequest
:return: StreamingResponse with text/event-stream

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
    api_instance = flyquery_sdk.AgentQueryApi(api_client)
    query_request = flyquery_sdk.QueryRequest() # QueryRequest | 

    try:
        # Run the pipeline as SSE stream (agent-tier).
        await api_instance.stream(query_request)
    except Exception as e:
        print("Exception when calling AgentQueryApi->stream: %s\n" % e)
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

Run Grounding + Generation + AST + ScopeGuard (agent-tier).

:param http_request: Starlette request
:param body: validated QueryRequest
:return: ValidateResponse

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
    api_instance = flyquery_sdk.AgentQueryApi(api_client)
    query_request = flyquery_sdk.QueryRequest() # QueryRequest | 

    try:
        # Run Grounding + Generation + AST + ScopeGuard (agent-tier).
        api_response = await api_instance.validate(query_request)
        print("The response of AgentQueryApi->validate:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentQueryApi->validate: %s\n" % e)
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

