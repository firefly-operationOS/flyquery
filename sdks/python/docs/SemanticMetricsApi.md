# flyquery_sdk.SemanticMetricsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create**](SemanticMetricsApi.md#create) | **POST** /api/v1/semantic/metrics | Create a new semantic metric in DRAFT status.
[**get_metric**](SemanticMetricsApi.md#get_metric) | **GET** /api/v1/semantic/metrics/{metric_id} | Fetch a single semantic metric by id.
[**history**](SemanticMetricsApi.md#history) | **GET** /api/v1/semantic/metrics/{metric_id}/history | Return version history for a metric, oldest first.
[**list_metrics**](SemanticMetricsApi.md#list_metrics) | **GET** /api/v1/semantic/metrics | List all semantic metrics for the caller&#39;s workspace.
[**publish**](SemanticMetricsApi.md#publish) | **POST** /api/v1/semantic/metrics/{metric_id}:publish | Validate, compile, and publish a metric (status → PUBLISHED).
[**retire**](SemanticMetricsApi.md#retire) | **POST** /api/v1/semantic/metrics/{metric_id}:retire | Retire a metric (status → RETIRED).
[**update**](SemanticMetricsApi.md#update) | **PUT** /api/v1/semantic/metrics/{metric_id} | Sparse-update a metric; re-validates YAML if definition changes.


# **create**
> SemanticMetricRead create(semantic_metric_create)

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
    api_instance = flyquery_sdk.SemanticMetricsApi(api_client)
    semantic_metric_create = flyquery_sdk.SemanticMetricCreate() # SemanticMetricCreate | 

    try:
        # Create a new semantic metric in DRAFT status.
        api_response = await api_instance.create(semantic_metric_create)
        print("The response of SemanticMetricsApi->create:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SemanticMetricsApi->create: %s\n" % e)
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
    api_instance = flyquery_sdk.SemanticMetricsApi(api_client)
    metric_id = 'metric_id_example' # str | 

    try:
        # Fetch a single semantic metric by id.
        api_response = await api_instance.get_metric(metric_id)
        print("The response of SemanticMetricsApi->get_metric:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SemanticMetricsApi->get_metric: %s\n" % e)
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
> history(metric_id)

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
    api_instance = flyquery_sdk.SemanticMetricsApi(api_client)
    metric_id = 'metric_id_example' # str | 

    try:
        # Return version history for a metric, oldest first.
        await api_instance.history(metric_id)
    except Exception as e:
        print("Exception when calling SemanticMetricsApi->history: %s\n" % e)
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
    api_instance = flyquery_sdk.SemanticMetricsApi(api_client)
    dataset_id = 'dataset_id_example' # str |  (optional)

    try:
        # List all semantic metrics for the caller's workspace.
        await api_instance.list_metrics(dataset_id=dataset_id)
    except Exception as e:
        print("Exception when calling SemanticMetricsApi->list_metrics: %s\n" % e)
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
> SemanticMetricRead publish(metric_id)

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
    api_instance = flyquery_sdk.SemanticMetricsApi(api_client)
    metric_id = 'metric_id_example' # str | 

    try:
        # Validate, compile, and publish a metric (status → PUBLISHED).
        api_response = await api_instance.publish(metric_id)
        print("The response of SemanticMetricsApi->publish:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SemanticMetricsApi->publish: %s\n" % e)
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
> SemanticMetricRead retire(metric_id)

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
    api_instance = flyquery_sdk.SemanticMetricsApi(api_client)
    metric_id = 'metric_id_example' # str | 

    try:
        # Retire a metric (status → RETIRED).
        api_response = await api_instance.retire(metric_id)
        print("The response of SemanticMetricsApi->retire:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SemanticMetricsApi->retire: %s\n" % e)
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
> SemanticMetricRead update(metric_id, semantic_metric_update)

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
    api_instance = flyquery_sdk.SemanticMetricsApi(api_client)
    metric_id = 'metric_id_example' # str | 
    semantic_metric_update = flyquery_sdk.SemanticMetricUpdate() # SemanticMetricUpdate | 

    try:
        # Sparse-update a metric; re-validates YAML if definition changes.
        api_response = await api_instance.update(metric_id, semantic_metric_update)
        print("The response of SemanticMetricsApi->update:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SemanticMetricsApi->update: %s\n" % e)
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

