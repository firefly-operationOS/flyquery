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
> SemanticDimensionRead create(semantic_dimension_create)

Create a new semantic dimension in DRAFT status.

### Example


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


# Enter a context with an instance of the API client
async with flyquery_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = flyquery_sdk.SemanticDimensionsApi(api_client)
    semantic_dimension_create = flyquery_sdk.SemanticDimensionCreate() # SemanticDimensionCreate | 

    try:
        # Create a new semantic dimension in DRAFT status.
        api_response = await api_instance.create(semantic_dimension_create)
        print("The response of SemanticDimensionsApi->create:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SemanticDimensionsApi->create: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **semantic_dimension_create** | [**SemanticDimensionCreate**](SemanticDimensionCreate.md)|  | 

### Return type

[**SemanticDimensionRead**](SemanticDimensionRead.md)

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

# **get_dimension**
> SemanticDimensionRead get_dimension(dimension_id)

Fetch a single semantic dimension by id.

### Example


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


# Enter a context with an instance of the API client
async with flyquery_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = flyquery_sdk.SemanticDimensionsApi(api_client)
    dimension_id = 'dimension_id_example' # str | 

    try:
        # Fetch a single semantic dimension by id.
        api_response = await api_instance.get_dimension(dimension_id)
        print("The response of SemanticDimensionsApi->get_dimension:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SemanticDimensionsApi->get_dimension: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **dimension_id** | **str**|  | 

### Return type

[**SemanticDimensionRead**](SemanticDimensionRead.md)

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

# **history**
> history(dimension_id)

Return version history for a dimension, oldest first.

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
    api_instance = flyquery_sdk.SemanticDimensionsApi(api_client)
    dimension_id = 'dimension_id_example' # str | 

    try:
        # Return version history for a dimension, oldest first.
        await api_instance.history(dimension_id)
    except Exception as e:
        print("Exception when calling SemanticDimensionsApi->history: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **dimension_id** | **str**|  | 

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

# **list_dimensions**
> list_dimensions(dataset_id=dataset_id)

List all semantic dimensions for the caller's workspace.

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
    api_instance = flyquery_sdk.SemanticDimensionsApi(api_client)
    dataset_id = 'dataset_id_example' # str |  (optional)

    try:
        # List all semantic dimensions for the caller's workspace.
        await api_instance.list_dimensions(dataset_id=dataset_id)
    except Exception as e:
        print("Exception when calling SemanticDimensionsApi->list_dimensions: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
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

# **publish**
> SemanticDimensionRead publish(dimension_id)

Validate, compile, and publish a dimension (status → PUBLISHED).

### Example


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


# Enter a context with an instance of the API client
async with flyquery_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = flyquery_sdk.SemanticDimensionsApi(api_client)
    dimension_id = 'dimension_id_example' # str | 

    try:
        # Validate, compile, and publish a dimension (status → PUBLISHED).
        api_response = await api_instance.publish(dimension_id)
        print("The response of SemanticDimensionsApi->publish:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SemanticDimensionsApi->publish: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **dimension_id** | **str**|  | 

### Return type

[**SemanticDimensionRead**](SemanticDimensionRead.md)

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

# **retire**
> SemanticDimensionRead retire(dimension_id)

Retire a dimension (status → RETIRED).

### Example


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


# Enter a context with an instance of the API client
async with flyquery_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = flyquery_sdk.SemanticDimensionsApi(api_client)
    dimension_id = 'dimension_id_example' # str | 

    try:
        # Retire a dimension (status → RETIRED).
        api_response = await api_instance.retire(dimension_id)
        print("The response of SemanticDimensionsApi->retire:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SemanticDimensionsApi->retire: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **dimension_id** | **str**|  | 

### Return type

[**SemanticDimensionRead**](SemanticDimensionRead.md)

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

# **update**
> SemanticDimensionRead update(dimension_id, semantic_dimension_update)

Sparse-update a dimension; re-validates YAML if definition changes.

### Example


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


# Enter a context with an instance of the API client
async with flyquery_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = flyquery_sdk.SemanticDimensionsApi(api_client)
    dimension_id = 'dimension_id_example' # str | 
    semantic_dimension_update = flyquery_sdk.SemanticDimensionUpdate() # SemanticDimensionUpdate | 

    try:
        # Sparse-update a dimension; re-validates YAML if definition changes.
        api_response = await api_instance.update(dimension_id, semantic_dimension_update)
        print("The response of SemanticDimensionsApi->update:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SemanticDimensionsApi->update: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **dimension_id** | **str**|  | 
 **semantic_dimension_update** | [**SemanticDimensionUpdate**](SemanticDimensionUpdate.md)|  | 

### Return type

[**SemanticDimensionRead**](SemanticDimensionRead.md)

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

