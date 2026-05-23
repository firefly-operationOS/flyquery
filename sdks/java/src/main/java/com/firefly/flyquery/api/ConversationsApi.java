package com.firefly.flyquery.api;

import com.firefly.flyquery.ApiClient;

import com.firefly.flyquery.model.AnswerResponse;
import com.firefly.flyquery.model.ConversationCreate;
import com.firefly.flyquery.model.ConversationRead;
import com.firefly.flyquery.model.ConversationTurnRequest;
import com.firefly.flyquery.model.HTTPValidationError;

import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Objects;
import java.util.Arrays;
import java.util.stream.Collectors;

import org.springframework.core.io.FileSystemResource;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.reactive.function.client.WebClient.ResponseSpec;
import org.springframework.web.reactive.function.client.WebClientResponseException;
import reactor.core.publisher.Mono;
import reactor.core.publisher.Flux;

@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaClientCodegen", date = "2026-05-23T20:36:34.703085+02:00[Europe/Madrid]", comments = "Generator version: 7.22.0")
public class ConversationsApi {
    private ApiClient apiClient;

    public ConversationsApi() {
        this(new ApiClient());
    }

    public ConversationsApi(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    public ApiClient getApiClient() {
        return apiClient;
    }

    public void setApiClient(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    /**
     * Create a new conversation.
     * :param http_request: Starlette request (tenant context headers) :param body: optional title :return: the new ConversationRead (no turns yet)
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param conversationCreate The conversationCreate parameter
     * @return ConversationRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec createRequestCreation(@javax.annotation.Nonnull ConversationCreate conversationCreate) throws WebClientResponseException {
        Object postBody = conversationCreate;
        // verify the required parameter 'conversationCreate' is set
        if (conversationCreate == null) {
            throw new WebClientResponseException("Missing the required parameter 'conversationCreate' when calling create", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        final MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<String, String>();
        final HttpHeaders headerParams = new HttpHeaders();
        final MultiValueMap<String, String> cookieParams = new LinkedMultiValueMap<String, String>();
        final MultiValueMap<String, Object> formParams = new LinkedMultiValueMap<String, Object>();

        final String[] localVarAccepts = { 
            "application/json"
        };
        final List<MediaType> localVarAccept = apiClient.selectHeaderAccept(localVarAccepts);
        final String[] localVarContentTypes = { 
            "application/json"
        };
        final MediaType localVarContentType = apiClient.selectHeaderContentType(localVarContentTypes);

        String[] localVarAuthNames = new String[] {  };

        ParameterizedTypeReference<ConversationRead> localVarReturnType = new ParameterizedTypeReference<ConversationRead>() {};
        return apiClient.invokeAPI("/api/v1/conversations", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Create a new conversation.
     * :param http_request: Starlette request (tenant context headers) :param body: optional title :return: the new ConversationRead (no turns yet)
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param conversationCreate The conversationCreate parameter
     * @return ConversationRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ConversationRead> create(@javax.annotation.Nonnull ConversationCreate conversationCreate) throws WebClientResponseException {
        ParameterizedTypeReference<ConversationRead> localVarReturnType = new ParameterizedTypeReference<ConversationRead>() {};
        return createRequestCreation(conversationCreate).bodyToMono(localVarReturnType);
    }

    /**
     * Create a new conversation.
     * :param http_request: Starlette request (tenant context headers) :param body: optional title :return: the new ConversationRead (no turns yet)
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param conversationCreate The conversationCreate parameter
     * @return ResponseEntity&lt;ConversationRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<ConversationRead>> createWithHttpInfo(@javax.annotation.Nonnull ConversationCreate conversationCreate) throws WebClientResponseException {
        ParameterizedTypeReference<ConversationRead> localVarReturnType = new ParameterizedTypeReference<ConversationRead>() {};
        return createRequestCreation(conversationCreate).toEntity(localVarReturnType);
    }

    /**
     * Create a new conversation.
     * :param http_request: Starlette request (tenant context headers) :param body: optional title :return: the new ConversationRead (no turns yet)
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param conversationCreate The conversationCreate parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec createWithResponseSpec(@javax.annotation.Nonnull ConversationCreate conversationCreate) throws WebClientResponseException {
        return createRequestCreation(conversationCreate);
    }

    /**
     * List conversations for the caller&#39;s workspace, newest first.
     * :param http_request: Starlette request :return: &#x60;&#x60;{\&quot;items\&quot;: [...]}&#x60;&#x60;
     * <p><b>200</b> - Successful response
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec listConversationsRequestCreation() throws WebClientResponseException {
        Object postBody = null;
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        final MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<String, String>();
        final HttpHeaders headerParams = new HttpHeaders();
        final MultiValueMap<String, String> cookieParams = new LinkedMultiValueMap<String, String>();
        final MultiValueMap<String, Object> formParams = new LinkedMultiValueMap<String, Object>();

        final String[] localVarAccepts = { };
        final List<MediaType> localVarAccept = apiClient.selectHeaderAccept(localVarAccepts);
        final String[] localVarContentTypes = { };
        final MediaType localVarContentType = apiClient.selectHeaderContentType(localVarContentTypes);

        String[] localVarAuthNames = new String[] {  };

        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return apiClient.invokeAPI("/api/v1/conversations", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * List conversations for the caller&#39;s workspace, newest first.
     * :param http_request: Starlette request :return: &#x60;&#x60;{\&quot;items\&quot;: [...]}&#x60;&#x60;
     * <p><b>200</b> - Successful response
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<Void> listConversations() throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return listConversationsRequestCreation().bodyToMono(localVarReturnType);
    }

    /**
     * List conversations for the caller&#39;s workspace, newest first.
     * :param http_request: Starlette request :return: &#x60;&#x60;{\&quot;items\&quot;: [...]}&#x60;&#x60;
     * <p><b>200</b> - Successful response
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<Void>> listConversationsWithHttpInfo() throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return listConversationsRequestCreation().toEntity(localVarReturnType);
    }

    /**
     * List conversations for the caller&#39;s workspace, newest first.
     * :param http_request: Starlette request :return: &#x60;&#x60;{\&quot;items\&quot;: [...]}&#x60;&#x60;
     * <p><b>200</b> - Successful response
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec listConversationsWithResponseSpec() throws WebClientResponseException {
        return listConversationsRequestCreation();
    }

    /**
     * Ask a follow-up question inside an existing conversation.
     * Loads the prior turn&#39;s &#x60;&#x60;executed_sql + table_qnames + snapshot_pins&#x60;&#x60; and passes them into the query pipeline as drill-down context.  :param http_request: Starlette request :param conversation_id: conversation UUID :param body: dataset_id + question :return: AnswerResponse from the full pipeline
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param conversationId The conversationId parameter
     * @param conversationTurnRequest The conversationTurnRequest parameter
     * @return AnswerResponse
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec postTurnRequestCreation(@javax.annotation.Nonnull String conversationId, @javax.annotation.Nonnull ConversationTurnRequest conversationTurnRequest) throws WebClientResponseException {
        Object postBody = conversationTurnRequest;
        // verify the required parameter 'conversationId' is set
        if (conversationId == null) {
            throw new WebClientResponseException("Missing the required parameter 'conversationId' when calling postTurn", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'conversationTurnRequest' is set
        if (conversationTurnRequest == null) {
            throw new WebClientResponseException("Missing the required parameter 'conversationTurnRequest' when calling postTurn", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("conversation_id", conversationId);

        final MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<String, String>();
        final HttpHeaders headerParams = new HttpHeaders();
        final MultiValueMap<String, String> cookieParams = new LinkedMultiValueMap<String, String>();
        final MultiValueMap<String, Object> formParams = new LinkedMultiValueMap<String, Object>();

        final String[] localVarAccepts = { 
            "application/json"
        };
        final List<MediaType> localVarAccept = apiClient.selectHeaderAccept(localVarAccepts);
        final String[] localVarContentTypes = { 
            "application/json"
        };
        final MediaType localVarContentType = apiClient.selectHeaderContentType(localVarContentTypes);

        String[] localVarAuthNames = new String[] {  };

        ParameterizedTypeReference<AnswerResponse> localVarReturnType = new ParameterizedTypeReference<AnswerResponse>() {};
        return apiClient.invokeAPI("/api/v1/conversations/{conversation_id}/turn", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Ask a follow-up question inside an existing conversation.
     * Loads the prior turn&#39;s &#x60;&#x60;executed_sql + table_qnames + snapshot_pins&#x60;&#x60; and passes them into the query pipeline as drill-down context.  :param http_request: Starlette request :param conversation_id: conversation UUID :param body: dataset_id + question :return: AnswerResponse from the full pipeline
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param conversationId The conversationId parameter
     * @param conversationTurnRequest The conversationTurnRequest parameter
     * @return AnswerResponse
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<AnswerResponse> postTurn(@javax.annotation.Nonnull String conversationId, @javax.annotation.Nonnull ConversationTurnRequest conversationTurnRequest) throws WebClientResponseException {
        ParameterizedTypeReference<AnswerResponse> localVarReturnType = new ParameterizedTypeReference<AnswerResponse>() {};
        return postTurnRequestCreation(conversationId, conversationTurnRequest).bodyToMono(localVarReturnType);
    }

    /**
     * Ask a follow-up question inside an existing conversation.
     * Loads the prior turn&#39;s &#x60;&#x60;executed_sql + table_qnames + snapshot_pins&#x60;&#x60; and passes them into the query pipeline as drill-down context.  :param http_request: Starlette request :param conversation_id: conversation UUID :param body: dataset_id + question :return: AnswerResponse from the full pipeline
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param conversationId The conversationId parameter
     * @param conversationTurnRequest The conversationTurnRequest parameter
     * @return ResponseEntity&lt;AnswerResponse&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<AnswerResponse>> postTurnWithHttpInfo(@javax.annotation.Nonnull String conversationId, @javax.annotation.Nonnull ConversationTurnRequest conversationTurnRequest) throws WebClientResponseException {
        ParameterizedTypeReference<AnswerResponse> localVarReturnType = new ParameterizedTypeReference<AnswerResponse>() {};
        return postTurnRequestCreation(conversationId, conversationTurnRequest).toEntity(localVarReturnType);
    }

    /**
     * Ask a follow-up question inside an existing conversation.
     * Loads the prior turn&#39;s &#x60;&#x60;executed_sql + table_qnames + snapshot_pins&#x60;&#x60; and passes them into the query pipeline as drill-down context.  :param http_request: Starlette request :param conversation_id: conversation UUID :param body: dataset_id + question :return: AnswerResponse from the full pipeline
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param conversationId The conversationId parameter
     * @param conversationTurnRequest The conversationTurnRequest parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec postTurnWithResponseSpec(@javax.annotation.Nonnull String conversationId, @javax.annotation.Nonnull ConversationTurnRequest conversationTurnRequest) throws WebClientResponseException {
        return postTurnRequestCreation(conversationId, conversationTurnRequest);
    }

    /**
     * Fetch a conversation with all its turns.
     * :param conversation_id: conversation UUID :return: ConversationRead including turns list :raises ResourceNotFound: when conversation does not exist
     * <p><b>200</b> - Successful response
     * @param conversationId The conversationId parameter
     * @return ConversationRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec readRequestCreation(@javax.annotation.Nullable String conversationId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'conversationId' is set
        if (conversationId == null) {
            throw new WebClientResponseException("Missing the required parameter 'conversationId' when calling read", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("conversation_id", conversationId);

        final MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<String, String>();
        final HttpHeaders headerParams = new HttpHeaders();
        final MultiValueMap<String, String> cookieParams = new LinkedMultiValueMap<String, String>();
        final MultiValueMap<String, Object> formParams = new LinkedMultiValueMap<String, Object>();

        final String[] localVarAccepts = { 
            "application/json"
        };
        final List<MediaType> localVarAccept = apiClient.selectHeaderAccept(localVarAccepts);
        final String[] localVarContentTypes = { };
        final MediaType localVarContentType = apiClient.selectHeaderContentType(localVarContentTypes);

        String[] localVarAuthNames = new String[] {  };

        ParameterizedTypeReference<ConversationRead> localVarReturnType = new ParameterizedTypeReference<ConversationRead>() {};
        return apiClient.invokeAPI("/api/v1/conversations/{conversation_id}", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Fetch a conversation with all its turns.
     * :param conversation_id: conversation UUID :return: ConversationRead including turns list :raises ResourceNotFound: when conversation does not exist
     * <p><b>200</b> - Successful response
     * @param conversationId The conversationId parameter
     * @return ConversationRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ConversationRead> read(@javax.annotation.Nullable String conversationId) throws WebClientResponseException {
        ParameterizedTypeReference<ConversationRead> localVarReturnType = new ParameterizedTypeReference<ConversationRead>() {};
        return readRequestCreation(conversationId).bodyToMono(localVarReturnType);
    }

    /**
     * Fetch a conversation with all its turns.
     * :param conversation_id: conversation UUID :return: ConversationRead including turns list :raises ResourceNotFound: when conversation does not exist
     * <p><b>200</b> - Successful response
     * @param conversationId The conversationId parameter
     * @return ResponseEntity&lt;ConversationRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<ConversationRead>> readWithHttpInfo(@javax.annotation.Nullable String conversationId) throws WebClientResponseException {
        ParameterizedTypeReference<ConversationRead> localVarReturnType = new ParameterizedTypeReference<ConversationRead>() {};
        return readRequestCreation(conversationId).toEntity(localVarReturnType);
    }

    /**
     * Fetch a conversation with all its turns.
     * :param conversation_id: conversation UUID :return: ConversationRead including turns list :raises ResourceNotFound: when conversation does not exist
     * <p><b>200</b> - Successful response
     * @param conversationId The conversationId parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec readWithResponseSpec(@javax.annotation.Nullable String conversationId) throws WebClientResponseException {
        return readRequestCreation(conversationId);
    }
}
