# flyquery_sdk.SemanticApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create**](SemanticApi.md#create) | **POST** /api/v1/semantic/dimensions | Create a new semantic dimension in DRAFT status.
[**create_0**](SemanticApi.md#create_0) | **POST** /api/v1/semantic/metrics | Create a new semantic metric in DRAFT status.
[**get_dimension**](SemanticApi.md#get_dimension) | **GET** /api/v1/semantic/dimensions/{dimension_id} | Fetch a single semantic dimension by id.
[**get_metric**](SemanticApi.md#get_metric) | **GET** /api/v1/semantic/metrics/{metric_id} | Fetch a single semantic metric by id.
[**history**](SemanticApi.md#history) | **GET** /api/v1/semantic/dimensions/{dimension_id}/history | Return version history for a dimension, oldest first.
[**history_0**](SemanticApi.md#history_0) | **GET** /api/v1/semantic/metrics/{metric_id}/history | Return version history for a metric, oldest first.
[**list_dimensions**](SemanticApi.md#list_dimensions) | **GET** /api/v1/semantic/dimensions | List all semantic dimensions for the caller&#39;s workspace.
[**list_metrics**](SemanticApi.md#list_metrics) | **GET** /api/v1/semantic/metrics | List all semantic metrics for the caller&#39;s workspace.
[**publish**](SemanticApi.md#publish) | **POST** /api/v1/semantic/dimensions/{dimension_id}:publish | Validate, compile, and publish a dimension (status → PUBLISHED).
[**publish_0**](SemanticApi.md#publish_0) | **POST** /api/v1/semantic/metrics/{metric_id}:publish | Validate, compile, and publish a metric (status → PUBLISHED).
[**retire**](SemanticApi.md#retire) | **POST** /api/v1/semantic/dimensions/{dimension_id}:retire | Retire a dimension (status → RETIRED).
[**retire_0**](SemanticApi.md#retire_0) | **POST** /api/v1/semantic/metrics/{metric_id}:retire | Retire a metric (status → RETIRED).
[**update**](SemanticApi.md#update) | **PUT** /api/v1/semantic/dimensions/{dimension_id} | Sparse-update a dimension; re-validates YAML if definition changes.
[**update_0**](SemanticApi.md#update_0) | **PUT** /api/v1/semantic/metrics/{metric_id} | Sparse-update a metric; re-validates YAML if definition changes.


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
    api_instance = flyquery_sdk.SemanticApi(api_client)
    semantic_dimension_create = flyquery_sdk.SemanticDimensionCreate() # SemanticDimensionCreate | 

    try:
        # Create a new semantic dimension in DRAFT status.
        api_response = await api_instance.create(semantic_dimension_create)
        print("The response of SemanticApi->create:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SemanticApi->create: %s\n" % e)
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

# **create_0**
> SemanticMetricRead create_0(semantic_metric_create)

Create a new semantic metric in DRAFT status.

### Example


```python
import flyquery_sdk
from flyquery_sdk.models.semantic_metric_create import SemanticMetricCreate
from flyquery_sdk.models.semantic_metric_read import SemanticMetricRead
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
    api_instance = flyquery_sdk.SemanticApi(api_client)
    semantic_metric_create = flyquery_sdk.SemanticMetricCreate() # SemanticMetricCreate | 

    try:
        # Create a new semantic metric in DRAFT status.
        api_response = await api_instance.create_0(semantic_metric_create)
        print("The response of SemanticApi->create_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SemanticApi->create_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **semantic_metric_create** | [**SemanticMetricCreate**](SemanticMetricCreate.md)|  | 

### Return type

[**SemanticMetricRead**](SemanticMetricRead.md)

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
    api_instance = flyquery_sdk.SemanticApi(api_client)
    dimension_id = 'dimension_id_example' # str | 

    try:
        # Fetch a single semantic dimension by id.
        api_response = await api_instance.get_dimension(dimension_id)
        print("The response of SemanticApi->get_dimension:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SemanticApi->get_dimension: %s\n" % e)
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

# **get_metric**
> SemanticMetricRead get_metric(metric_id)

Fetch a single semantic metric by id.

### Example


```python
import flyquery_sdk
from flyquery_sdk.models.semantic_metric_read import SemanticMetricRead
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
    api_instance = flyquery_sdk.SemanticApi(api_client)
    metric_id = 'metric_id_example' # str | 

    try:
        # Fetch a single semantic metric by id.
        api_response = await api_instance.get_metric(metric_id)
        print("The response of SemanticApi->get_metric:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SemanticApi->get_metric: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **metric_id** | **str**|  | 

### Return type

[**SemanticMetricRead**](SemanticMetricRead.md)

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
    api_instance = flyquery_sdk.SemanticApi(api_client)
    dimension_id = 'dimension_id_example' # str | 

    try:
        # Return version history for a dimension, oldest first.
        await api_instance.history(dimension_id)
    except Exception as e:
        print("Exception when calling SemanticApi->history: %s\n" % e)
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

# **history_0**
> history_0(metric_id)

Return version history for a metric, oldest first.

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
    api_instance = flyquery_sdk.SemanticApi(api_client)
    metric_id = 'metric_id_example' # str | 

    try:
        # Return version history for a metric, oldest first.
        await api_instance.history_0(metric_id)
    except Exception as e:
        print("Exception when calling SemanticApi->history_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **metric_id** | **str**|  | 

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
    api_instance = flyquery_sdk.SemanticApi(api_client)
    dataset_id = 'dataset_id_example' # str |  (optional)

    try:
        # List all semantic dimensions for the caller's workspace.
        await api_instance.list_dimensions(dataset_id=dataset_id)
    except Exception as e:
        print("Exception when calling SemanticApi->list_dimensions: %s\n" % e)
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

# **list_metrics**
> list_metrics(dataset_id=dataset_id)

List all semantic metrics for the caller's workspace.

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
    api_instance = flyquery_sdk.SemanticApi(api_client)
    dataset_id = 'dataset_id_example' # str |  (optional)

    try:
        # List all semantic metrics for the caller's workspace.
        await api_instance.list_metrics(dataset_id=dataset_id)
    except Exception as e:
        print("Exception when calling SemanticApi->list_metrics: %s\n" % e)
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
    api_instance = flyquery_sdk.SemanticApi(api_client)
    dimension_id = 'dimension_id_example' # str | 

    try:
        # Validate, compile, and publish a dimension (status → PUBLISHED).
        api_response = await api_instance.publish(dimension_id)
        print("The response of SemanticApi->publish:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SemanticApi->publish: %s\n" % e)
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

# **publish_0**
> SemanticMetricRead publish_0(metric_id)

Validate, compile, and publish a metric (status → PUBLISHED).

### Example


```python
import flyquery_sdk
from flyquery_sdk.models.semantic_metric_read import SemanticMetricRead
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
    api_instance = flyquery_sdk.SemanticApi(api_client)
    metric_id = 'metric_id_example' # str | 

    try:
        # Validate, compile, and publish a metric (status → PUBLISHED).
        api_response = await api_instance.publish_0(metric_id)
        print("The response of SemanticApi->publish_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SemanticApi->publish_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **metric_id** | **str**|  | 

### Return type

[**SemanticMetricRead**](SemanticMetricRead.md)

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
    api_instance = flyquery_sdk.SemanticApi(api_client)
    dimension_id = 'dimension_id_example' # str | 

    try:
        # Retire a dimension (status → RETIRED).
        api_response = await api_instance.retire(dimension_id)
        print("The response of SemanticApi->retire:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SemanticApi->retire: %s\n" % e)
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

# **retire_0**
> SemanticMetricRead retire_0(metric_id)

Retire a metric (status → RETIRED).

### Example


```python
import flyquery_sdk
from flyquery_sdk.models.semantic_metric_read import SemanticMetricRead
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
    api_instance = flyquery_sdk.SemanticApi(api_client)
    metric_id = 'metric_id_example' # str | 

    try:
        # Retire a metric (status → RETIRED).
        api_response = await api_instance.retire_0(metric_id)
        print("The response of SemanticApi->retire_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SemanticApi->retire_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **metric_id** | **str**|  | 

### Return type

[**SemanticMetricRead**](SemanticMetricRead.md)

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
    api_instance = flyquery_sdk.SemanticApi(api_client)
    dimension_id = 'dimension_id_example' # str | 
    semantic_dimension_update = flyquery_sdk.SemanticDimensionUpdate() # SemanticDimensionUpdate | 

    try:
        # Sparse-update a dimension; re-validates YAML if definition changes.
        api_response = await api_instance.update(dimension_id, semantic_dimension_update)
        print("The response of SemanticApi->update:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SemanticApi->update: %s\n" % e)
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

# **update_0**
> SemanticMetricRead update_0(metric_id, semantic_metric_update)

Sparse-update a metric; re-validates YAML if definition changes.

### Example


```python
import flyquery_sdk
from flyquery_sdk.models.semantic_metric_read import SemanticMetricRead
from flyquery_sdk.models.semantic_metric_update import SemanticMetricUpdate
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
    api_instance = flyquery_sdk.SemanticApi(api_client)
    metric_id = 'metric_id_example' # str | 
    semantic_metric_update = flyquery_sdk.SemanticMetricUpdate() # SemanticMetricUpdate | 

    try:
        # Sparse-update a metric; re-validates YAML if definition changes.
        api_response = await api_instance.update_0(metric_id, semantic_metric_update)
        print("The response of SemanticApi->update_0:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SemanticApi->update_0: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **metric_id** | **str**|  | 
 **semantic_metric_update** | [**SemanticMetricUpdate**](SemanticMetricUpdate.md)|  | 

### Return type

[**SemanticMetricRead**](SemanticMetricRead.md)

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

