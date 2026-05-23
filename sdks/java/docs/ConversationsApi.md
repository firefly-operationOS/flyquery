# ConversationsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**create**](ConversationsApi.md#create) | **POST** /api/v1/conversations | Create a new conversation. |
| [**listConversations**](ConversationsApi.md#listConversations) | **GET** /api/v1/conversations | List conversations for the caller&#39;s workspace, newest first. |
| [**postTurn**](ConversationsApi.md#postTurn) | **POST** /api/v1/conversations/{conversation_id}/turn | Ask a follow-up question inside an existing conversation. |
| [**read**](ConversationsApi.md#read) | **GET** /api/v1/conversations/{conversation_id} | Fetch a conversation with all its turns. |


<a id="create"></a>
# **create**
> ConversationRead create(conversationCreate)

Create a new conversation.

:param http_request: Starlette request (tenant context headers) :param body: optional title :return: the new ConversationRead (no turns yet)

### Example
```java
// Import classes:
import io.firefly.flyquery.ApiClient;
import io.firefly.flyquery.ApiException;
import io.firefly.flyquery.Configuration;
import io.firefly.flyquery.models.*;
import io.firefly.flyquery.api.ConversationsApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");

    ConversationsApi apiInstance = new ConversationsApi(defaultClient);
    ConversationCreate conversationCreate = new ConversationCreate(); // ConversationCreate | 
    try {
      ConversationRead result = apiInstance.create(conversationCreate);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling ConversationsApi#create");
      System.err.println("Status code: " + e.getCode());
      System.err.println("Reason: " + e.getResponseBody());
      System.err.println("Response headers: " + e.getResponseHeaders());
      e.printStackTrace();
    }
  }
}
```

### Parameters

| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **conversationCreate** | [**ConversationCreate**](ConversationCreate.md)|  | |

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
| **201** | Successful response |  -  |
| **422** | Validation Error |  -  |

<a id="listConversations"></a>
# **listConversations**
> listConversations()

List conversations for the caller&#39;s workspace, newest first.

:param http_request: Starlette request :return: &#x60;&#x60;{\&quot;items\&quot;: [...]}&#x60;&#x60;

### Example
```java
// Import classes:
import io.firefly.flyquery.ApiClient;
import io.firefly.flyquery.ApiException;
import io.firefly.flyquery.Configuration;
import io.firefly.flyquery.models.*;
import io.firefly.flyquery.api.ConversationsApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");

    ConversationsApi apiInstance = new ConversationsApi(defaultClient);
    try {
      apiInstance.listConversations();
    } catch (ApiException e) {
      System.err.println("Exception when calling ConversationsApi#listConversations");
      System.err.println("Status code: " + e.getCode());
      System.err.println("Reason: " + e.getResponseBody());
      System.err.println("Response headers: " + e.getResponseHeaders());
      e.printStackTrace();
    }
  }
}
```

### Parameters
This endpoint does not need any parameter.

### Return type

null (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful response |  -  |

<a id="postTurn"></a>
# **postTurn**
> AnswerResponse postTurn(conversationId, conversationTurnRequest)

Ask a follow-up question inside an existing conversation.

Loads the prior turn&#39;s &#x60;&#x60;executed_sql + table_qnames + snapshot_pins&#x60;&#x60; and passes them into the query pipeline as drill-down context.  :param http_request: Starlette request :param conversation_id: conversation UUID :param body: dataset_id + question :return: AnswerResponse from the full pipeline

### Example
```java
// Import classes:
import io.firefly.flyquery.ApiClient;
import io.firefly.flyquery.ApiException;
import io.firefly.flyquery.Configuration;
import io.firefly.flyquery.models.*;
import io.firefly.flyquery.api.ConversationsApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");

    ConversationsApi apiInstance = new ConversationsApi(defaultClient);
    String conversationId = "conversationId_example"; // String | 
    ConversationTurnRequest conversationTurnRequest = new ConversationTurnRequest(); // ConversationTurnRequest | 
    try {
      AnswerResponse result = apiInstance.postTurn(conversationId, conversationTurnRequest);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling ConversationsApi#postTurn");
      System.err.println("Status code: " + e.getCode());
      System.err.println("Reason: " + e.getResponseBody());
      System.err.println("Response headers: " + e.getResponseHeaders());
      e.printStackTrace();
    }
  }
}
```

### Parameters

| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **conversationId** | **String**|  | |
| **conversationTurnRequest** | [**ConversationTurnRequest**](ConversationTurnRequest.md)|  | |

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
| **200** | Successful response |  -  |
| **422** | Validation Error |  -  |

<a id="read"></a>
# **read**
> ConversationRead read(conversationId)

Fetch a conversation with all its turns.

:param conversation_id: conversation UUID :return: ConversationRead including turns list :raises ResourceNotFound: when conversation does not exist

### Example
```java
// Import classes:
import io.firefly.flyquery.ApiClient;
import io.firefly.flyquery.ApiException;
import io.firefly.flyquery.Configuration;
import io.firefly.flyquery.models.*;
import io.firefly.flyquery.api.ConversationsApi;

public class Example {
  public static void main(String[] args) {
    ApiClient defaultClient = Configuration.getDefaultApiClient();
    defaultClient.setBasePath("http://localhost");

    ConversationsApi apiInstance = new ConversationsApi(defaultClient);
    String conversationId = "conversationId_example"; // String | 
    try {
      ConversationRead result = apiInstance.read(conversationId);
      System.out.println(result);
    } catch (ApiException e) {
      System.err.println("Exception when calling ConversationsApi#read");
      System.err.println("Status code: " + e.getCode());
      System.err.println("Reason: " + e.getResponseBody());
      System.err.println("Response headers: " + e.getResponseHeaders());
      e.printStackTrace();
    }
  }
}
```

### Parameters

| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **conversationId** | **String**|  | |

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
| **200** | Successful response |  -  |

