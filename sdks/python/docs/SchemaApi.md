# flyquery_sdk.SchemaApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**confirm**](SchemaApi.md#confirm) | **POST** /api/v1/schema-changes/{change_id}:confirm | Flip a RENAMED_CANDIDATE row to RENAMED.
[**get_object**](SchemaApi.md#get_object) | **GET** /api/v1/schema-objects/{object_id} | Get a single schema object by ID.
[**update_object**](SchemaApi.md#update_object) | **PUT** /api/v1/schema-objects/{object_id} | Update human-set fields on a schema object.


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
    api_instance = flyquery_sdk.SchemaApi(api_client)
    change_id = 'change_id_example' # str | 

    try:
        # Flip a RENAMED_CANDIDATE row to RENAMED.
        api_response = await api_instance.confirm(change_id)
        print("The response of SchemaApi->confirm:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SchemaApi->confirm: %s\n" % e)
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

# **get_object**
> SchemaObjectRead get_object(object_id)

Get a single schema object by ID.

### Example


```python
import flyquery_sdk
from flyquery_sdk.models.schema_object_read import SchemaObjectRead
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
    api_instance = flyquery_sdk.SchemaApi(api_client)
    object_id = 'object_id_example' # str | 

    try:
        # Get a single schema object by ID.
        api_response = await api_instance.get_object(object_id)
        print("The response of SchemaApi->get_object:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SchemaApi->get_object: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **object_id** | **str**|  | 

### Return type

[**SchemaObjectRead**](SchemaObjectRead.md)

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

# **update_object**
> SchemaObjectRead update_object(object_id, schema_object_update)

Update human-set fields on a schema object.

Sets description_source='HUMAN' when description is provided.
Sets pii_source='HUMAN' when pii_tag is provided.

### Example


```python
import flyquery_sdk
from flyquery_sdk.models.schema_object_read import SchemaObjectRead
from flyquery_sdk.models.schema_object_update import SchemaObjectUpdate
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
    api_instance = flyquery_sdk.SchemaApi(api_client)
    object_id = 'object_id_example' # str | 
    schema_object_update = flyquery_sdk.SchemaObjectUpdate() # SchemaObjectUpdate | 

    try:
        # Update human-set fields on a schema object.
        api_response = await api_instance.update_object(object_id, schema_object_update)
        print("The response of SchemaApi->update_object:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SchemaApi->update_object: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **object_id** | **str**|  | 
 **schema_object_update** | [**SchemaObjectUpdate**](SchemaObjectUpdate.md)|  | 

### Return type

[**SchemaObjectRead**](SchemaObjectRead.md)

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

