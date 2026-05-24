# flyquery_sdk.ConversationsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create**](ConversationsApi.md#create) | **POST** /api/v1/conversations | Create a new conversation.
[**list_conversations**](ConversationsApi.md#list_conversations) | **GET** /api/v1/conversations | List conversations for the caller&#39;s workspace, newest first.
[**post_turn**](ConversationsApi.md#post_turn) | **POST** /api/v1/conversations/{conversation_id}/turn | Ask a follow-up question inside an existing conversation.
[**read**](ConversationsApi.md#read) | **GET** /api/v1/conversations/{conversation_id} | Fetch a conversation with all its turns.


# **create**
> ConversationRead create(x_tenant_id, x_workspace_id, conversation_create, x_correlation_id=x_correlation_id, idempotency_key=idempotency_key)

Create a new conversation.

:param http_request: Starlette request (tenant context headers)
:param body: optional title
:return: the new ConversationRead (no turns yet)

### Example

* Api Key Authentication (WorkspaceContext):
* Api Key Authentication (TenantContext):

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

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: WorkspaceContext
configuration.api_key['WorkspaceContext'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['WorkspaceContext'] = 'Bearer'

# Configure API key authorization: TenantContext
configuration.api_key['TenantContext'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['TenantContext'] = 'Bearer'

# Enter a context with an instance of the API client
async with flyquery_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = flyquery_sdk.ConversationsApi(api_client)
    x_tenant_id = 'acme-corp' # str | Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
    x_workspace_id = '00000000-0000-0000-0000-000000000001' # str | Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
    conversation_create = flyquery_sdk.ConversationCreate() # ConversationCreate | 
    x_correlation_id = UUID('550e8400-e29b-41d4-a716-446655440000') # UUID | Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. (optional)
    idempotency_key = 'ingest-2026-05-23-abc123' # str | Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h. (optional)

    try:
        # Create a new conversation.
        api_response = await api_instance.create(x_tenant_id, x_workspace_id, conversation_create, x_correlation_id=x_correlation_id, idempotency_key=idempotency_key)
        print("The response of ConversationsApi->create:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ConversationsApi->create: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **x_tenant_id** | **str**| Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present. | 
 **x_workspace_id** | **str**| Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation. | 
 **conversation_create** | [**ConversationCreate**](ConversationCreate.md)|  | 
 **x_correlation_id** | **UUID**| Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. | [optional] 
 **idempotency_key** | **str**| Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h. | [optional] 

### Return type

[**ConversationRead**](ConversationRead.md)

### Authorization

[WorkspaceContext](../README.md#WorkspaceContext), [TenantContext](../README.md#TenantContext)

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
> PaginatedConversationRead list_conversations(x_tenant_id, x_workspace_id, limit=limit, offset=offset, x_correlation_id=x_correlation_id)

List conversations for the caller's workspace, newest first.

Service does not currently return a total; ``has_more`` is
inferred from page size (``len(items) >= limit`` -> assume
there may be more).

### Example

* Api Key Authentication (WorkspaceContext):
* Api Key Authentication (TenantContext):

```python
import flyquery_sdk
from flyquery_sdk.models.paginated_conversation_read import PaginatedConversationRead
from flyquery_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = flyquery_sdk.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: WorkspaceContext
configuration.api_key['WorkspaceContext'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['WorkspaceContext'] = 'Bearer'

# Configure API key authorization: TenantContext
configuration.api_key['TenantContext'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['TenantContext'] = 'Bearer'

# Enter a context with an instance of the API client
async with flyquery_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = flyquery_sdk.ConversationsApi(api_client)
    x_tenant_id = 'acme-corp' # str | Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
    x_workspace_id = '00000000-0000-0000-0000-000000000001' # str | Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
    limit = 100 # int |  (optional) (default to 100)
    offset = 0 # int |  (optional) (default to 0)
    x_correlation_id = UUID('550e8400-e29b-41d4-a716-446655440000') # UUID | Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. (optional)

    try:
        # List conversations for the caller's workspace, newest first.
        api_response = await api_instance.list_conversations(x_tenant_id, x_workspace_id, limit=limit, offset=offset, x_correlation_id=x_correlation_id)
        print("The response of ConversationsApi->list_conversations:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ConversationsApi->list_conversations: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **x_tenant_id** | **str**| Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present. | 
 **x_workspace_id** | **str**| Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation. | 
 **limit** | **int**|  | [optional] [default to 100]
 **offset** | **int**|  | [optional] [default to 0]
 **x_correlation_id** | **UUID**| Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. | [optional] 

### Return type

[**PaginatedConversationRead**](PaginatedConversationRead.md)

### Authorization

[WorkspaceContext](../README.md#WorkspaceContext), [TenantContext](../README.md#TenantContext)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_turn**
> AnswerResponse post_turn(conversation_id, x_tenant_id, x_workspace_id, conversation_turn_request, x_correlation_id=x_correlation_id, idempotency_key=idempotency_key)

Ask a follow-up question inside an existing conversation.

Loads the prior turn's ``executed_sql + table_qnames + snapshot_pins``
and passes them into the query pipeline as drill-down context.

:param http_request: Starlette request
:param conversation_id: conversation UUID
:param body: dataset_id + question
:return: AnswerResponse from the full pipeline

### Example

* Api Key Authentication (WorkspaceContext):
* Api Key Authentication (TenantContext):

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

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: WorkspaceContext
configuration.api_key['WorkspaceContext'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['WorkspaceContext'] = 'Bearer'

# Configure API key authorization: TenantContext
configuration.api_key['TenantContext'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['TenantContext'] = 'Bearer'

# Enter a context with an instance of the API client
async with flyquery_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = flyquery_sdk.ConversationsApi(api_client)
    conversation_id = 'conversation_id_example' # str | 
    x_tenant_id = 'acme-corp' # str | Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
    x_workspace_id = '00000000-0000-0000-0000-000000000001' # str | Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
    conversation_turn_request = flyquery_sdk.ConversationTurnRequest() # ConversationTurnRequest | 
    x_correlation_id = UUID('550e8400-e29b-41d4-a716-446655440000') # UUID | Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. (optional)
    idempotency_key = 'ingest-2026-05-23-abc123' # str | Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h. (optional)

    try:
        # Ask a follow-up question inside an existing conversation.
        api_response = await api_instance.post_turn(conversation_id, x_tenant_id, x_workspace_id, conversation_turn_request, x_correlation_id=x_correlation_id, idempotency_key=idempotency_key)
        print("The response of ConversationsApi->post_turn:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ConversationsApi->post_turn: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **conversation_id** | **str**|  | 
 **x_tenant_id** | **str**| Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present. | 
 **x_workspace_id** | **str**| Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation. | 
 **conversation_turn_request** | [**ConversationTurnRequest**](ConversationTurnRequest.md)|  | 
 **x_correlation_id** | **UUID**| Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. | [optional] 
 **idempotency_key** | **str**| Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h. | [optional] 

### Return type

[**AnswerResponse**](AnswerResponse.md)

### Authorization

[WorkspaceContext](../README.md#WorkspaceContext), [TenantContext](../README.md#TenantContext)

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
> ConversationRead read(conversation_id, x_tenant_id, x_workspace_id, x_correlation_id=x_correlation_id)

Fetch a conversation with all its turns.

:param conversation_id: conversation UUID
:return: ConversationRead including turns list
:raises ResourceNotFound: when conversation does not exist

### Example

* Api Key Authentication (WorkspaceContext):
* Api Key Authentication (TenantContext):

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

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: WorkspaceContext
configuration.api_key['WorkspaceContext'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['WorkspaceContext'] = 'Bearer'

# Configure API key authorization: TenantContext
configuration.api_key['TenantContext'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['TenantContext'] = 'Bearer'

# Enter a context with an instance of the API client
async with flyquery_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = flyquery_sdk.ConversationsApi(api_client)
    conversation_id = 'conversation_id_example' # str | 
    x_tenant_id = 'acme-corp' # str | Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
    x_workspace_id = '00000000-0000-0000-0000-000000000001' # str | Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
    x_correlation_id = UUID('550e8400-e29b-41d4-a716-446655440000') # UUID | Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. (optional)

    try:
        # Fetch a conversation with all its turns.
        api_response = await api_instance.read(conversation_id, x_tenant_id, x_workspace_id, x_correlation_id=x_correlation_id)
        print("The response of ConversationsApi->read:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ConversationsApi->read: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **conversation_id** | **str**|  | 
 **x_tenant_id** | **str**| Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present. | 
 **x_workspace_id** | **str**| Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation. | 
 **x_correlation_id** | **UUID**| Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header. | [optional] 

### Return type

[**ConversationRead**](ConversationRead.md)

### Authorization

[WorkspaceContext](../README.md#WorkspaceContext), [TenantContext](../README.md#TenantContext)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

