# flyquery_sdk.ExamplesApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**approve**](ExamplesApi.md#approve) | **POST** /api/v1/examples/{example_id}:approve | Approve an example (quality → APPROVED).
[**create**](ExamplesApi.md#create) | **POST** /api/v1/examples | Create an example; defaults to source&#x3D;USER_CURATED, quality&#x3D;PROPOSED.
[**list_examples**](ExamplesApi.md#list_examples) | **GET** /api/v1/examples | List examples for the caller&#39;s workspace, with optional filters.
[**reject**](ExamplesApi.md#reject) | **POST** /api/v1/examples/{example_id}:reject | Reject an example (quality → REJECTED).


# **approve**
> ExampleRead approve(example_id)

Approve an example (quality → APPROVED).

### Example


```python
import flyquery_sdk
from flyquery_sdk.models.example_read import ExampleRead
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
    api_instance = flyquery_sdk.ExamplesApi(api_client)
    example_id = 'example_id_example' # str | 

    try:
        # Approve an example (quality → APPROVED).
        api_response = await api_instance.approve(example_id)
        print("The response of ExamplesApi->approve:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExamplesApi->approve: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **example_id** | **str**|  | 

### Return type

[**ExampleRead**](ExampleRead.md)

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

# **create**
> ExampleRead create(example_create)

Create an example; defaults to source=USER_CURATED, quality=PROPOSED.

### Example


```python
import flyquery_sdk
from flyquery_sdk.models.example_create import ExampleCreate
from flyquery_sdk.models.example_read import ExampleRead
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
    api_instance = flyquery_sdk.ExamplesApi(api_client)
    example_create = flyquery_sdk.ExampleCreate() # ExampleCreate | 

    try:
        # Create an example; defaults to source=USER_CURATED, quality=PROPOSED.
        api_response = await api_instance.create(example_create)
        print("The response of ExamplesApi->create:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExamplesApi->create: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **example_create** | [**ExampleCreate**](ExampleCreate.md)|  | 

### Return type

[**ExampleRead**](ExampleRead.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_examples**
> list_examples(quality=quality, dataset_id=dataset_id)

List examples for the caller's workspace, with optional filters.

### Example


```python
import flyquery_sdk
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
    api_instance = flyquery_sdk.ExamplesApi(api_client)
    quality = 'quality_example' # str |  (optional)
    dataset_id = 'dataset_id_example' # str |  (optional)

    try:
        # List examples for the caller's workspace, with optional filters.
        await api_instance.list_examples(quality=quality, dataset_id=dataset_id)
    except Exception as e:
        print("Exception when calling ExamplesApi->list_examples: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **quality** | **str**|  | [optional] 
 **dataset_id** | **str**|  | [optional] 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **reject**
> ExampleRead reject(example_id)

Reject an example (quality → REJECTED).

### Example


```python
import flyquery_sdk
from flyquery_sdk.models.example_read import ExampleRead
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
    api_instance = flyquery_sdk.ExamplesApi(api_client)
    example_id = 'example_id_example' # str | 

    try:
        # Reject an example (quality → REJECTED).
        api_response = await api_instance.reject(example_id)
        print("The response of ExamplesApi->reject:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExamplesApi->reject: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **example_id** | **str**|  | 

### Return type

[**ExampleRead**](ExampleRead.md)

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

