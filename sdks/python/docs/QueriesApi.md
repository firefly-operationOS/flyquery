# flyquery_sdk.QueriesApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_query**](QueriesApi.md#get_query) | **GET** /api/v1/queries/{query_id} | Fetch a single query with every candidate, retry, and model id.
[**get_query_result**](QueriesApi.md#get_query_result) | **GET** /api/v1/queries/{query_id}/result | Re-download a previously-executed query&#39;s preview + parquet.
[**list_queries**](QueriesApi.md#list_queries) | **GET** /api/v1/queries | List queries for the caller&#39;s workspace, newest first.


# **get_query**
> QueryDetailRead get_query(query_id, x_tenant_id, x_workspace_id, x_correlation_id=x_correlation_id)

Fetch a single query with every candidate, retry, and model id.

Returns 404 if the query doesn't belong to the caller's
``(tenant, workspace)`` -- not just "not found", but also
"exists but wrong tenant" (cross-tenant probing is the same
404 as missing).

### Example

* Api Key Authentication (WorkspaceContext):
* Api Key Authentication (TenantContext):

```python
import flyquery_sdk
from flyquery_sdk.models.query_detail_read import QueryDetailRead
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
    api_instance = flyquery_sdk.QueriesApi(api_client)
    query_id = 'query_id_example' # str | 
    x_tenant_id = 'acme-corp' # str | Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
    x_workspace_id = '00000000-0000-0000-0000-000000000001' # str | Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
    x_correlation_id = UUID('550e8400-e29b-41d4-a716-446655440000') # UUID | Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. (optional)

    try:
        # Fetch a single query with every candidate, retry, and model id.
        api_response = await api_instance.get_query(query_id, x_tenant_id, x_workspace_id, x_correlation_id=x_correlation_id)
        print("The response of QueriesApi->get_query:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling QueriesApi->get_query: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **query_id** | **str**|  | 
 **x_tenant_id** | **str**| Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present. | 
 **x_workspace_id** | **str**| Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation. | 
 **x_correlation_id** | **UUID**| Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. | [optional] 

### Return type

[**QueryDetailRead**](QueryDetailRead.md)

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

# **get_query_result**
> QueryResultRead get_query_result(query_id, x_tenant_id, x_workspace_id, x_correlation_id=x_correlation_id)

Re-download a previously-executed query's preview + parquet.

The preview is always inlined. The presigned Parquet URL is
``None`` when the TTL has elapsed (default 24h) -- consumers
must rerun the query in that case. The presign TTL itself is
bounded by ``object_store_presign_ttl_s`` (default 24h).

Returns 404 if either the query OR its result row doesn't
exist for this tenant.

### Example

* Api Key Authentication (WorkspaceContext):
* Api Key Authentication (TenantContext):

```python
import flyquery_sdk
from flyquery_sdk.models.query_result_read import QueryResultRead
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
    api_instance = flyquery_sdk.QueriesApi(api_client)
    query_id = 'query_id_example' # str | 
    x_tenant_id = 'acme-corp' # str | Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
    x_workspace_id = '00000000-0000-0000-0000-000000000001' # str | Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
    x_correlation_id = UUID('550e8400-e29b-41d4-a716-446655440000') # UUID | Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. (optional)

    try:
        # Re-download a previously-executed query's preview + parquet.
        api_response = await api_instance.get_query_result(query_id, x_tenant_id, x_workspace_id, x_correlation_id=x_correlation_id)
        print("The response of QueriesApi->get_query_result:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling QueriesApi->get_query_result: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **query_id** | **str**|  | 
 **x_tenant_id** | **str**| Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present. | 
 **x_workspace_id** | **str**| Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation. | 
 **x_correlation_id** | **UUID**| Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. | [optional] 

### Return type

[**QueryResultRead**](QueryResultRead.md)

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

# **list_queries**
> PaginatedQueryHistoryItem list_queries(x_tenant_id, x_workspace_id, dataset_id=dataset_id, execution_status=execution_status, semantic_path_taken=semantic_path_taken, date_from=date_from, date_to=date_to, limit=limit, offset=offset, x_correlation_id=x_correlation_id)

List queries for the caller's workspace, newest first.

Filters
-------
* ``dataset_id``           -- restrict to one dataset
* ``execution_status``     -- ``OK`` / ``REJECTED_BY_FIREWALL`` / ``FAILED`` / ...
* ``semantic_path_taken``  -- e.g. ``"sql"`` vs ``"semantic-layer"``
* ``date_from``            -- inclusive lower bound on ``created_at``
* ``date_to``              -- exclusive upper bound on ``created_at``

Page size is clamped to ``[1, 200]``. Each item is the compact
history shape (no heavy JSONB columns). Use
``GET /queries/{id}`` for the full row.

### Example

* Api Key Authentication (WorkspaceContext):
* Api Key Authentication (TenantContext):

```python
import flyquery_sdk
from flyquery_sdk.models.paginated_query_history_item import PaginatedQueryHistoryItem
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
    api_instance = flyquery_sdk.QueriesApi(api_client)
    x_tenant_id = 'acme-corp' # str | Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
    x_workspace_id = '00000000-0000-0000-0000-000000000001' # str | Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
    dataset_id = 'dataset_id_example' # str |  (optional)
    execution_status = 'execution_status_example' # str |  (optional)
    semantic_path_taken = 'semantic_path_taken_example' # str |  (optional)
    date_from = 'date_from_example' # str |  (optional)
    date_to = 'date_to_example' # str |  (optional)
    limit = 50 # int |  (optional) (default to 50)
    offset = 0 # int |  (optional) (default to 0)
    x_correlation_id = UUID('550e8400-e29b-41d4-a716-446655440000') # UUID | Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. (optional)

    try:
        # List queries for the caller's workspace, newest first.
        api_response = await api_instance.list_queries(x_tenant_id, x_workspace_id, dataset_id=dataset_id, execution_status=execution_status, semantic_path_taken=semantic_path_taken, date_from=date_from, date_to=date_to, limit=limit, offset=offset, x_correlation_id=x_correlation_id)
        print("The response of QueriesApi->list_queries:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling QueriesApi->list_queries: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **x_tenant_id** | **str**| Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present. | 
 **x_workspace_id** | **str**| Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation. | 
 **dataset_id** | **str**|  | [optional] 
 **execution_status** | **str**|  | [optional] 
 **semantic_path_taken** | **str**|  | [optional] 
 **date_from** | **str**|  | [optional] 
 **date_to** | **str**|  | [optional] 
 **limit** | **int**|  | [optional] [default to 50]
 **offset** | **int**|  | [optional] [default to 0]
 **x_correlation_id** | **UUID**| Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. | [optional] 

### Return type

[**PaginatedQueryHistoryItem**](PaginatedQueryHistoryItem.md)

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

