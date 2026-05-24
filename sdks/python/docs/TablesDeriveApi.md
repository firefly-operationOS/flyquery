# flyquery_sdk.TablesDeriveApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**derive**](TablesDeriveApi.md#derive) | **POST** /api/v1/tables:derive | Materialise a SELECT result as a new DERIVED table.


# **derive**
> DeriveTableResponse derive(x_tenant_id, x_workspace_id, derive_table_request, x_correlation_id=x_correlation_id, idempotency_key=idempotency_key)

Materialise a SELECT result as a new DERIVED table.

:param http_request: Starlette request (tenant context headers)
:param body: dataset_id + name + sql (must be a SELECT)
:return: DeriveTableResponse with the new table_id
:raises DeriveTableForbidden: when sql is not a SELECT
:raises DeriveTableError: when DuckDB execution fails

### Example

* Api Key Authentication (WorkspaceContext):
* Api Key Authentication (TenantContext):

```python
import flyquery_sdk
from flyquery_sdk.models.derive_table_request import DeriveTableRequest
from flyquery_sdk.models.derive_table_response import DeriveTableResponse
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
    api_instance = flyquery_sdk.TablesDeriveApi(api_client)
    x_tenant_id = 'acme-corp' # str | Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
    x_workspace_id = '00000000-0000-0000-0000-000000000001' # str | Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
    derive_table_request = flyquery_sdk.DeriveTableRequest() # DeriveTableRequest | 
    x_correlation_id = UUID('550e8400-e29b-41d4-a716-446655440000') # UUID | Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. (optional)
    idempotency_key = 'ingest-2026-05-23-abc123' # str | Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h. (optional)

    try:
        # Materialise a SELECT result as a new DERIVED table.
        api_response = await api_instance.derive(x_tenant_id, x_workspace_id, derive_table_request, x_correlation_id=x_correlation_id, idempotency_key=idempotency_key)
        print("The response of TablesDeriveApi->derive:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TablesDeriveApi->derive: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **x_tenant_id** | **str**| Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present. | 
 **x_workspace_id** | **str**| Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation. | 
 **derive_table_request** | [**DeriveTableRequest**](DeriveTableRequest.md)|  | 
 **x_correlation_id** | **UUID**| Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. | [optional] 
 **idempotency_key** | **str**| Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h. | [optional] 

### Return type

[**DeriveTableResponse**](DeriveTableResponse.md)

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

