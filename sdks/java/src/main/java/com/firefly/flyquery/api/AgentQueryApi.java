package com.firefly.flyquery.api;

import com.firefly.flyquery.ApiClient;

import com.firefly.flyquery.model.AnswerResponse;
import com.firefly.flyquery.model.BatchQueryRequest;
import com.firefly.flyquery.model.BatchQueryResponse;
import com.firefly.flyquery.model.ExplainResponse;
import com.firefly.flyquery.model.HTTPValidationError;
import com.firefly.flyquery.model.QueryRequest;
import java.util.UUID;
import com.firefly.flyquery.model.ValidateResponse;

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

@jakarta.annotation.Generated(value = "org.openapitools.codegen.languages.JavaClientCodegen", date = "2026-05-24T14:41:07.623178+02:00[Europe/Madrid]", comments = "Generator version: 7.22.0")
public class AgentQueryApi {
    private ApiClient apiClient;

    public AgentQueryApi() {
        this(new ApiClient());
    }

    public AgentQueryApi(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    public ApiClient getApiClient() {
        return apiClient;
    }

    public void setApiClient(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    /**
     * Agent-tier mirror of POST /api/v1/query:batch.
     * Delegates to the user-tier &#x60;&#x60;QueryController.batch&#x60;&#x60; by instantiating it inline (same pattern as :meth:&#x60;stream&#x60;). Replay-dedup&#39;d via &#x60;&#x60;Idempotency-Key&#x60;&#x60; (required) -- a batch is N parallel multi-LLM pipelines, the costliest single request shape in the API.
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param batchQueryRequest The batchQueryRequest parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return BatchQueryResponse
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec batchRequestCreation(@jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nonnull BatchQueryRequest batchQueryRequest, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        Object postBody = batchQueryRequest;
        // verify the required parameter 'xAgentToken' is set
        if (xAgentToken == null) {
            throw new WebClientResponseException("Missing the required parameter 'xAgentToken' when calling batch", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'batchQueryRequest' is set
        if (batchQueryRequest == null) {
            throw new WebClientResponseException("Missing the required parameter 'batchQueryRequest' when calling batch", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        final MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<String, String>();
        final HttpHeaders headerParams = new HttpHeaders();
        final MultiValueMap<String, String> cookieParams = new LinkedMultiValueMap<String, String>();
        final MultiValueMap<String, Object> formParams = new LinkedMultiValueMap<String, Object>();

        if (xAgentToken != null)
        headerParams.add("X-Agent-Token", apiClient.parameterToString(xAgentToken));
        if (xCorrelationId != null)
        headerParams.add("X-Correlation-Id", apiClient.parameterToString(xCorrelationId));
        if (idempotencyKey != null)
        headerParams.add("Idempotency-Key", apiClient.parameterToString(idempotencyKey));
        final String[] localVarAccepts = { 
            "application/json"
        };
        final List<MediaType> localVarAccept = apiClient.selectHeaderAccept(localVarAccepts);
        final String[] localVarContentTypes = { 
            "application/json"
        };
        final MediaType localVarContentType = apiClient.selectHeaderContentType(localVarContentTypes);

        String[] localVarAuthNames = new String[] { "AgentToken" };

        ParameterizedTypeReference<BatchQueryResponse> localVarReturnType = new ParameterizedTypeReference<BatchQueryResponse>() {};
        return apiClient.invokeAPI("/api/v1/agent/query:batch", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Agent-tier mirror of POST /api/v1/query:batch.
     * Delegates to the user-tier &#x60;&#x60;QueryController.batch&#x60;&#x60; by instantiating it inline (same pattern as :meth:&#x60;stream&#x60;). Replay-dedup&#39;d via &#x60;&#x60;Idempotency-Key&#x60;&#x60; (required) -- a batch is N parallel multi-LLM pipelines, the costliest single request shape in the API.
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param batchQueryRequest The batchQueryRequest parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return BatchQueryResponse
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<BatchQueryResponse> batch(@jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nonnull BatchQueryRequest batchQueryRequest, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<BatchQueryResponse> localVarReturnType = new ParameterizedTypeReference<BatchQueryResponse>() {};
        return batchRequestCreation(xAgentToken, batchQueryRequest, xCorrelationId, idempotencyKey).bodyToMono(localVarReturnType);
    }

    /**
     * Agent-tier mirror of POST /api/v1/query:batch.
     * Delegates to the user-tier &#x60;&#x60;QueryController.batch&#x60;&#x60; by instantiating it inline (same pattern as :meth:&#x60;stream&#x60;). Replay-dedup&#39;d via &#x60;&#x60;Idempotency-Key&#x60;&#x60; (required) -- a batch is N parallel multi-LLM pipelines, the costliest single request shape in the API.
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param batchQueryRequest The batchQueryRequest parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseEntity&lt;BatchQueryResponse&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<BatchQueryResponse>> batchWithHttpInfo(@jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nonnull BatchQueryRequest batchQueryRequest, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<BatchQueryResponse> localVarReturnType = new ParameterizedTypeReference<BatchQueryResponse>() {};
        return batchRequestCreation(xAgentToken, batchQueryRequest, xCorrelationId, idempotencyKey).toEntity(localVarReturnType);
    }

    /**
     * Agent-tier mirror of POST /api/v1/query:batch.
     * Delegates to the user-tier &#x60;&#x60;QueryController.batch&#x60;&#x60; by instantiating it inline (same pattern as :meth:&#x60;stream&#x60;). Replay-dedup&#39;d via &#x60;&#x60;Idempotency-Key&#x60;&#x60; (required) -- a batch is N parallel multi-LLM pipelines, the costliest single request shape in the API.
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param batchQueryRequest The batchQueryRequest parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec batchWithResponseSpec(@jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nonnull BatchQueryRequest batchQueryRequest, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        return batchRequestCreation(xAgentToken, batchQueryRequest, xCorrelationId, idempotencyKey);
    }

    /**
     * Run Grounding + Generation only (agent-tier).
     * :param http_request: Starlette request :param body: validated QueryRequest :return: ExplainResponse with candidate SQL and reasoning
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param queryRequest The queryRequest parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ExplainResponse
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec explainRequestCreation(@jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nonnull QueryRequest queryRequest, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        Object postBody = queryRequest;
        // verify the required parameter 'xAgentToken' is set
        if (xAgentToken == null) {
            throw new WebClientResponseException("Missing the required parameter 'xAgentToken' when calling explain", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'queryRequest' is set
        if (queryRequest == null) {
            throw new WebClientResponseException("Missing the required parameter 'queryRequest' when calling explain", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        final MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<String, String>();
        final HttpHeaders headerParams = new HttpHeaders();
        final MultiValueMap<String, String> cookieParams = new LinkedMultiValueMap<String, String>();
        final MultiValueMap<String, Object> formParams = new LinkedMultiValueMap<String, Object>();

        if (xAgentToken != null)
        headerParams.add("X-Agent-Token", apiClient.parameterToString(xAgentToken));
        if (xCorrelationId != null)
        headerParams.add("X-Correlation-Id", apiClient.parameterToString(xCorrelationId));
        if (idempotencyKey != null)
        headerParams.add("Idempotency-Key", apiClient.parameterToString(idempotencyKey));
        final String[] localVarAccepts = { 
            "application/json"
        };
        final List<MediaType> localVarAccept = apiClient.selectHeaderAccept(localVarAccepts);
        final String[] localVarContentTypes = { 
            "application/json"
        };
        final MediaType localVarContentType = apiClient.selectHeaderContentType(localVarContentTypes);

        String[] localVarAuthNames = new String[] { "AgentToken" };

        ParameterizedTypeReference<ExplainResponse> localVarReturnType = new ParameterizedTypeReference<ExplainResponse>() {};
        return apiClient.invokeAPI("/api/v1/agent/query:explain", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Run Grounding + Generation only (agent-tier).
     * :param http_request: Starlette request :param body: validated QueryRequest :return: ExplainResponse with candidate SQL and reasoning
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param queryRequest The queryRequest parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ExplainResponse
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ExplainResponse> explain(@jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nonnull QueryRequest queryRequest, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<ExplainResponse> localVarReturnType = new ParameterizedTypeReference<ExplainResponse>() {};
        return explainRequestCreation(xAgentToken, queryRequest, xCorrelationId, idempotencyKey).bodyToMono(localVarReturnType);
    }

    /**
     * Run Grounding + Generation only (agent-tier).
     * :param http_request: Starlette request :param body: validated QueryRequest :return: ExplainResponse with candidate SQL and reasoning
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param queryRequest The queryRequest parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseEntity&lt;ExplainResponse&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<ExplainResponse>> explainWithHttpInfo(@jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nonnull QueryRequest queryRequest, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<ExplainResponse> localVarReturnType = new ParameterizedTypeReference<ExplainResponse>() {};
        return explainRequestCreation(xAgentToken, queryRequest, xCorrelationId, idempotencyKey).toEntity(localVarReturnType);
    }

    /**
     * Run Grounding + Generation only (agent-tier).
     * :param http_request: Starlette request :param body: validated QueryRequest :return: ExplainResponse with candidate SQL and reasoning
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param queryRequest The queryRequest parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec explainWithResponseSpec(@jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nonnull QueryRequest queryRequest, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        return explainRequestCreation(xAgentToken, queryRequest, xCorrelationId, idempotencyKey);
    }

    /**
     * Run the full NL → SQL → result pipeline (agent-tier).
     * Replay-dedup&#39;d via &#x60;&#x60;Idempotency-Key&#x60;&#x60;. The header is *required* on the agent surface so an at-least-once delivery agent (which retries on network error) doesn&#39;t burn budget by re-running the same multi-LLM pipeline twice.  :param http_request: Starlette request (provides tenant context + agent token) :param body: validated QueryRequest :return: AnswerResponse
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param queryRequest The queryRequest parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return AnswerResponse
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec queryRequestCreation(@jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nonnull QueryRequest queryRequest, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        Object postBody = queryRequest;
        // verify the required parameter 'xAgentToken' is set
        if (xAgentToken == null) {
            throw new WebClientResponseException("Missing the required parameter 'xAgentToken' when calling query", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'queryRequest' is set
        if (queryRequest == null) {
            throw new WebClientResponseException("Missing the required parameter 'queryRequest' when calling query", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        final MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<String, String>();
        final HttpHeaders headerParams = new HttpHeaders();
        final MultiValueMap<String, String> cookieParams = new LinkedMultiValueMap<String, String>();
        final MultiValueMap<String, Object> formParams = new LinkedMultiValueMap<String, Object>();

        if (xAgentToken != null)
        headerParams.add("X-Agent-Token", apiClient.parameterToString(xAgentToken));
        if (xCorrelationId != null)
        headerParams.add("X-Correlation-Id", apiClient.parameterToString(xCorrelationId));
        if (idempotencyKey != null)
        headerParams.add("Idempotency-Key", apiClient.parameterToString(idempotencyKey));
        final String[] localVarAccepts = { 
            "application/json"
        };
        final List<MediaType> localVarAccept = apiClient.selectHeaderAccept(localVarAccepts);
        final String[] localVarContentTypes = { 
            "application/json"
        };
        final MediaType localVarContentType = apiClient.selectHeaderContentType(localVarContentTypes);

        String[] localVarAuthNames = new String[] { "AgentToken" };

        ParameterizedTypeReference<AnswerResponse> localVarReturnType = new ParameterizedTypeReference<AnswerResponse>() {};
        return apiClient.invokeAPI("/api/v1/agent/query", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Run the full NL → SQL → result pipeline (agent-tier).
     * Replay-dedup&#39;d via &#x60;&#x60;Idempotency-Key&#x60;&#x60;. The header is *required* on the agent surface so an at-least-once delivery agent (which retries on network error) doesn&#39;t burn budget by re-running the same multi-LLM pipeline twice.  :param http_request: Starlette request (provides tenant context + agent token) :param body: validated QueryRequest :return: AnswerResponse
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param queryRequest The queryRequest parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return AnswerResponse
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<AnswerResponse> query(@jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nonnull QueryRequest queryRequest, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<AnswerResponse> localVarReturnType = new ParameterizedTypeReference<AnswerResponse>() {};
        return queryRequestCreation(xAgentToken, queryRequest, xCorrelationId, idempotencyKey).bodyToMono(localVarReturnType);
    }

    /**
     * Run the full NL → SQL → result pipeline (agent-tier).
     * Replay-dedup&#39;d via &#x60;&#x60;Idempotency-Key&#x60;&#x60;. The header is *required* on the agent surface so an at-least-once delivery agent (which retries on network error) doesn&#39;t burn budget by re-running the same multi-LLM pipeline twice.  :param http_request: Starlette request (provides tenant context + agent token) :param body: validated QueryRequest :return: AnswerResponse
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param queryRequest The queryRequest parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseEntity&lt;AnswerResponse&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<AnswerResponse>> queryWithHttpInfo(@jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nonnull QueryRequest queryRequest, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<AnswerResponse> localVarReturnType = new ParameterizedTypeReference<AnswerResponse>() {};
        return queryRequestCreation(xAgentToken, queryRequest, xCorrelationId, idempotencyKey).toEntity(localVarReturnType);
    }

    /**
     * Run the full NL → SQL → result pipeline (agent-tier).
     * Replay-dedup&#39;d via &#x60;&#x60;Idempotency-Key&#x60;&#x60;. The header is *required* on the agent surface so an at-least-once delivery agent (which retries on network error) doesn&#39;t burn budget by re-running the same multi-LLM pipeline twice.  :param http_request: Starlette request (provides tenant context + agent token) :param body: validated QueryRequest :return: AnswerResponse
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param queryRequest The queryRequest parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec queryWithResponseSpec(@jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nonnull QueryRequest queryRequest, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        return queryRequestCreation(xAgentToken, queryRequest, xCorrelationId, idempotencyKey);
    }

    /**
     * Run the pipeline as SSE stream (agent-tier).
     * :param http_request: Starlette request :param body: validated QueryRequest :return: StreamingResponse with text/event-stream
     * <p><b>200</b> - Server-Sent Events stream. Each frame follows the SSE wire format &#x60;&#x60;event: &lt;name&gt;\\ndata: &lt;json&gt;\\n\\n&#x60;&#x60;. See &#x60;&#x60;docs/api-reference.md&#x60;&#x60; section 8 for the per-endpoint event catalogue.
     * <p><b>422</b> - Validation Error
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param queryRequest The queryRequest parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return String
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec streamRequestCreation(@jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nonnull QueryRequest queryRequest, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        Object postBody = queryRequest;
        // verify the required parameter 'xAgentToken' is set
        if (xAgentToken == null) {
            throw new WebClientResponseException("Missing the required parameter 'xAgentToken' when calling stream", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'queryRequest' is set
        if (queryRequest == null) {
            throw new WebClientResponseException("Missing the required parameter 'queryRequest' when calling stream", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        final MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<String, String>();
        final HttpHeaders headerParams = new HttpHeaders();
        final MultiValueMap<String, String> cookieParams = new LinkedMultiValueMap<String, String>();
        final MultiValueMap<String, Object> formParams = new LinkedMultiValueMap<String, Object>();

        if (xAgentToken != null)
        headerParams.add("X-Agent-Token", apiClient.parameterToString(xAgentToken));
        if (xCorrelationId != null)
        headerParams.add("X-Correlation-Id", apiClient.parameterToString(xCorrelationId));
        if (idempotencyKey != null)
        headerParams.add("Idempotency-Key", apiClient.parameterToString(idempotencyKey));
        final String[] localVarAccepts = { 
            "text/event-stream", "application/json"
        };
        final List<MediaType> localVarAccept = apiClient.selectHeaderAccept(localVarAccepts);
        final String[] localVarContentTypes = { 
            "application/json"
        };
        final MediaType localVarContentType = apiClient.selectHeaderContentType(localVarContentTypes);

        String[] localVarAuthNames = new String[] { "AgentToken" };

        ParameterizedTypeReference<String> localVarReturnType = new ParameterizedTypeReference<String>() {};
        return apiClient.invokeAPI("/api/v1/agent/query/stream", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Run the pipeline as SSE stream (agent-tier).
     * :param http_request: Starlette request :param body: validated QueryRequest :return: StreamingResponse with text/event-stream
     * <p><b>200</b> - Server-Sent Events stream. Each frame follows the SSE wire format &#x60;&#x60;event: &lt;name&gt;\\ndata: &lt;json&gt;\\n\\n&#x60;&#x60;. See &#x60;&#x60;docs/api-reference.md&#x60;&#x60; section 8 for the per-endpoint event catalogue.
     * <p><b>422</b> - Validation Error
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param queryRequest The queryRequest parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return String
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<String> stream(@jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nonnull QueryRequest queryRequest, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<String> localVarReturnType = new ParameterizedTypeReference<String>() {};
        return streamRequestCreation(xAgentToken, queryRequest, xCorrelationId, idempotencyKey).bodyToMono(localVarReturnType);
    }

    /**
     * Run the pipeline as SSE stream (agent-tier).
     * :param http_request: Starlette request :param body: validated QueryRequest :return: StreamingResponse with text/event-stream
     * <p><b>200</b> - Server-Sent Events stream. Each frame follows the SSE wire format &#x60;&#x60;event: &lt;name&gt;\\ndata: &lt;json&gt;\\n\\n&#x60;&#x60;. See &#x60;&#x60;docs/api-reference.md&#x60;&#x60; section 8 for the per-endpoint event catalogue.
     * <p><b>422</b> - Validation Error
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param queryRequest The queryRequest parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseEntity&lt;String&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<String>> streamWithHttpInfo(@jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nonnull QueryRequest queryRequest, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<String> localVarReturnType = new ParameterizedTypeReference<String>() {};
        return streamRequestCreation(xAgentToken, queryRequest, xCorrelationId, idempotencyKey).toEntity(localVarReturnType);
    }

    /**
     * Run the pipeline as SSE stream (agent-tier).
     * :param http_request: Starlette request :param body: validated QueryRequest :return: StreamingResponse with text/event-stream
     * <p><b>200</b> - Server-Sent Events stream. Each frame follows the SSE wire format &#x60;&#x60;event: &lt;name&gt;\\ndata: &lt;json&gt;\\n\\n&#x60;&#x60;. See &#x60;&#x60;docs/api-reference.md&#x60;&#x60; section 8 for the per-endpoint event catalogue.
     * <p><b>422</b> - Validation Error
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param queryRequest The queryRequest parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec streamWithResponseSpec(@jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nonnull QueryRequest queryRequest, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        return streamRequestCreation(xAgentToken, queryRequest, xCorrelationId, idempotencyKey);
    }

    /**
     * Run Grounding + Generation + AST + ScopeGuard (agent-tier).
     * :param http_request: Starlette request :param body: validated QueryRequest :return: ValidateResponse
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param queryRequest The queryRequest parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ValidateResponse
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec validateRequestCreation(@jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nonnull QueryRequest queryRequest, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        Object postBody = queryRequest;
        // verify the required parameter 'xAgentToken' is set
        if (xAgentToken == null) {
            throw new WebClientResponseException("Missing the required parameter 'xAgentToken' when calling validate", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'queryRequest' is set
        if (queryRequest == null) {
            throw new WebClientResponseException("Missing the required parameter 'queryRequest' when calling validate", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        final MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<String, String>();
        final HttpHeaders headerParams = new HttpHeaders();
        final MultiValueMap<String, String> cookieParams = new LinkedMultiValueMap<String, String>();
        final MultiValueMap<String, Object> formParams = new LinkedMultiValueMap<String, Object>();

        if (xAgentToken != null)
        headerParams.add("X-Agent-Token", apiClient.parameterToString(xAgentToken));
        if (xCorrelationId != null)
        headerParams.add("X-Correlation-Id", apiClient.parameterToString(xCorrelationId));
        if (idempotencyKey != null)
        headerParams.add("Idempotency-Key", apiClient.parameterToString(idempotencyKey));
        final String[] localVarAccepts = { 
            "application/json"
        };
        final List<MediaType> localVarAccept = apiClient.selectHeaderAccept(localVarAccepts);
        final String[] localVarContentTypes = { 
            "application/json"
        };
        final MediaType localVarContentType = apiClient.selectHeaderContentType(localVarContentTypes);

        String[] localVarAuthNames = new String[] { "AgentToken" };

        ParameterizedTypeReference<ValidateResponse> localVarReturnType = new ParameterizedTypeReference<ValidateResponse>() {};
        return apiClient.invokeAPI("/api/v1/agent/query:validate", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Run Grounding + Generation + AST + ScopeGuard (agent-tier).
     * :param http_request: Starlette request :param body: validated QueryRequest :return: ValidateResponse
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param queryRequest The queryRequest parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ValidateResponse
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ValidateResponse> validate(@jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nonnull QueryRequest queryRequest, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<ValidateResponse> localVarReturnType = new ParameterizedTypeReference<ValidateResponse>() {};
        return validateRequestCreation(xAgentToken, queryRequest, xCorrelationId, idempotencyKey).bodyToMono(localVarReturnType);
    }

    /**
     * Run Grounding + Generation + AST + ScopeGuard (agent-tier).
     * :param http_request: Starlette request :param body: validated QueryRequest :return: ValidateResponse
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param queryRequest The queryRequest parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseEntity&lt;ValidateResponse&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<ValidateResponse>> validateWithHttpInfo(@jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nonnull QueryRequest queryRequest, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<ValidateResponse> localVarReturnType = new ParameterizedTypeReference<ValidateResponse>() {};
        return validateRequestCreation(xAgentToken, queryRequest, xCorrelationId, idempotencyKey).toEntity(localVarReturnType);
    }

    /**
     * Run Grounding + Generation + AST + ScopeGuard (agent-tier).
     * :param http_request: Starlette request :param body: validated QueryRequest :return: ValidateResponse
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param queryRequest The queryRequest parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec validateWithResponseSpec(@jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nonnull QueryRequest queryRequest, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        return validateRequestCreation(xAgentToken, queryRequest, xCorrelationId, idempotencyKey);
    }
}
