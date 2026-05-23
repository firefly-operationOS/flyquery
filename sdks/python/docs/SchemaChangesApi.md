# flyquery_sdk.SchemaChangesApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**confirm**](SchemaChangesApi.md#confirm) | **POST** /api/v1/schema-changes/{change_id}:confirm | Flip a RENAMED_CANDIDATE row to RENAMED.


# **confirm**
> SchemaChangeRead confirm(change_id)

Flip a RENAMED_CANDIDATE row to RENAMED.

Validates that the change exists and is in state RENAMED_CANDIDATE.
Sets approved_by (the current actor / tenant_id), approved_at (now),
change = 'RENAMED'.
Also updates last_changed_at on the corresponding schema_objects column row.

### Example


```python
import flyquery_sdk
from flyquery_sdk.models.schema_change_read import SchemaChangeRead
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
    api_instance = flyquery_sdk.SchemaChangesApi(api_client)
    change_id = 'change_id_example' # str | 

    try:
        # Flip a RENAMED_CANDIDATE row to RENAMED.
        api_response = await api_instance.confirm(change_id)
        print("The response of SchemaChangesApi->confirm:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SchemaChangesApi->confirm: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **change_id** | **str**|  | 

### Return type

[**SchemaChangeRead**](SchemaChangeRead.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

