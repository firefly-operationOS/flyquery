# flyquery_sdk.DatasetsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**archive**](DatasetsApi.md#archive) | **DELETE** /api/v1/datasets/{dataset_id} | Archive a dataset (set status&#x3D;ARCHIVED).
[**create**](DatasetsApi.md#create) | **POST** /api/v1/datasets | Create a dataset; tenant + workspace come from request headers.
[**list_datasets**](DatasetsApi.md#list_datasets) | **GET** /api/v1/datasets | Search/filter datasets for the caller&#39;s tenant.
[**read**](DatasetsApi.md#read) | **GET** /api/v1/datasets/{dataset_id} | Fetch a single dataset by id. Returns 404 if not found.
[**read_by_name**](DatasetsApi.md#read_by_name) | **GET** /api/v1/datasets/by-name/{name} | Resolve a dataset by &#x60;&#x60;(tenant_id, workspace_id, name)&#x60;&#x60;.
[**update**](DatasetsApi.md#update) | **PUT** /api/v1/datasets/{dataset_id} | Sparse-update a dataset. Only fields present in body are changed.


# **archive**
> DatasetRead archive(dataset_id)

Archive a dataset (set status=ARCHIVED).

### Example


```python
import flyquery_sdk
from flyquery_sdk.models.dataset_read import DatasetRead
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
    api_instance = flyquery_sdk.DatasetsApi(api_client)
    dataset_id = 'dataset_id_example' # str | 

    try:
        # Archive a dataset (set status=ARCHIVED).
        api_response = await api_instance.archive(dataset_id)
        print("The response of DatasetsApi->archive:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DatasetsApi->archive: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **dataset_id** | **str**|  | 

### Return type

[**DatasetRead**](DatasetRead.md)

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
> DatasetRead create(dataset_create)

Create a dataset; tenant + workspace come from request headers.

### Example


```python
import flyquery_sdk
from flyquery_sdk.models.dataset_create import DatasetCreate
from flyquery_sdk.models.dataset_read import DatasetRead
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
    api_instance = flyquery_sdk.DatasetsApi(api_client)
    dataset_create = flyquery_sdk.DatasetCreate() # DatasetCreate | 

    try:
        # Create a dataset; tenant + workspace come from request headers.
        api_response = await api_instance.create(dataset_create)
        print("The response of DatasetsApi->create:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DatasetsApi->create: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **dataset_create** | [**DatasetCreate**](DatasetCreate.md)|  | 

### Return type

[**DatasetRead**](DatasetRead.md)

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

# **list_datasets**
> list_datasets(q=q, name=name, status=status, workspace_id=workspace_id, limit=limit, offset=offset)

Search/filter datasets for the caller's tenant.

Query parameters
----------------
* ``q``            -- free-text substring against ``name`` or
``description`` (case-insensitive ``ILIKE``).
* ``name``         -- exact match -- gives you name-based lookup
with zero extra round-trips.
* ``status``       -- ``ACTIVE`` / ``ARCHIVED`` / ``PURGING``.
* ``workspace_id`` -- restrict to a single workspace; defaults to
``X-Workspace-Id`` header. Pass another UUID
explicitly to override the header.
* ``limit``        -- page size, clamped to [1, 1000]. Default 100.
* ``offset``       -- starting offset. Default 0.

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
    api_instance = flyquery_sdk.DatasetsApi(api_client)
    q = 'q_example' # str |  (optional)
    name = 'name_example' # str |  (optional)
    status = 'status_example' # str |  (optional)
    workspace_id = 'workspace_id_example' # str |  (optional)
    limit = 100 # int |  (optional) (default to 100)
    offset = 0 # int |  (optional) (default to 0)

    try:
        # Search/filter datasets for the caller's tenant.
        await api_instance.list_datasets(q=q, name=name, status=status, workspace_id=workspace_id, limit=limit, offset=offset)
    except Exception as e:
        print("Exception when calling DatasetsApi->list_datasets: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **q** | **str**|  | [optional] 
 **name** | **str**|  | [optional] 
 **status** | **str**|  | [optional] 
 **workspace_id** | **str**|  | [optional] 
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

# **read**
> DatasetRead read(dataset_id)

Fetch a single dataset by id. Returns 404 if not found.

### Example


```python
import flyquery_sdk
from flyquery_sdk.models.dataset_read import DatasetRead
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
    api_instance = flyquery_sdk.DatasetsApi(api_client)
    dataset_id = 'dataset_id_example' # str | 

    try:
        # Fetch a single dataset by id. Returns 404 if not found.
        api_response = await api_instance.read(dataset_id)
        print("The response of DatasetsApi->read:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DatasetsApi->read: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **dataset_id** | **str**|  | 

### Return type

[**DatasetRead**](DatasetRead.md)

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

# **read_by_name**
> DatasetRead read_by_name(name)

Resolve a dataset by ``(tenant_id, workspace_id, name)``.

Reads the workspace scope from ``X-Workspace-Id``. Datasets enforce
``UNIQUE(workspace_id, name)`` so the lookup always returns 0 or 1.

### Example


```python
import flyquery_sdk
from flyquery_sdk.models.dataset_read import DatasetRead
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
    api_instance = flyquery_sdk.DatasetsApi(api_client)
    name = 'name_example' # str | 

    try:
        # Resolve a dataset by ``(tenant_id, workspace_id, name)``.
        api_response = await api_instance.read_by_name(name)
        print("The response of DatasetsApi->read_by_name:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DatasetsApi->read_by_name: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**|  | 

### Return type

[**DatasetRead**](DatasetRead.md)

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
> DatasetRead update(dataset_id, dataset_update)

Sparse-update a dataset. Only fields present in body are changed.

### Example


```python
import flyquery_sdk
from flyquery_sdk.models.dataset_read import DatasetRead
from flyquery_sdk.models.dataset_update import DatasetUpdate
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
    api_instance = flyquery_sdk.DatasetsApi(api_client)
    dataset_id = 'dataset_id_example' # str | 
    dataset_update = flyquery_sdk.DatasetUpdate() # DatasetUpdate | 

    try:
        # Sparse-update a dataset. Only fields present in body are changed.
        api_response = await api_instance.update(dataset_id, dataset_update)
        print("The response of DatasetsApi->update:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DatasetsApi->update: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **dataset_id** | **str**|  | 
 **dataset_update** | [**DatasetUpdate**](DatasetUpdate.md)|  | 

### Return type

[**DatasetRead**](DatasetRead.md)

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

