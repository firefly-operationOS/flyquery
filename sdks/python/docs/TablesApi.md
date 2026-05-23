# flyquery_sdk.TablesApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_table**](TablesApi.md#get_table) | **GET** /api/v1/tables/{table_id} | 
[**get_table_by_name**](TablesApi.md#get_table_by_name) | **GET** /api/v1/tables/by-name/{name} | Resolve a table by &#x60;&#x60;name&#x60;&#x60; within the caller&#39;s workspace.
[**list_changes**](TablesApi.md#list_changes) | **GET** /api/v1/tables/{table_id}/changes | 
[**list_objects**](TablesApi.md#list_objects) | **GET** /api/v1/tables/{table_id}/objects | List schema_objects for the table&#39;s current snapshot.
[**list_snapshots**](TablesApi.md#list_snapshots) | **GET** /api/v1/tables/{table_id}/snapshots | 
[**list_tables**](TablesApi.md#list_tables) | **GET** /api/v1/datasets/{dataset_id}/tables | 
[**search_tables**](TablesApi.md#search_tables) | **GET** /api/v1/tables | Search/filter tables across the caller&#39;s workspace.


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

# **get_table_by_name**
> TableRead get_table_by_name(name, dataset_id=dataset_id)

Resolve a table by ``name`` within the caller's workspace.

Pass ``?dataset_id=...`` to scope the lookup to a single dataset.
Returns 404 if the name is not unique within the scope or no
match is found.

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
    name = 'name_example' # str | 
    dataset_id = 'dataset_id_example' # str |  (optional)

    try:
        # Resolve a table by ``name`` within the caller's workspace.
        api_response = await api_instance.get_table_by_name(name, dataset_id=dataset_id)
        print("The response of TablesApi->get_table_by_name:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TablesApi->get_table_by_name: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**|  | 
 **dataset_id** | **str**|  | [optional] 

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

# **search_tables**
> search_tables(q=q, name=name, dataset_id=dataset_id, kind=kind, is_active=is_active, limit=limit, offset=offset)

Search/filter tables across the caller's workspace.

Query parameters
----------------
* ``q``          -- substring match on ``name`` or ``qualified_name``
(case-insensitive ``ILIKE``).
* ``name``       -- exact match on ``name``.
* ``dataset_id`` -- restrict to a single dataset.
* ``kind``       -- ``UPLOADED`` / ``VIEW`` / ``DERIVED``.
* ``is_active``  -- default ``true``; pass ``false`` to include
archived tables.
* ``limit``      -- page size, clamped to [1, 1000]. Default 100.
* ``offset``     -- starting offset. Default 0.

Response envelope: ``{items, total, limit, offset, has_more}``.

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
    q = 'q_example' # str |  (optional)
    name = 'name_example' # str |  (optional)
    dataset_id = 'dataset_id_example' # str |  (optional)
    kind = 'kind_example' # str |  (optional)
    is_active = 'is_active_example' # str |  (optional)
    limit = 100 # int |  (optional) (default to 100)
    offset = 0 # int |  (optional) (default to 0)

    try:
        # Search/filter tables across the caller's workspace.
        await api_instance.search_tables(q=q, name=name, dataset_id=dataset_id, kind=kind, is_active=is_active, limit=limit, offset=offset)
    except Exception as e:
        print("Exception when calling TablesApi->search_tables: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **q** | **str**|  | [optional] 
 **name** | **str**|  | [optional] 
 **dataset_id** | **str**|  | [optional] 
 **kind** | **str**|  | [optional] 
 **is_active** | **str**|  | [optional] 
 **limit** | **int**|  | [optional] [default to 100]
 **offset** | **int**|  | [optional] [default to 0]

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

