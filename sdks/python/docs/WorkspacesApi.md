# flyquery_sdk.WorkspacesApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create**](WorkspacesApi.md#create) | **POST** /api/v1/workspaces | Create a workspace; tenant comes from &#x60;&#x60;X-Tenant-Id&#x60;&#x60; header.
[**list_workspaces**](WorkspacesApi.md#list_workspaces) | **GET** /api/v1/workspaces | Search/filter workspaces for the caller&#39;s tenant.
[**purge**](WorkspacesApi.md#purge) | **DELETE** /api/v1/workspaces/{workspace_id}:purge | Purge a workspace: mark PURGING + walk + delete all blobs.
[**read**](WorkspacesApi.md#read) | **GET** /api/v1/workspaces/{workspace_id} | Fetch a single workspace by id. Returns 404 if not found.
[**read_by_slug**](WorkspacesApi.md#read_by_slug) | **GET** /api/v1/workspaces/by-slug/{slug} | Fetch a workspace by its &#x60;&#x60;(tenant_id, slug)&#x60;&#x60; natural key.
[**update**](WorkspacesApi.md#update) | **PUT** /api/v1/workspaces/{workspace_id} | Sparse-update a workspace. Only fields present in body are changed.


# **create**
> WorkspaceRead create(workspace_create)

Create a workspace; tenant comes from ``X-Tenant-Id`` header.

### Example


```python
import flyquery_sdk
from flyquery_sdk.models.workspace_create import WorkspaceCreate
from flyquery_sdk.models.workspace_read import WorkspaceRead
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
    api_instance = flyquery_sdk.WorkspacesApi(api_client)
    workspace_create = flyquery_sdk.WorkspaceCreate() # WorkspaceCreate | 

    try:
        # Create a workspace; tenant comes from ``X-Tenant-Id`` header.
        api_response = await api_instance.create(workspace_create)
        print("The response of WorkspacesApi->create:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkspacesApi->create: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_create** | [**WorkspaceCreate**](WorkspaceCreate.md)|  | 

### Return type

[**WorkspaceRead**](WorkspaceRead.md)

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

# **list_workspaces**
> list_workspaces(q=q, slug=slug, status=status, limit=limit, offset=offset)

Search/filter workspaces for the caller's tenant.

Query parameters
----------------
* ``q``      -- free-text substring match against ``slug`` or ``name``
(case-insensitive ``ILIKE``).
* ``slug``   -- exact match on ``slug`` -- gives you slug-based lookup
with zero extra round trips.
* ``status`` -- exact match (``ACTIVE``, ``ARCHIVED``, ``PURGING``).
* ``limit``  -- page size, clamped to [1, 1000]. Default 100.
* ``offset`` -- starting offset. Default 0.

Response envelope: ``{items, total, limit, offset, has_more}``
where ``total`` is the un-paginated match count.

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
    api_instance = flyquery_sdk.WorkspacesApi(api_client)
    q = 'q_example' # str |  (optional)
    slug = 'slug_example' # str |  (optional)
    status = 'status_example' # str |  (optional)
    limit = 100 # int |  (optional) (default to 100)
    offset = 0 # int |  (optional) (default to 0)

    try:
        # Search/filter workspaces for the caller's tenant.
        await api_instance.list_workspaces(q=q, slug=slug, status=status, limit=limit, offset=offset)
    except Exception as e:
        print("Exception when calling WorkspacesApi->list_workspaces: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **q** | **str**|  | [optional] 
 **slug** | **str**|  | [optional] 
 **status** | **str**|  | [optional] 
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

# **purge**
> purge(workspace_id)

Purge a workspace: mark PURGING + walk + delete all blobs.

Returns 202 Accepted with a tombstone placeholder.

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
    api_instance = flyquery_sdk.WorkspacesApi(api_client)
    workspace_id = 'workspace_id_example' # str | 

    try:
        # Purge a workspace: mark PURGING + walk + delete all blobs.
        await api_instance.purge(workspace_id)
    except Exception as e:
        print("Exception when calling WorkspacesApi->purge: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**|  | 

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
**202** | Successful response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **read**
> WorkspaceRead read(workspace_id)

Fetch a single workspace by id. Returns 404 if not found.

### Example


```python
import flyquery_sdk
from flyquery_sdk.models.workspace_read import WorkspaceRead
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
    api_instance = flyquery_sdk.WorkspacesApi(api_client)
    workspace_id = 'workspace_id_example' # str | 

    try:
        # Fetch a single workspace by id. Returns 404 if not found.
        api_response = await api_instance.read(workspace_id)
        print("The response of WorkspacesApi->read:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkspacesApi->read: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**|  | 

### Return type

[**WorkspaceRead**](WorkspaceRead.md)

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

# **read_by_slug**
> WorkspaceRead read_by_slug(slug)

Fetch a workspace by its ``(tenant_id, slug)`` natural key.

Lets SDKs and CLIs resolve a workspace from a memorable identifier
instead of carrying around a UUID. Returns 404 if no match.

### Example


```python
import flyquery_sdk
from flyquery_sdk.models.workspace_read import WorkspaceRead
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
    api_instance = flyquery_sdk.WorkspacesApi(api_client)
    slug = 'slug_example' # str | 

    try:
        # Fetch a workspace by its ``(tenant_id, slug)`` natural key.
        api_response = await api_instance.read_by_slug(slug)
        print("The response of WorkspacesApi->read_by_slug:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkspacesApi->read_by_slug: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **slug** | **str**|  | 

### Return type

[**WorkspaceRead**](WorkspaceRead.md)

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
> WorkspaceRead update(workspace_id, workspace_update)

Sparse-update a workspace. Only fields present in body are changed.

### Example


```python
import flyquery_sdk
from flyquery_sdk.models.workspace_read import WorkspaceRead
from flyquery_sdk.models.workspace_update import WorkspaceUpdate
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
    api_instance = flyquery_sdk.WorkspacesApi(api_client)
    workspace_id = 'workspace_id_example' # str | 
    workspace_update = flyquery_sdk.WorkspaceUpdate() # WorkspaceUpdate | 

    try:
        # Sparse-update a workspace. Only fields present in body are changed.
        api_response = await api_instance.update(workspace_id, workspace_update)
        print("The response of WorkspacesApi->update:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkspacesApi->update: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**|  | 
 **workspace_update** | [**WorkspaceUpdate**](WorkspaceUpdate.md)|  | 

### Return type

[**WorkspaceRead**](WorkspaceRead.md)

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

