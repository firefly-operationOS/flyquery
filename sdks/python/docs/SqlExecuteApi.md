# flyquery_sdk.SqlExecuteApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**execute**](SqlExecuteApi.md#execute) | **POST** /api/v1/sql:execute | Execute a SQL statement directly against the workspace&#39;s dataset Parquet.
[**execute_stream**](SqlExecuteApi.md#execute_stream) | **POST** /api/v1/sql:execute/stream | Execute SQL and stream progress as Server-Sent Events.


# **execute**
> SqlExecuteResponse execute(sql_execute_request)

Execute a SQL statement directly against the workspace's dataset Parquet.

Requires the workspace flag ``allow_direct_sql=true``. The SQL is
AST-classified and scope-checked; the agent pipeline is skipped.

:param http_request: Starlette request
:param body: validated SqlExecuteRequest
:return: SqlExecuteResponse with preview rows and execution metadata
:raises DirectSqlForbidden: when workspace.allow_direct_sql is False

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
    api_instance = flyquery_sdk.SqlExecuteApi(api_client)
    sql_execute_request = flyquery_sdk.SqlExecuteRequest() # SqlExecuteRequest | 

    try:
        # Execute a SQL statement directly against the workspace's dataset Parquet.
        api_response = await api_instance.execute(sql_execute_request)
        print("The response of SqlExecuteApi->execute:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SqlExecuteApi->execute: %s\n" % e)
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

Execute SQL and stream progress as Server-Sent Events.

Event sequence:
1. ``ast_classified`` — AST result + scope check outcome
2. ``executed``       — DuckDB result
3. ``final``          — full SqlExecuteResponse JSON

:param http_request: Starlette request
:param body: validated SqlExecuteRequest
:return: StreamingResponse with ``text/event-stream``

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
    api_instance = flyquery_sdk.SqlExecuteApi(api_client)
    sql_execute_request = flyquery_sdk.SqlExecuteRequest() # SqlExecuteRequest | 

    try:
        # Execute SQL and stream progress as Server-Sent Events.
        await api_instance.execute_stream(sql_execute_request)
    except Exception as e:
        print("Exception when calling SqlExecuteApi->execute_stream: %s\n" % e)
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

