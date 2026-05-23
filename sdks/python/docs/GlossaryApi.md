# flyquery_sdk.GlossaryApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create**](GlossaryApi.md#create) | **POST** /api/v1/glossary | Create a glossary term; (workspace_id, term) must be unique.
[**delete**](GlossaryApi.md#delete) | **DELETE** /api/v1/glossary/{term_id} | Hard-delete a glossary term.
[**list_terms**](GlossaryApi.md#list_terms) | **GET** /api/v1/glossary | Return paginated glossary terms for the caller&#39;s workspace.
[**update**](GlossaryApi.md#update) | **PUT** /api/v1/glossary/{term_id} | Sparse-update a glossary term.


# **create**
> GlossaryTermRead create(glossary_term_create)

Create a glossary term; (workspace_id, term) must be unique.

### Example


```python
import flyquery_sdk
from flyquery_sdk.models.glossary_term_create import GlossaryTermCreate
from flyquery_sdk.models.glossary_term_read import GlossaryTermRead
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
    api_instance = flyquery_sdk.GlossaryApi(api_client)
    glossary_term_create = flyquery_sdk.GlossaryTermCreate() # GlossaryTermCreate | 

    try:
        # Create a glossary term; (workspace_id, term) must be unique.
        api_response = await api_instance.create(glossary_term_create)
        print("The response of GlossaryApi->create:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling GlossaryApi->create: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **glossary_term_create** | [**GlossaryTermCreate**](GlossaryTermCreate.md)|  | 

### Return type

[**GlossaryTermRead**](GlossaryTermRead.md)

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

# **delete**
> delete(term_id)

Hard-delete a glossary term.

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
    api_instance = flyquery_sdk.GlossaryApi(api_client)
    term_id = 'term_id_example' # str | 

    try:
        # Hard-delete a glossary term.
        await api_instance.delete(term_id)
    except Exception as e:
        print("Exception when calling GlossaryApi->delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **term_id** | **str**|  | 

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
**204** | No Content |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_terms**
> list_terms(limit=limit, offset=offset)

Return paginated glossary terms for the caller's workspace.

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
    api_instance = flyquery_sdk.GlossaryApi(api_client)
    limit = 100 # int |  (optional) (default to 100)
    offset = 0 # int |  (optional) (default to 0)

    try:
        # Return paginated glossary terms for the caller's workspace.
        await api_instance.list_terms(limit=limit, offset=offset)
    except Exception as e:
        print("Exception when calling GlossaryApi->list_terms: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
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

# **update**
> GlossaryTermRead update(term_id, glossary_term_update)

Sparse-update a glossary term.

### Example


```python
import flyquery_sdk
from flyquery_sdk.models.glossary_term_read import GlossaryTermRead
from flyquery_sdk.models.glossary_term_update import GlossaryTermUpdate
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
    api_instance = flyquery_sdk.GlossaryApi(api_client)
    term_id = 'term_id_example' # str | 
    glossary_term_update = flyquery_sdk.GlossaryTermUpdate() # GlossaryTermUpdate | 

    try:
        # Sparse-update a glossary term.
        api_response = await api_instance.update(term_id, glossary_term_update)
        print("The response of GlossaryApi->update:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling GlossaryApi->update: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **term_id** | **str**|  | 
 **glossary_term_update** | [**GlossaryTermUpdate**](GlossaryTermUpdate.md)|  | 

### Return type

[**GlossaryTermRead**](GlossaryTermRead.md)

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

