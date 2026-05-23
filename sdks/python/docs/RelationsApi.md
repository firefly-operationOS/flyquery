# flyquery_sdk.RelationsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**approve_relation**](RelationsApi.md#approve_relation) | **POST** /api/v1/relations/{relation_id}:approve | Approve a PROPOSED relation.
[**list_relations**](RelationsApi.md#list_relations) | **GET** /api/v1/datasets/{dataset_id}/relations | List relations for a dataset (all statuses by default).
[**reject_relation**](RelationsApi.md#reject_relation) | **POST** /api/v1/relations/{relation_id}:reject | Reject a PROPOSED relation.


# **approve_relation**
> approve_relation(relation_id)

Approve a PROPOSED relation.

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
    api_instance = flyquery_sdk.RelationsApi(api_client)
    relation_id = 'relation_id_example' # str | 

    try:
        # Approve a PROPOSED relation.
        await api_instance.approve_relation(relation_id)
    except Exception as e:
        print("Exception when calling RelationsApi->approve_relation: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **relation_id** | **str**|  | 

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

# **list_relations**
> list_relations(dataset_id)

List relations for a dataset (all statuses by default).

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
    api_instance = flyquery_sdk.RelationsApi(api_client)
    dataset_id = 'dataset_id_example' # str | 

    try:
        # List relations for a dataset (all statuses by default).
        await api_instance.list_relations(dataset_id)
    except Exception as e:
        print("Exception when calling RelationsApi->list_relations: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **dataset_id** | **str**|  | 

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

# **reject_relation**
> reject_relation(relation_id)

Reject a PROPOSED relation.

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
    api_instance = flyquery_sdk.RelationsApi(api_client)
    relation_id = 'relation_id_example' # str | 

    try:
        # Reject a PROPOSED relation.
        await api_instance.reject_relation(relation_id)
    except Exception as e:
        print("Exception when calling RelationsApi->reject_relation: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **relation_id** | **str**|  | 

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

