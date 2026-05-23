# flyquery_sdk.AgentSqlExecuteApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**execute**](AgentSqlExecuteApi.md#execute) | **POST** /api/v1/agent/sql:execute | Execute SQL directly (agent-tier).
[**execute_stream**](AgentSqlExecuteApi.md#execute_stream) | **POST** /api/v1/agent/sql:execute/stream | Execute SQL as SSE stream (agent-tier).


# **execute**
> SqlExecuteResponse execute(sql_execute_request)

Execute SQL directly (agent-tier).

:param http_request: Starlette request
:param body: validated SqlExecuteRequest
:return: SqlExecuteResponse

### Example


```python
import flyquery_sdk
from flyquery_sdk.models.sql_execute_request import SqlExecuteRequest
from flyquery_sdk.models.sql_execute_response import SqlExecuteResponse
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
    api_instance = flyquery_sdk.AgentSqlExecuteApi(api_client)
    sql_execute_request = flyquery_sdk.SqlExecuteRequest() # SqlExecuteRequest | 

    try:
        # Execute SQL directly (agent-tier).
        api_response = await api_instance.execute(sql_execute_request)
        print("The response of AgentSqlExecuteApi->execute:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentSqlExecuteApi->execute: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sql_execute_request** | [**SqlExecuteRequest**](SqlExecuteRequest.md)|  | 

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
**200** | Successful response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **execute_stream**
> execute_stream(sql_execute_request)

Execute SQL as SSE stream (agent-tier).

:param http_request: Starlette request
:param body: validated SqlExecuteRequest
:return: StreamingResponse with text/event-stream

### Example


```python
import flyquery_sdk
from flyquery_sdk.models.sql_execute_request import SqlExecuteRequest
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
    api_instance = flyquery_sdk.AgentSqlExecuteApi(api_client)
    sql_execute_request = flyquery_sdk.SqlExecuteRequest() # SqlExecuteRequest | 

    try:
        # Execute SQL as SSE stream (agent-tier).
        await api_instance.execute_stream(sql_execute_request)
    except Exception as e:
        print("Exception when calling AgentSqlExecuteApi->execute_stream: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sql_execute_request** | [**SqlExecuteRequest**](SqlExecuteRequest.md)|  | 

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

