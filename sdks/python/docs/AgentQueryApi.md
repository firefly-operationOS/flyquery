# flyquery_sdk.AgentQueryApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**batch**](AgentQueryApi.md#batch) | **POST** /api/v1/agent/query:batch | Agent-tier mirror of POST /api/v1/query:batch.
[**explain**](AgentQueryApi.md#explain) | **POST** /api/v1/agent/query:explain | Run Grounding + Generation only (agent-tier).
[**query**](AgentQueryApi.md#query) | **POST** /api/v1/agent/query | Run the full NL → SQL → result pipeline (agent-tier).
[**stream**](AgentQueryApi.md#stream) | **POST** /api/v1/agent/query/stream | Run the pipeline as SSE stream (agent-tier).
[**validate**](AgentQueryApi.md#validate) | **POST** /api/v1/agent/query:validate | Run Grounding + Generation + AST + ScopeGuard (agent-tier).


# **batch**
> BatchQueryResponse batch(x_agent_token, batch_query_request, x_correlation_id=x_correlation_id, idempotency_key=idempotency_key)

Agent-tier mirror of POST /api/v1/query:batch.

Delegates to the user-tier ``QueryController.batch`` by
instantiating it inline (same pattern as :meth:`stream`).
Replay-dedup'd via ``Idempotency-Key`` (required) -- a batch
is N parallel multi-LLM pipelines, the costliest single
request shape in the API.

### Example

* Api Key Authentication (AgentToken):

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

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: AgentToken
configuration.api_key['AgentToken'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['AgentToken'] = 'Bearer'

# Enter a context with an instance of the API client
async with flyquery_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = flyquery_sdk.AgentQueryApi(api_client)
    x_agent_token = 'fqt_live_aBcDeF1234567890aBcDeF1234567890' # str | Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token's claims encode the tenant + workspace + scopes. Issue via ``POST /api/v1/agent-tokens``.
    batch_query_request = flyquery_sdk.BatchQueryRequest() # BatchQueryRequest | 
    x_correlation_id = UUID('550e8400-e29b-41d4-a716-446655440000') # UUID | Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. (optional)
    idempotency_key = 'ingest-2026-05-23-abc123' # str | Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h. (optional)

    try:
        # Agent-tier mirror of POST /api/v1/query:batch.
        api_response = await api_instance.batch(x_agent_token, batch_query_request, x_correlation_id=x_correlation_id, idempotency_key=idempotency_key)
        print("The response of AgentQueryApi->batch:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentQueryApi->batch: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **x_agent_token** | **str**| Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;. | 
 **batch_query_request** | [**BatchQueryRequest**](BatchQueryRequest.md)|  | 
 **x_correlation_id** | **UUID**| Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. | [optional] 
 **idempotency_key** | **str**| Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h. | [optional] 

### Return type

[**BatchQueryResponse**](BatchQueryResponse.md)

### Authorization

[AgentToken](../README.md#AgentToken)

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
> ExplainResponse explain(x_agent_token, query_request, x_correlation_id=x_correlation_id, idempotency_key=idempotency_key)

Run Grounding + Generation only (agent-tier).

:param http_request: Starlette request
:param body: validated QueryRequest
:return: ExplainResponse with candidate SQL and reasoning

### Example

* Api Key Authentication (AgentToken):

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

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: AgentToken
configuration.api_key['AgentToken'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['AgentToken'] = 'Bearer'

# Enter a context with an instance of the API client
async with flyquery_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = flyquery_sdk.AgentQueryApi(api_client)
    x_agent_token = 'fqt_live_aBcDeF1234567890aBcDeF1234567890' # str | Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token's claims encode the tenant + workspace + scopes. Issue via ``POST /api/v1/agent-tokens``.
    query_request = flyquery_sdk.QueryRequest() # QueryRequest | 
    x_correlation_id = UUID('550e8400-e29b-41d4-a716-446655440000') # UUID | Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. (optional)
    idempotency_key = 'ingest-2026-05-23-abc123' # str | Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h. (optional)

    try:
        # Run Grounding + Generation only (agent-tier).
        api_response = await api_instance.explain(x_agent_token, query_request, x_correlation_id=x_correlation_id, idempotency_key=idempotency_key)
        print("The response of AgentQueryApi->explain:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentQueryApi->explain: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **x_agent_token** | **str**| Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;. | 
 **query_request** | [**QueryRequest**](QueryRequest.md)|  | 
 **x_correlation_id** | **UUID**| Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. | [optional] 
 **idempotency_key** | **str**| Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h. | [optional] 

### Return type

[**ExplainResponse**](ExplainResponse.md)

### Authorization

[AgentToken](../README.md#AgentToken)

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
> AnswerResponse query(x_agent_token, query_request, x_correlation_id=x_correlation_id, idempotency_key=idempotency_key)

Run the full NL → SQL → result pipeline (agent-tier).

Replay-dedup'd via ``Idempotency-Key``. The header is *required*
on the agent surface so an at-least-once delivery agent (which
retries on network error) doesn't burn budget by re-running the
same multi-LLM pipeline twice.

:param http_request: Starlette request (provides tenant context + agent token)
:param body: validated QueryRequest
:return: AnswerResponse

### Example

* Api Key Authentication (AgentToken):

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

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: AgentToken
configuration.api_key['AgentToken'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['AgentToken'] = 'Bearer'

# Enter a context with an instance of the API client
async with flyquery_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = flyquery_sdk.AgentQueryApi(api_client)
    x_agent_token = 'fqt_live_aBcDeF1234567890aBcDeF1234567890' # str | Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token's claims encode the tenant + workspace + scopes. Issue via ``POST /api/v1/agent-tokens``.
    query_request = flyquery_sdk.QueryRequest() # QueryRequest | 
    x_correlation_id = UUID('550e8400-e29b-41d4-a716-446655440000') # UUID | Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. (optional)
    idempotency_key = 'ingest-2026-05-23-abc123' # str | Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h. (optional)

    try:
        # Run the full NL → SQL → result pipeline (agent-tier).
        api_response = await api_instance.query(x_agent_token, query_request, x_correlation_id=x_correlation_id, idempotency_key=idempotency_key)
        print("The response of AgentQueryApi->query:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentQueryApi->query: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **x_agent_token** | **str**| Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;. | 
 **query_request** | [**QueryRequest**](QueryRequest.md)|  | 
 **x_correlation_id** | **UUID**| Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. | [optional] 
 **idempotency_key** | **str**| Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h. | [optional] 

### Return type

[**AnswerResponse**](AnswerResponse.md)

### Authorization

[AgentToken](../README.md#AgentToken)

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
> str stream(x_agent_token, query_request, x_correlation_id=x_correlation_id, idempotency_key=idempotency_key)

Run the pipeline as SSE stream (agent-tier).

:param http_request: Starlette request
:param body: validated QueryRequest
:return: StreamingResponse with text/event-stream

### Example

* Api Key Authentication (AgentToken):

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

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: AgentToken
configuration.api_key['AgentToken'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['AgentToken'] = 'Bearer'

# Enter a context with an instance of the API client
async with flyquery_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = flyquery_sdk.AgentQueryApi(api_client)
    x_agent_token = 'fqt_live_aBcDeF1234567890aBcDeF1234567890' # str | Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token's claims encode the tenant + workspace + scopes. Issue via ``POST /api/v1/agent-tokens``.
    query_request = flyquery_sdk.QueryRequest() # QueryRequest | 
    x_correlation_id = UUID('550e8400-e29b-41d4-a716-446655440000') # UUID | Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. (optional)
    idempotency_key = 'ingest-2026-05-23-abc123' # str | Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h. (optional)

    try:
        # Run the pipeline as SSE stream (agent-tier).
        api_response = await api_instance.stream(x_agent_token, query_request, x_correlation_id=x_correlation_id, idempotency_key=idempotency_key)
        print("The response of AgentQueryApi->stream:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentQueryApi->stream: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **x_agent_token** | **str**| Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;. | 
 **query_request** | [**QueryRequest**](QueryRequest.md)|  | 
 **x_correlation_id** | **UUID**| Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. | [optional] 
 **idempotency_key** | **str**| Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h. | [optional] 

### Return type

**str**

### Authorization

[AgentToken](../README.md#AgentToken)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: text/event-stream, application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Server-Sent Events stream. Each frame follows the SSE wire format &#x60;&#x60;event: &lt;name&gt;\\ndata: &lt;json&gt;\\n\\n&#x60;&#x60;. See &#x60;&#x60;docs/api-reference.md&#x60;&#x60; section 8 for the per-endpoint event catalogue. |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **validate**
> ValidateResponse validate(x_agent_token, query_request, x_correlation_id=x_correlation_id, idempotency_key=idempotency_key)

Run Grounding + Generation + AST + ScopeGuard (agent-tier).

:param http_request: Starlette request
:param body: validated QueryRequest
:return: ValidateResponse

### Example

* Api Key Authentication (AgentToken):

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

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: AgentToken
configuration.api_key['AgentToken'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['AgentToken'] = 'Bearer'

# Enter a context with an instance of the API client
async with flyquery_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = flyquery_sdk.AgentQueryApi(api_client)
    x_agent_token = 'fqt_live_aBcDeF1234567890aBcDeF1234567890' # str | Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token's claims encode the tenant + workspace + scopes. Issue via ``POST /api/v1/agent-tokens``.
    query_request = flyquery_sdk.QueryRequest() # QueryRequest | 
    x_correlation_id = UUID('550e8400-e29b-41d4-a716-446655440000') # UUID | Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. (optional)
    idempotency_key = 'ingest-2026-05-23-abc123' # str | Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h. (optional)

    try:
        # Run Grounding + Generation + AST + ScopeGuard (agent-tier).
        api_response = await api_instance.validate(x_agent_token, query_request, x_correlation_id=x_correlation_id, idempotency_key=idempotency_key)
        print("The response of AgentQueryApi->validate:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentQueryApi->validate: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **x_agent_token** | **str**| Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;. | 
 **query_request** | [**QueryRequest**](QueryRequest.md)|  | 
 **x_correlation_id** | **UUID**| Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. | [optional] 
 **idempotency_key** | **str**| Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h. | [optional] 

### Return type

[**ValidateResponse**](ValidateResponse.md)

### Authorization

[AgentToken](../README.md#AgentToken)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

