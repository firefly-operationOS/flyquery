# flyquery_sdk.AgentSemanticDimensionsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create**](AgentSemanticDimensionsApi.md#create) | **POST** /api/v1/agent/semantic/dimensions | Create a dimension in DRAFT (agent-tier).
[**get_dimension**](AgentSemanticDimensionsApi.md#get_dimension) | **GET** /api/v1/agent/semantic/dimensions/{dimension_id} | Fetch a single dimension (agent-tier).
[**history**](AgentSemanticDimensionsApi.md#history) | **GET** /api/v1/agent/semantic/dimensions/{dimension_id}/history | Return version history for a dimension (agent-tier).
[**list_dimensions**](AgentSemanticDimensionsApi.md#list_dimensions) | **GET** /api/v1/agent/semantic/dimensions | List dimensions for the caller&#39;s workspace (agent-tier).
[**publish**](AgentSemanticDimensionsApi.md#publish) | **POST** /api/v1/agent/semantic/dimensions/{dimension_id}:publish | Publish a dimension (agent-tier).
[**retire**](AgentSemanticDimensionsApi.md#retire) | **POST** /api/v1/agent/semantic/dimensions/{dimension_id}:retire | Retire a dimension (agent-tier).
[**update**](AgentSemanticDimensionsApi.md#update) | **PUT** /api/v1/agent/semantic/dimensions/{dimension_id} | Sparse-update a dimension (agent-tier).


# **create**
> SemanticDimensionRead create(x_agent_token, semantic_dimension_create, x_correlation_id=x_correlation_id, idempotency_key=idempotency_key)

Create a dimension in DRAFT (agent-tier).

### Example

* Api Key Authentication (AgentToken):

```python
import flyquery_sdk
from flyquery_sdk.models.semantic_dimension_create import SemanticDimensionCreate
from flyquery_sdk.models.semantic_dimension_read import SemanticDimensionRead
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
    api_instance = flyquery_sdk.AgentSemanticDimensionsApi(api_client)
    x_agent_token = 'fqt_live_aBcDeF1234567890aBcDeF1234567890' # str | Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token's claims encode the tenant + workspace + scopes. Issue via ``POST /api/v1/agent-tokens``.
    semantic_dimension_create = flyquery_sdk.SemanticDimensionCreate() # SemanticDimensionCreate | 
    x_correlation_id = UUID('550e8400-e29b-41d4-a716-446655440000') # UUID | Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. (optional)
    idempotency_key = 'ingest-2026-05-23-abc123' # str | Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h. (optional)

    try:
        # Create a dimension in DRAFT (agent-tier).
        api_response = await api_instance.create(x_agent_token, semantic_dimension_create, x_correlation_id=x_correlation_id, idempotency_key=idempotency_key)
        print("The response of AgentSemanticDimensionsApi->create:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentSemanticDimensionsApi->create: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **x_agent_token** | **str**| Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;. | 
 **semantic_dimension_create** | [**SemanticDimensionCreate**](SemanticDimensionCreate.md)|  | 
 **x_correlation_id** | **UUID**| Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. | [optional] 
 **idempotency_key** | **str**| Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h. | [optional] 

### Return type

[**SemanticDimensionRead**](SemanticDimensionRead.md)

### Authorization

[AgentToken](../README.md#AgentToken)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_dimension**
> SemanticDimensionRead get_dimension(dimension_id, x_agent_token, x_correlation_id=x_correlation_id)

Fetch a single dimension (agent-tier).

### Example

* Api Key Authentication (AgentToken):

```python
import flyquery_sdk
from flyquery_sdk.models.semantic_dimension_read import SemanticDimensionRead
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
    api_instance = flyquery_sdk.AgentSemanticDimensionsApi(api_client)
    dimension_id = 'dimension_id_example' # str | 
    x_agent_token = 'fqt_live_aBcDeF1234567890aBcDeF1234567890' # str | Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token's claims encode the tenant + workspace + scopes. Issue via ``POST /api/v1/agent-tokens``.
    x_correlation_id = UUID('550e8400-e29b-41d4-a716-446655440000') # UUID | Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. (optional)

    try:
        # Fetch a single dimension (agent-tier).
        api_response = await api_instance.get_dimension(dimension_id, x_agent_token, x_correlation_id=x_correlation_id)
        print("The response of AgentSemanticDimensionsApi->get_dimension:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentSemanticDimensionsApi->get_dimension: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **dimension_id** | **str**|  | 
 **x_agent_token** | **str**| Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;. | 
 **x_correlation_id** | **UUID**| Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. | [optional] 

### Return type

[**SemanticDimensionRead**](SemanticDimensionRead.md)

### Authorization

[AgentToken](../README.md#AgentToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **history**
> PaginatedSemanticVersionRead history(dimension_id, x_agent_token, x_correlation_id=x_correlation_id)

Return version history for a dimension (agent-tier).

### Example

* Api Key Authentication (AgentToken):

```python
import flyquery_sdk
from flyquery_sdk.models.paginated_semantic_version_read import PaginatedSemanticVersionRead
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
    api_instance = flyquery_sdk.AgentSemanticDimensionsApi(api_client)
    dimension_id = 'dimension_id_example' # str | 
    x_agent_token = 'fqt_live_aBcDeF1234567890aBcDeF1234567890' # str | Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token's claims encode the tenant + workspace + scopes. Issue via ``POST /api/v1/agent-tokens``.
    x_correlation_id = UUID('550e8400-e29b-41d4-a716-446655440000') # UUID | Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. (optional)

    try:
        # Return version history for a dimension (agent-tier).
        api_response = await api_instance.history(dimension_id, x_agent_token, x_correlation_id=x_correlation_id)
        print("The response of AgentSemanticDimensionsApi->history:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentSemanticDimensionsApi->history: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **dimension_id** | **str**|  | 
 **x_agent_token** | **str**| Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;. | 
 **x_correlation_id** | **UUID**| Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. | [optional] 

### Return type

[**PaginatedSemanticVersionRead**](PaginatedSemanticVersionRead.md)

### Authorization

[AgentToken](../README.md#AgentToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_dimensions**
> PaginatedSemanticDimensionRead list_dimensions(x_agent_token, dataset_id=dataset_id, status=status, limit=limit, offset=offset, x_correlation_id=x_correlation_id)

List dimensions for the caller's workspace (agent-tier).

### Example

* Api Key Authentication (AgentToken):

```python
import flyquery_sdk
from flyquery_sdk.models.paginated_semantic_dimension_read import PaginatedSemanticDimensionRead
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
    api_instance = flyquery_sdk.AgentSemanticDimensionsApi(api_client)
    x_agent_token = 'fqt_live_aBcDeF1234567890aBcDeF1234567890' # str | Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token's claims encode the tenant + workspace + scopes. Issue via ``POST /api/v1/agent-tokens``.
    dataset_id = 'dataset_id_example' # str |  (optional)
    status = 'status_example' # str |  (optional)
    limit = 100 # int |  (optional) (default to 100)
    offset = 0 # int |  (optional) (default to 0)
    x_correlation_id = UUID('550e8400-e29b-41d4-a716-446655440000') # UUID | Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. (optional)

    try:
        # List dimensions for the caller's workspace (agent-tier).
        api_response = await api_instance.list_dimensions(x_agent_token, dataset_id=dataset_id, status=status, limit=limit, offset=offset, x_correlation_id=x_correlation_id)
        print("The response of AgentSemanticDimensionsApi->list_dimensions:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentSemanticDimensionsApi->list_dimensions: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **x_agent_token** | **str**| Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;. | 
 **dataset_id** | **str**|  | [optional] 
 **status** | **str**|  | [optional] 
 **limit** | **int**|  | [optional] [default to 100]
 **offset** | **int**|  | [optional] [default to 0]
 **x_correlation_id** | **UUID**| Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. | [optional] 

### Return type

[**PaginatedSemanticDimensionRead**](PaginatedSemanticDimensionRead.md)

### Authorization

[AgentToken](../README.md#AgentToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **publish**
> SemanticDimensionRead publish(dimension_id, x_agent_token, x_correlation_id=x_correlation_id, idempotency_key=idempotency_key)

Publish a dimension (agent-tier).

### Example

* Api Key Authentication (AgentToken):

```python
import flyquery_sdk
from flyquery_sdk.models.semantic_dimension_read import SemanticDimensionRead
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
    api_instance = flyquery_sdk.AgentSemanticDimensionsApi(api_client)
    dimension_id = 'dimension_id_example' # str | 
    x_agent_token = 'fqt_live_aBcDeF1234567890aBcDeF1234567890' # str | Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token's claims encode the tenant + workspace + scopes. Issue via ``POST /api/v1/agent-tokens``.
    x_correlation_id = UUID('550e8400-e29b-41d4-a716-446655440000') # UUID | Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. (optional)
    idempotency_key = 'ingest-2026-05-23-abc123' # str | Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h. (optional)

    try:
        # Publish a dimension (agent-tier).
        api_response = await api_instance.publish(dimension_id, x_agent_token, x_correlation_id=x_correlation_id, idempotency_key=idempotency_key)
        print("The response of AgentSemanticDimensionsApi->publish:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentSemanticDimensionsApi->publish: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **dimension_id** | **str**|  | 
 **x_agent_token** | **str**| Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;. | 
 **x_correlation_id** | **UUID**| Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. | [optional] 
 **idempotency_key** | **str**| Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h. | [optional] 

### Return type

[**SemanticDimensionRead**](SemanticDimensionRead.md)

### Authorization

[AgentToken](../README.md#AgentToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **retire**
> SemanticDimensionRead retire(dimension_id, x_agent_token, x_correlation_id=x_correlation_id, idempotency_key=idempotency_key)

Retire a dimension (agent-tier).

### Example

* Api Key Authentication (AgentToken):

```python
import flyquery_sdk
from flyquery_sdk.models.semantic_dimension_read import SemanticDimensionRead
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
    api_instance = flyquery_sdk.AgentSemanticDimensionsApi(api_client)
    dimension_id = 'dimension_id_example' # str | 
    x_agent_token = 'fqt_live_aBcDeF1234567890aBcDeF1234567890' # str | Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token's claims encode the tenant + workspace + scopes. Issue via ``POST /api/v1/agent-tokens``.
    x_correlation_id = UUID('550e8400-e29b-41d4-a716-446655440000') # UUID | Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. (optional)
    idempotency_key = 'ingest-2026-05-23-abc123' # str | Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h. (optional)

    try:
        # Retire a dimension (agent-tier).
        api_response = await api_instance.retire(dimension_id, x_agent_token, x_correlation_id=x_correlation_id, idempotency_key=idempotency_key)
        print("The response of AgentSemanticDimensionsApi->retire:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentSemanticDimensionsApi->retire: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **dimension_id** | **str**|  | 
 **x_agent_token** | **str**| Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;. | 
 **x_correlation_id** | **UUID**| Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. | [optional] 
 **idempotency_key** | **str**| Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h. | [optional] 

### Return type

[**SemanticDimensionRead**](SemanticDimensionRead.md)

### Authorization

[AgentToken](../README.md#AgentToken)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update**
> SemanticDimensionRead update(dimension_id, x_agent_token, semantic_dimension_update, x_correlation_id=x_correlation_id, idempotency_key=idempotency_key)

Sparse-update a dimension (agent-tier).

### Example

* Api Key Authentication (AgentToken):

```python
import flyquery_sdk
from flyquery_sdk.models.semantic_dimension_read import SemanticDimensionRead
from flyquery_sdk.models.semantic_dimension_update import SemanticDimensionUpdate
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
    api_instance = flyquery_sdk.AgentSemanticDimensionsApi(api_client)
    dimension_id = 'dimension_id_example' # str | 
    x_agent_token = 'fqt_live_aBcDeF1234567890aBcDeF1234567890' # str | Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token's claims encode the tenant + workspace + scopes. Issue via ``POST /api/v1/agent-tokens``.
    semantic_dimension_update = flyquery_sdk.SemanticDimensionUpdate() # SemanticDimensionUpdate | 
    x_correlation_id = UUID('550e8400-e29b-41d4-a716-446655440000') # UUID | Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. (optional)
    idempotency_key = 'ingest-2026-05-23-abc123' # str | Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h. (optional)

    try:
        # Sparse-update a dimension (agent-tier).
        api_response = await api_instance.update(dimension_id, x_agent_token, semantic_dimension_update, x_correlation_id=x_correlation_id, idempotency_key=idempotency_key)
        print("The response of AgentSemanticDimensionsApi->update:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentSemanticDimensionsApi->update: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **dimension_id** | **str**|  | 
 **x_agent_token** | **str**| Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;. | 
 **semantic_dimension_update** | [**SemanticDimensionUpdate**](SemanticDimensionUpdate.md)|  | 
 **x_correlation_id** | **UUID**| Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. | [optional] 
 **idempotency_key** | **str**| Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h. | [optional] 

### Return type

[**SemanticDimensionRead**](SemanticDimensionRead.md)

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

