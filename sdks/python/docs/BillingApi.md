# flyquery_sdk.BillingApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**rollup**](BillingApi.md#rollup) | **GET** /api/v1/billing | Aggregate LLM cost into &#x60;&#x60;day&#x60;&#x60; / &#x60;&#x60;week&#x60;&#x60; / &#x60;&#x60;month&#x60;&#x60; buckets.


# **rollup**
> BillingRollup rollup(x_tenant_id, x_workspace_id, period=period, date_from=date_from, date_to=date_to, x_correlation_id=x_correlation_id)

Aggregate LLM cost into ``day`` / ``week`` / ``month`` buckets.

Query params
------------
* ``period``    -- ``day`` (default) / ``week`` / ``month``
* ``date_from`` -- inclusive lower bound on ``created_at``
* ``date_to``   -- exclusive upper bound on ``created_at``

Response shape: :class:`BillingRollup`. Buckets with zero
cost are omitted from the breakdown (no empty days).

### Example

* Api Key Authentication (WorkspaceContext):
* Api Key Authentication (TenantContext):

```python
import flyquery_sdk
from flyquery_sdk.models.billing_rollup import BillingRollup
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
    api_instance = flyquery_sdk.BillingApi(api_client)
    x_tenant_id = 'acme-corp' # str | Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
    x_workspace_id = '00000000-0000-0000-0000-000000000001' # str | Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
    period = 'day' # str |  (optional) (default to 'day')
    date_from = 'date_from_example' # str |  (optional)
    date_to = 'date_to_example' # str |  (optional)
    x_correlation_id = UUID('550e8400-e29b-41d4-a716-446655440000') # UUID | Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. (optional)

    try:
        # Aggregate LLM cost into ``day`` / ``week`` / ``month`` buckets.
        api_response = await api_instance.rollup(x_tenant_id, x_workspace_id, period=period, date_from=date_from, date_to=date_to, x_correlation_id=x_correlation_id)
        print("The response of BillingApi->rollup:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BillingApi->rollup: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **x_tenant_id** | **str**| Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present. | 
 **x_workspace_id** | **str**| Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation. | 
 **period** | **str**|  | [optional] [default to &#39;day&#39;]
 **date_from** | **str**|  | [optional] 
 **date_to** | **str**|  | [optional] 
 **x_correlation_id** | **UUID**| Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. | [optional] 

### Return type

[**BillingRollup**](BillingRollup.md)

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

