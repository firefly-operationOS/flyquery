# flyquery_sdk.TablesApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**derive**](TablesApi.md#derive) | **POST** /api/v1/tables:derive | Materialise a SELECT result as a new DERIVED table.
[**get_table**](TablesApi.md#get_table) | **GET** /api/v1/tables/{table_id} | 
[**list_changes**](TablesApi.md#list_changes) | **GET** /api/v1/tables/{table_id}/changes | 
[**list_objects**](TablesApi.md#list_objects) | **GET** /api/v1/tables/{table_id}/objects | List schema_objects for the table&#39;s current snapshot.
[**list_snapshots**](TablesApi.md#list_snapshots) | **GET** /api/v1/tables/{table_id}/snapshots | 
[**list_tables**](TablesApi.md#list_tables) | **GET** /api/v1/datasets/{dataset_id}/tables | 


# **derive**
> DeriveTableResponse derive(derive_table_request)

Materialise a SELECT result as a new DERIVED table.

:param http_request: Starlette request (tenant context headers)
:param body: dataset_id + name + sql (must be a SELECT)
:return: DeriveTableResponse with the new table_id
:raises DeriveTableForbidden: when sql is not a SELECT
:raises DeriveTableError: when DuckDB execution fails

### Example


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


# Enter a context with an instance of the API client
async with flyquery_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = flyquery_sdk.TablesApi(api_client)
    derive_table_request = flyquery_sdk.DeriveTableRequest() # DeriveTableRequest | 

    try:
        # Materialise a SELECT result as a new DERIVED table.
        api_response = await api_instance.derive(derive_table_request)
        print("The response of TablesApi->derive:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TablesApi->derive: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **derive_table_request** | [**DeriveTableRequest**](DeriveTableRequest.md)|  | 

### Return type

[**DeriveTableResponse**](DeriveTableResponse.md)

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

# **get_table**
> TableRead get_table(table_id)

### Example


```python
import flyquery_sdk
from flyquery_sdk.models.table_read import TableRead
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
    api_instance = flyquery_sdk.TablesApi(api_client)
    table_id = 'table_id_example' # str | 

    try:
        api_response = await api_instance.get_table(table_id)
        print("The response of TablesApi->get_table:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TablesApi->get_table: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **table_id** | **str**|  | 

### Return type

[**TableRead**](TableRead.md)

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

# **list_changes**
> list_changes(table_id)

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
    api_instance = flyquery_sdk.TablesApi(api_client)
    table_id = 'table_id_example' # str | 

    try:
        await api_instance.list_changes(table_id)
    except Exception as e:
        print("Exception when calling TablesApi->list_changes: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **table_id** | **str**|  | 

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

# **list_objects**
> list_objects(table_id)

List schema_objects for the table's current snapshot.

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
    api_instance = flyquery_sdk.TablesApi(api_client)
    table_id = 'table_id_example' # str | 

    try:
        # List schema_objects for the table's current snapshot.
        await api_instance.list_objects(table_id)
    except Exception as e:
        print("Exception when calling TablesApi->list_objects: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **table_id** | **str**|  | 

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

# **list_snapshots**
> list_snapshots(table_id)

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
    api_instance = flyquery_sdk.TablesApi(api_client)
    table_id = 'table_id_example' # str | 

    try:
        await api_instance.list_snapshots(table_id)
    except Exception as e:
        print("Exception when calling TablesApi->list_snapshots: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **table_id** | **str**|  | 

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

# **list_tables**
> list_tables(dataset_id)

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
    api_instance = flyquery_sdk.TablesApi(api_client)
    dataset_id = 'dataset_id_example' # str | 

    try:
        await api_instance.list_tables(dataset_id)
    except Exception as e:
        print("Exception when calling TablesApi->list_tables: %s\n" % e)
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

