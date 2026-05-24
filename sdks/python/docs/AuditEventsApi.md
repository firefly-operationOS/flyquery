# flyquery_sdk.AuditEventsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**list_events**](AuditEventsApi.md#list_events) | **GET** /api/v1/audit-events | List audit events for the caller&#39;s workspace, newest first.


# **list_events**
> PaginatedAuditEventRead list_events(x_tenant_id, x_workspace_id, event_type=event_type, actor=actor, resource_kind=resource_kind, date_from=date_from, date_to=date_to, limit=limit, offset=offset, x_correlation_id=x_correlation_id)

List audit events for the caller's workspace, newest first.

Filters
-------
* ``event_type``    -- exact match (e.g. ``dataset.created``)
* ``actor``         -- exact match
* ``resource_kind`` -- exact match (``dataset`` / ``agent_token`` / ...)
* ``date_from``     -- inclusive lower bound on ``created_at``
* ``date_to``       -- exclusive upper bound on ``created_at``

### Example

* Api Key Authentication (WorkspaceContext):
* Api Key Authentication (TenantContext):

```python
import flyquery_sdk
from flyquery_sdk.models.paginated_audit_event_read import PaginatedAuditEventRead
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
    api_instance = flyquery_sdk.AuditEventsApi(api_client)
    x_tenant_id = 'acme-corp' # str | Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
    x_workspace_id = '00000000-0000-0000-0000-000000000001' # str | Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
    event_type = 'event_type_example' # str |  (optional)
    actor = 'actor_example' # str |  (optional)
    resource_kind = 'resource_kind_example' # str |  (optional)
    date_from = 'date_from_example' # str |  (optional)
    date_to = 'date_to_example' # str |  (optional)
    limit = 100 # int |  (optional) (default to 100)
    offset = 0 # int |  (optional) (default to 0)
    x_correlation_id = UUID('550e8400-e29b-41d4-a716-446655440000') # UUID | Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. (optional)

    try:
        # List audit events for the caller's workspace, newest first.
        api_response = await api_instance.list_events(x_tenant_id, x_workspace_id, event_type=event_type, actor=actor, resource_kind=resource_kind, date_from=date_from, date_to=date_to, limit=limit, offset=offset, x_correlation_id=x_correlation_id)
        print("The response of AuditEventsApi->list_events:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuditEventsApi->list_events: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **x_tenant_id** | **str**| Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present. | 
 **x_workspace_id** | **str**| Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation. | 
 **event_type** | **str**|  | [optional] 
 **actor** | **str**|  | [optional] 
 **resource_kind** | **str**|  | [optional] 
 **date_from** | **str**|  | [optional] 
 **date_to** | **str**|  | [optional] 
 **limit** | **int**|  | [optional] [default to 100]
 **offset** | **int**|  | [optional] [default to 0]
 **x_correlation_id** | **UUID**| Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. | [optional] 

### Return type

[**PaginatedAuditEventRead**](PaginatedAuditEventRead.md)

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

