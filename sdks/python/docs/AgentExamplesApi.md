# flyquery_sdk.AgentExamplesApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create**](AgentExamplesApi.md#create) | **POST** /api/v1/agent/examples | Create an example (agent-tier — source&#x3D;AGENT_LEARNED, quality&#x3D;PROPOSED).
[**list_examples**](AgentExamplesApi.md#list_examples) | **GET** /api/v1/agent/examples | List examples for the caller&#39;s workspace (agent-tier).


# **create**
> ExampleRead create(example_create)

Create an example (agent-tier — source=AGENT_LEARNED, quality=PROPOSED).

:param http_request: Starlette request
:param body: validated ExampleCreate
:return: ExampleRead with created fields

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
    api_instance = flyquery_sdk.AgentExamplesApi(api_client)
    example_create = flyquery_sdk.ExampleCreate() # ExampleCreate | 

    try:
        # Create an example (agent-tier — source=AGENT_LEARNED, quality=PROPOSED).
        api_response = await api_instance.create(example_create)
        print("The response of AgentExamplesApi->create:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentExamplesApi->create: %s\n" % e)
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

List examples for the caller's workspace (agent-tier).

:param http_request: Starlette request
:param quality: optional quality filter (PROPOSED/APPROVED/REJECTED)
:param dataset_id: optional dataset filter
:return: ``{"items": [...]}``

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
    api_instance = flyquery_sdk.AgentExamplesApi(api_client)
    quality = 'null' # str |  (optional) (default to 'null')
    dataset_id = 'dataset_id_example' # str |  (optional)

    try:
        # List examples for the caller's workspace (agent-tier).
        await api_instance.list_examples(quality=quality, dataset_id=dataset_id)
    except Exception as e:
        print("Exception when calling AgentExamplesApi->list_examples: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **quality** | **str**|  | [optional] [default to &#39;null&#39;]
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

