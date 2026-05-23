# flyquery_sdk.ConversationsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create**](ConversationsApi.md#create) | **POST** /api/v1/conversations | Create a new conversation.
[**list_conversations**](ConversationsApi.md#list_conversations) | **GET** /api/v1/conversations | List conversations for the caller&#39;s workspace, newest first.
[**post_turn**](ConversationsApi.md#post_turn) | **POST** /api/v1/conversations/{conversation_id}/turn | Ask a follow-up question inside an existing conversation.
[**read**](ConversationsApi.md#read) | **GET** /api/v1/conversations/{conversation_id} | Fetch a conversation with all its turns.


# **create**
> ConversationRead create(conversation_create)

Create a new conversation.

:param http_request: Starlette request (tenant context headers)
:param body: optional title
:return: the new ConversationRead (no turns yet)

### Example


```python
import flyquery_sdk
from flyquery_sdk.models.conversation_create import ConversationCreate
from flyquery_sdk.models.conversation_read import ConversationRead
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
    api_instance = flyquery_sdk.ConversationsApi(api_client)
    conversation_create = flyquery_sdk.ConversationCreate() # ConversationCreate | 

    try:
        # Create a new conversation.
        api_response = await api_instance.create(conversation_create)
        print("The response of ConversationsApi->create:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ConversationsApi->create: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **conversation_create** | [**ConversationCreate**](ConversationCreate.md)|  | 

### Return type

[**ConversationRead**](ConversationRead.md)

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

# **list_conversations**
> list_conversations()

List conversations for the caller's workspace, newest first.

:param http_request: Starlette request
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
    api_instance = flyquery_sdk.ConversationsApi(api_client)

    try:
        # List conversations for the caller's workspace, newest first.
        await api_instance.list_conversations()
    except Exception as e:
        print("Exception when calling ConversationsApi->list_conversations: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

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

# **post_turn**
> AnswerResponse post_turn(conversation_id, conversation_turn_request)

Ask a follow-up question inside an existing conversation.

Loads the prior turn's ``executed_sql + table_qnames + snapshot_pins``
and passes them into the query pipeline as drill-down context.

:param http_request: Starlette request
:param conversation_id: conversation UUID
:param body: dataset_id + question
:return: AnswerResponse from the full pipeline

### Example


```python
import flyquery_sdk
from flyquery_sdk.models.answer_response import AnswerResponse
from flyquery_sdk.models.conversation_turn_request import ConversationTurnRequest
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
    api_instance = flyquery_sdk.ConversationsApi(api_client)
    conversation_id = 'conversation_id_example' # str | 
    conversation_turn_request = flyquery_sdk.ConversationTurnRequest() # ConversationTurnRequest | 

    try:
        # Ask a follow-up question inside an existing conversation.
        api_response = await api_instance.post_turn(conversation_id, conversation_turn_request)
        print("The response of ConversationsApi->post_turn:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ConversationsApi->post_turn: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **conversation_id** | **str**|  | 
 **conversation_turn_request** | [**ConversationTurnRequest**](ConversationTurnRequest.md)|  | 

### Return type

[**AnswerResponse**](AnswerResponse.md)

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

# **read**
> ConversationRead read(conversation_id)

Fetch a conversation with all its turns.

:param conversation_id: conversation UUID
:return: ConversationRead including turns list
:raises ResourceNotFound: when conversation does not exist

### Example


```python
import flyquery_sdk
from flyquery_sdk.models.conversation_read import ConversationRead
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
    api_instance = flyquery_sdk.ConversationsApi(api_client)
    conversation_id = 'conversation_id_example' # str | 

    try:
        # Fetch a conversation with all its turns.
        api_response = await api_instance.read(conversation_id)
        print("The response of ConversationsApi->read:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ConversationsApi->read: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **conversation_id** | **str**|  | 

### Return type

[**ConversationRead**](ConversationRead.md)

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

