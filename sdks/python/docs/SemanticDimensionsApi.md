# flyquery_sdk.SemanticDimensionsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create**](SemanticDimensionsApi.md#create) | **POST** /api/v1/semantic/dimensions | Create a new semantic dimension in DRAFT status.
[**get_dimension**](SemanticDimensionsApi.md#get_dimension) | **GET** /api/v1/semantic/dimensions/{dimension_id} | Fetch a single semantic dimension by id.
[**history**](SemanticDimensionsApi.md#history) | **GET** /api/v1/semantic/dimensions/{dimension_id}/history | Return version history for a dimension, oldest first.
[**list_dimensions**](SemanticDimensionsApi.md#list_dimensions) | **GET** /api/v1/semantic/dimensions | List all semantic dimensions for the caller&#39;s workspace.
[**publish**](SemanticDimensionsApi.md#publish) | **POST** /api/v1/semantic/dimensions/{dimension_id}:publish | Validate, compile, and publish a dimension (status → PUBLISHED).
[**retire**](SemanticDimensionsApi.md#retire) | **POST** /api/v1/semantic/dimensions/{dimension_id}:retire | Retire a dimension (status → RETIRED).
[**update**](SemanticDimensionsApi.md#update) | **PUT** /api/v1/semantic/dimensions/{dimension_id} | Sparse-update a dimension; re-validates YAML if definition changes.


# **create**
> SemanticDimensionRead create(x_tenant_id, x_workspace_id, semantic_dimension_create, x_correlation_id=x_correlation_id, idempotency_key=idempotency_key)

Create a new semantic dimension in DRAFT status.

### Example

* Api Key Authentication (WorkspaceContext):
* Api Key Authentication (TenantContext):

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

# Configure API key authorization: WorkspaceContext
configuration.api_key['WorkspaceContext'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['WorkspaceContext'] = 'Bearer'

# Configure API key authorization: TenantContext
configuration.api_key['TenantContext'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['TenantContext'] = 'Bearer'

# Enter a context with an instance of the API client
async with flyquery_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = flyquery_sdk.SemanticDimensionsApi(api_client)
    x_tenant_id = 'acme-corp' # str | Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
    x_workspace_id = '00000000-0000-0000-0000-000000000001' # str | Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
    semantic_dimension_create = flyquery_sdk.SemanticDimensionCreate() # SemanticDimensionCreate | 
    x_correlation_id = UUID('550e8400-e29b-41d4-a716-446655440000') # UUID | Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. (optional)
    idempotency_key = 'ingest-2026-05-23-abc123' # str | Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h. (optional)

    try:
        # Create a new semantic dimension in DRAFT status.
        api_response = await api_instance.create(x_tenant_id, x_workspace_id, semantic_dimension_create, x_correlation_id=x_correlation_id, idempotency_key=idempotency_key)
        print("The response of SemanticDimensionsApi->create:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SemanticDimensionsApi->create: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **x_tenant_id** | **str**| Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present. | 
 **x_workspace_id** | **str**| Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation. | 
 **semantic_dimension_create** | [**SemanticDimensionCreate**](SemanticDimensionCreate.md)|  | 
 **x_correlation_id** | **UUID**| Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. | [optional] 
 **idempotency_key** | **str**| Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h. | [optional] 

### Return type

[**SemanticDimensionRead**](SemanticDimensionRead.md)

### Authorization

[WorkspaceContext](../README.md#WorkspaceContext), [TenantContext](../README.md#TenantContext)

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
> SemanticDimensionRead get_dimension(dimension_id, x_tenant_id, x_workspace_id, x_correlation_id=x_correlation_id)

Fetch a single semantic dimension by id.

### Example

* Api Key Authentication (WorkspaceContext):
* Api Key Authentication (TenantContext):

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

# Configure API key authorization: WorkspaceContext
configuration.api_key['WorkspaceContext'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['WorkspaceContext'] = 'Bearer'

# Configure API key authorization: TenantContext
configuration.api_key['TenantContext'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['TenantContext'] = 'Bearer'

# Enter a context with an instance of the API client
async with flyquery_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = flyquery_sdk.SemanticDimensionsApi(api_client)
    dimension_id = 'dimension_id_example' # str | 
    x_tenant_id = 'acme-corp' # str | Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
    x_workspace_id = '00000000-0000-0000-0000-000000000001' # str | Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
    x_correlation_id = UUID('550e8400-e29b-41d4-a716-446655440000') # UUID | Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. (optional)

    try:
        # Fetch a single semantic dimension by id.
        api_response = await api_instance.get_dimension(dimension_id, x_tenant_id, x_workspace_id, x_correlation_id=x_correlation_id)
        print("The response of SemanticDimensionsApi->get_dimension:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SemanticDimensionsApi->get_dimension: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **dimension_id** | **str**|  | 
 **x_tenant_id** | **str**| Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present. | 
 **x_workspace_id** | **str**| Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation. | 
 **x_correlation_id** | **UUID**| Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. | [optional] 

### Return type

[**SemanticDimensionRead**](SemanticDimensionRead.md)

### Authorization

[WorkspaceContext](../README.md#WorkspaceContext), [TenantContext](../README.md#TenantContext)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **history**
> PaginatedSemanticVersionRead history(dimension_id, x_tenant_id, x_workspace_id, x_correlation_id=x_correlation_id)

Return version history for a dimension, oldest first.

### Example

* Api Key Authentication (WorkspaceContext):
* Api Key Authentication (TenantContext):

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

# Configure API key authorization: WorkspaceContext
configuration.api_key['WorkspaceContext'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['WorkspaceContext'] = 'Bearer'

# Configure API key authorization: TenantContext
configuration.api_key['TenantContext'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['TenantContext'] = 'Bearer'

# Enter a context with an instance of the API client
async with flyquery_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = flyquery_sdk.SemanticDimensionsApi(api_client)
    dimension_id = 'dimension_id_example' # str | 
    x_tenant_id = 'acme-corp' # str | Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
    x_workspace_id = '00000000-0000-0000-0000-000000000001' # str | Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
    x_correlation_id = UUID('550e8400-e29b-41d4-a716-446655440000') # UUID | Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. (optional)

    try:
        # Return version history for a dimension, oldest first.
        api_response = await api_instance.history(dimension_id, x_tenant_id, x_workspace_id, x_correlation_id=x_correlation_id)
        print("The response of SemanticDimensionsApi->history:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SemanticDimensionsApi->history: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **dimension_id** | **str**|  | 
 **x_tenant_id** | **str**| Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present. | 
 **x_workspace_id** | **str**| Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation. | 
 **x_correlation_id** | **UUID**| Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. | [optional] 

### Return type

[**PaginatedSemanticVersionRead**](PaginatedSemanticVersionRead.md)

### Authorization

[WorkspaceContext](../README.md#WorkspaceContext), [TenantContext](../README.md#TenantContext)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_dimensions**
> PaginatedSemanticDimensionRead list_dimensions(x_tenant_id, x_workspace_id, dataset_id=dataset_id, limit=limit, offset=offset, x_correlation_id=x_correlation_id)

List all semantic dimensions for the caller's workspace.

### Example

* Api Key Authentication (WorkspaceContext):
* Api Key Authentication (TenantContext):

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

# Configure API key authorization: WorkspaceContext
configuration.api_key['WorkspaceContext'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['WorkspaceContext'] = 'Bearer'

# Configure API key authorization: TenantContext
configuration.api_key['TenantContext'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['TenantContext'] = 'Bearer'

# Enter a context with an instance of the API client
async with flyquery_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = flyquery_sdk.SemanticDimensionsApi(api_client)
    x_tenant_id = 'acme-corp' # str | Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
    x_workspace_id = '00000000-0000-0000-0000-000000000001' # str | Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
    dataset_id = 'dataset_id_example' # str |  (optional)
    limit = 100 # int |  (optional) (default to 100)
    offset = 0 # int |  (optional) (default to 0)
    x_correlation_id = UUID('550e8400-e29b-41d4-a716-446655440000') # UUID | Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. (optional)

    try:
        # List all semantic dimensions for the caller's workspace.
        api_response = await api_instance.list_dimensions(x_tenant_id, x_workspace_id, dataset_id=dataset_id, limit=limit, offset=offset, x_correlation_id=x_correlation_id)
        print("The response of SemanticDimensionsApi->list_dimensions:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SemanticDimensionsApi->list_dimensions: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **x_tenant_id** | **str**| Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present. | 
 **x_workspace_id** | **str**| Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation. | 
 **dataset_id** | **str**|  | [optional] 
 **limit** | **int**|  | [optional] [default to 100]
 **offset** | **int**|  | [optional] [default to 0]
 **x_correlation_id** | **UUID**| Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. | [optional] 

### Return type

[**PaginatedSemanticDimensionRead**](PaginatedSemanticDimensionRead.md)

### Authorization

[WorkspaceContext](../README.md#WorkspaceContext), [TenantContext](../README.md#TenantContext)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **publish**
> SemanticDimensionRead publish(dimension_id, x_tenant_id, x_workspace_id, x_correlation_id=x_correlation_id, idempotency_key=idempotency_key)

Validate, compile, and publish a dimension (status → PUBLISHED).

### Example

* Api Key Authentication (WorkspaceContext):
* Api Key Authentication (TenantContext):

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

# Configure API key authorization: WorkspaceContext
configuration.api_key['WorkspaceContext'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['WorkspaceContext'] = 'Bearer'

# Configure API key authorization: TenantContext
configuration.api_key['TenantContext'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['TenantContext'] = 'Bearer'

# Enter a context with an instance of the API client
async with flyquery_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = flyquery_sdk.SemanticDimensionsApi(api_client)
    dimension_id = 'dimension_id_example' # str | 
    x_tenant_id = 'acme-corp' # str | Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
    x_workspace_id = '00000000-0000-0000-0000-000000000001' # str | Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
    x_correlation_id = UUID('550e8400-e29b-41d4-a716-446655440000') # UUID | Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. (optional)
    idempotency_key = 'ingest-2026-05-23-abc123' # str | Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h. (optional)

    try:
        # Validate, compile, and publish a dimension (status → PUBLISHED).
        api_response = await api_instance.publish(dimension_id, x_tenant_id, x_workspace_id, x_correlation_id=x_correlation_id, idempotency_key=idempotency_key)
        print("The response of SemanticDimensionsApi->publish:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SemanticDimensionsApi->publish: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **dimension_id** | **str**|  | 
 **x_tenant_id** | **str**| Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present. | 
 **x_workspace_id** | **str**| Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation. | 
 **x_correlation_id** | **UUID**| Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. | [optional] 
 **idempotency_key** | **str**| Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h. | [optional] 

### Return type

[**SemanticDimensionRead**](SemanticDimensionRead.md)

### Authorization

[WorkspaceContext](../README.md#WorkspaceContext), [TenantContext](../README.md#TenantContext)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **retire**
> SemanticDimensionRead retire(dimension_id, x_tenant_id, x_workspace_id, x_correlation_id=x_correlation_id, idempotency_key=idempotency_key)

Retire a dimension (status → RETIRED).

### Example

* Api Key Authentication (WorkspaceContext):
* Api Key Authentication (TenantContext):

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

# Configure API key authorization: WorkspaceContext
configuration.api_key['WorkspaceContext'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['WorkspaceContext'] = 'Bearer'

# Configure API key authorization: TenantContext
configuration.api_key['TenantContext'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['TenantContext'] = 'Bearer'

# Enter a context with an instance of the API client
async with flyquery_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = flyquery_sdk.SemanticDimensionsApi(api_client)
    dimension_id = 'dimension_id_example' # str | 
    x_tenant_id = 'acme-corp' # str | Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
    x_workspace_id = '00000000-0000-0000-0000-000000000001' # str | Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
    x_correlation_id = UUID('550e8400-e29b-41d4-a716-446655440000') # UUID | Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. (optional)
    idempotency_key = 'ingest-2026-05-23-abc123' # str | Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h. (optional)

    try:
        # Retire a dimension (status → RETIRED).
        api_response = await api_instance.retire(dimension_id, x_tenant_id, x_workspace_id, x_correlation_id=x_correlation_id, idempotency_key=idempotency_key)
        print("The response of SemanticDimensionsApi->retire:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SemanticDimensionsApi->retire: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **dimension_id** | **str**|  | 
 **x_tenant_id** | **str**| Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present. | 
 **x_workspace_id** | **str**| Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation. | 
 **x_correlation_id** | **UUID**| Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. | [optional] 
 **idempotency_key** | **str**| Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h. | [optional] 

### Return type

[**SemanticDimensionRead**](SemanticDimensionRead.md)

### Authorization

[WorkspaceContext](../README.md#WorkspaceContext), [TenantContext](../README.md#TenantContext)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update**
> SemanticDimensionRead update(dimension_id, x_tenant_id, x_workspace_id, semantic_dimension_update, x_correlation_id=x_correlation_id, idempotency_key=idempotency_key)

Sparse-update a dimension; re-validates YAML if definition changes.

### Example

* Api Key Authentication (WorkspaceContext):
* Api Key Authentication (TenantContext):

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

# Configure API key authorization: WorkspaceContext
configuration.api_key['WorkspaceContext'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['WorkspaceContext'] = 'Bearer'

# Configure API key authorization: TenantContext
configuration.api_key['TenantContext'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['TenantContext'] = 'Bearer'

# Enter a context with an instance of the API client
async with flyquery_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = flyquery_sdk.SemanticDimensionsApi(api_client)
    dimension_id = 'dimension_id_example' # str | 
    x_tenant_id = 'acme-corp' # str | Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
    x_workspace_id = '00000000-0000-0000-0000-000000000001' # str | Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
    semantic_dimension_update = flyquery_sdk.SemanticDimensionUpdate() # SemanticDimensionUpdate | 
    x_correlation_id = UUID('550e8400-e29b-41d4-a716-446655440000') # UUID | Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. (optional)
    idempotency_key = 'ingest-2026-05-23-abc123' # str | Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h. (optional)

    try:
        # Sparse-update a dimension; re-validates YAML if definition changes.
        api_response = await api_instance.update(dimension_id, x_tenant_id, x_workspace_id, semantic_dimension_update, x_correlation_id=x_correlation_id, idempotency_key=idempotency_key)
        print("The response of SemanticDimensionsApi->update:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SemanticDimensionsApi->update: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **dimension_id** | **str**|  | 
 **x_tenant_id** | **str**| Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present. | 
 **x_workspace_id** | **str**| Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation. | 
 **semantic_dimension_update** | [**SemanticDimensionUpdate**](SemanticDimensionUpdate.md)|  | 
 **x_correlation_id** | **UUID**| Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. | [optional] 
 **idempotency_key** | **str**| Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h. | [optional] 

### Return type

[**SemanticDimensionRead**](SemanticDimensionRead.md)

### Authorization

[WorkspaceContext](../README.md#WorkspaceContext), [TenantContext](../README.md#TenantContext)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

