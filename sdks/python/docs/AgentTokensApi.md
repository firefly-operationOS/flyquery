# flyquery_sdk.AgentTokensApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**list_tokens**](AgentTokensApi.md#list_tokens) | **GET** /api/v1/agent-tokens | List tokens for the current tenant (newest first).
[**mint**](AgentTokensApi.md#mint) | **POST** /api/v1/agent-tokens | Mint a new agent token.
[**revoke**](AgentTokensApi.md#revoke) | **DELETE** /api/v1/agent-tokens/{token_id} | Revoke a token. Idempotent -- already-revoked is a no-op (204).


# **list_tokens**
> List[AgentTokenSummaryDto] list_tokens()

List tokens for the current tenant (newest first).

Returns the summary shape only -- the secret is never
round-tripped on this endpoint.

### Example


```python
import flyquery_sdk
from flyquery_sdk.models.agent_token_summary_dto import AgentTokenSummaryDto
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
    api_instance = flyquery_sdk.AgentTokensApi(api_client)

    try:
        # List tokens for the current tenant (newest first).
        api_response = await api_instance.list_tokens()
        print("The response of AgentTokensApi->list_tokens:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentTokensApi->list_tokens: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**List[AgentTokenSummaryDto]**](AgentTokenSummaryDto.md)

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

# **mint**
> AgentTokenCreated mint(agent_token_mint_request)

Mint a new agent token.

Returns 201 with the full ``token`` populated. The token is
only returned this once -- subsequent reads expose only
``prefix``. Refuses agent-tier callers with
``403 agent_cannot_mint``.

### Example


```python
import flyquery_sdk
from flyquery_sdk.models.agent_token_created import AgentTokenCreated
from flyquery_sdk.models.agent_token_mint_request import AgentTokenMintRequest
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
    api_instance = flyquery_sdk.AgentTokensApi(api_client)
    agent_token_mint_request = flyquery_sdk.AgentTokenMintRequest() # AgentTokenMintRequest | 

    try:
        # Mint a new agent token.
        api_response = await api_instance.mint(agent_token_mint_request)
        print("The response of AgentTokensApi->mint:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentTokensApi->mint: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **agent_token_mint_request** | [**AgentTokenMintRequest**](AgentTokenMintRequest.md)|  | 

### Return type

[**AgentTokenCreated**](AgentTokenCreated.md)

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

# **revoke**
> revoke(token_id)

Revoke a token. Idempotent -- already-revoked is a no-op (204).

Unknown ``token_id`` returns ``404 resource_not_found``.

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
    api_instance = flyquery_sdk.AgentTokensApi(api_client)
    token_id = 'token_id_example' # str | 

    try:
        # Revoke a token. Idempotent -- already-revoked is a no-op (204).
        await api_instance.revoke(token_id)
    except Exception as e:
        print("Exception when calling AgentTokensApi->revoke: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **token_id** | **str**|  | 

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

