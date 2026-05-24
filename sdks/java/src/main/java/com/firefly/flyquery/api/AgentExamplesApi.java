package com.firefly.flyquery.api;

import com.firefly.flyquery.ApiClient;

import com.firefly.flyquery.model.ExampleCreate;
import com.firefly.flyquery.model.ExampleRead;
import com.firefly.flyquery.model.HTTPValidationError;
import com.firefly.flyquery.model.PaginatedExampleRead;
import java.util.UUID;

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
public class AgentExamplesApi {
    private ApiClient apiClient;

    public AgentExamplesApi() {
        this(new ApiClient());
    }

    public AgentExamplesApi(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    public ApiClient getApiClient() {
        return apiClient;
    }

    public void setApiClient(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    /**
     * Create an example (agent-tier — source&#x3D;AGENT_LEARNED, quality&#x3D;PROPOSED).
     * Replay-dedup&#39;d via &#x60;&#x60;Idempotency-Key&#x60;&#x60; (required). Without this gate an agent retrying a network blip would persist duplicate (question, SQL) PROPOSED rows that an operator would then have to manually reject.
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param exampleCreate The exampleCreate parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ExampleRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec createRequestCreation(@jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nonnull ExampleCreate exampleCreate, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        Object postBody = exampleCreate;
        // verify the required parameter 'xAgentToken' is set
        if (xAgentToken == null) {
            throw new WebClientResponseException("Missing the required parameter 'xAgentToken' when calling create", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'exampleCreate' is set
        if (exampleCreate == null) {
            throw new WebClientResponseException("Missing the required parameter 'exampleCreate' when calling create", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
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

        ParameterizedTypeReference<ExampleRead> localVarReturnType = new ParameterizedTypeReference<ExampleRead>() {};
        return apiClient.invokeAPI("/api/v1/agent/examples", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Create an example (agent-tier — source&#x3D;AGENT_LEARNED, quality&#x3D;PROPOSED).
     * Replay-dedup&#39;d via &#x60;&#x60;Idempotency-Key&#x60;&#x60; (required). Without this gate an agent retrying a network blip would persist duplicate (question, SQL) PROPOSED rows that an operator would then have to manually reject.
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param exampleCreate The exampleCreate parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ExampleRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ExampleRead> create(@jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nonnull ExampleCreate exampleCreate, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<ExampleRead> localVarReturnType = new ParameterizedTypeReference<ExampleRead>() {};
        return createRequestCreation(xAgentToken, exampleCreate, xCorrelationId, idempotencyKey).bodyToMono(localVarReturnType);
    }

    /**
     * Create an example (agent-tier — source&#x3D;AGENT_LEARNED, quality&#x3D;PROPOSED).
     * Replay-dedup&#39;d via &#x60;&#x60;Idempotency-Key&#x60;&#x60; (required). Without this gate an agent retrying a network blip would persist duplicate (question, SQL) PROPOSED rows that an operator would then have to manually reject.
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param exampleCreate The exampleCreate parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseEntity&lt;ExampleRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<ExampleRead>> createWithHttpInfo(@jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nonnull ExampleCreate exampleCreate, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<ExampleRead> localVarReturnType = new ParameterizedTypeReference<ExampleRead>() {};
        return createRequestCreation(xAgentToken, exampleCreate, xCorrelationId, idempotencyKey).toEntity(localVarReturnType);
    }

    /**
     * Create an example (agent-tier — source&#x3D;AGENT_LEARNED, quality&#x3D;PROPOSED).
     * Replay-dedup&#39;d via &#x60;&#x60;Idempotency-Key&#x60;&#x60; (required). Without this gate an agent retrying a network blip would persist duplicate (question, SQL) PROPOSED rows that an operator would then have to manually reject.
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param exampleCreate The exampleCreate parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec createWithResponseSpec(@jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nonnull ExampleCreate exampleCreate, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        return createRequestCreation(xAgentToken, exampleCreate, xCorrelationId, idempotencyKey);
    }

    /**
     * List examples for the caller&#39;s workspace (agent-tier).
     * :param http_request: Starlette request :param quality: optional quality filter (PROPOSED/APPROVED/REJECTED) :param dataset_id: optional dataset filter :param limit: page size (default 100) :param offset: starting offset (default 0) :return: Paginated[ExampleRead]
     * <p><b>200</b> - Successful response
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param quality The quality parameter
     * @param datasetId The datasetId parameter
     * @param limit The limit parameter
     * @param offset The offset parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return PaginatedExampleRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec listExamplesRequestCreation(@jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable String quality, @jakarta.annotation.Nullable String datasetId, @jakarta.annotation.Nullable Integer limit, @jakarta.annotation.Nullable Integer offset, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'xAgentToken' is set
        if (xAgentToken == null) {
            throw new WebClientResponseException("Missing the required parameter 'xAgentToken' when calling listExamples", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        final MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<String, String>();
        final HttpHeaders headerParams = new HttpHeaders();
        final MultiValueMap<String, String> cookieParams = new LinkedMultiValueMap<String, String>();
        final MultiValueMap<String, Object> formParams = new LinkedMultiValueMap<String, Object>();

        queryParams.putAll(apiClient.parameterToMultiValueMap(null, "quality", quality));
        queryParams.putAll(apiClient.parameterToMultiValueMap(null, "dataset_id", datasetId));
        queryParams.putAll(apiClient.parameterToMultiValueMap(null, "limit", limit));
        queryParams.putAll(apiClient.parameterToMultiValueMap(null, "offset", offset));

        if (xAgentToken != null)
        headerParams.add("X-Agent-Token", apiClient.parameterToString(xAgentToken));
        if (xCorrelationId != null)
        headerParams.add("X-Correlation-Id", apiClient.parameterToString(xCorrelationId));
        final String[] localVarAccepts = { 
            "application/json"
        };
        final List<MediaType> localVarAccept = apiClient.selectHeaderAccept(localVarAccepts);
        final String[] localVarContentTypes = { };
        final MediaType localVarContentType = apiClient.selectHeaderContentType(localVarContentTypes);

        String[] localVarAuthNames = new String[] { "AgentToken" };

        ParameterizedTypeReference<PaginatedExampleRead> localVarReturnType = new ParameterizedTypeReference<PaginatedExampleRead>() {};
        return apiClient.invokeAPI("/api/v1/agent/examples", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * List examples for the caller&#39;s workspace (agent-tier).
     * :param http_request: Starlette request :param quality: optional quality filter (PROPOSED/APPROVED/REJECTED) :param dataset_id: optional dataset filter :param limit: page size (default 100) :param offset: starting offset (default 0) :return: Paginated[ExampleRead]
     * <p><b>200</b> - Successful response
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param quality The quality parameter
     * @param datasetId The datasetId parameter
     * @param limit The limit parameter
     * @param offset The offset parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return PaginatedExampleRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<PaginatedExampleRead> listExamples(@jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable String quality, @jakarta.annotation.Nullable String datasetId, @jakarta.annotation.Nullable Integer limit, @jakarta.annotation.Nullable Integer offset, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        ParameterizedTypeReference<PaginatedExampleRead> localVarReturnType = new ParameterizedTypeReference<PaginatedExampleRead>() {};
        return listExamplesRequestCreation(xAgentToken, quality, datasetId, limit, offset, xCorrelationId).bodyToMono(localVarReturnType);
    }

    /**
     * List examples for the caller&#39;s workspace (agent-tier).
     * :param http_request: Starlette request :param quality: optional quality filter (PROPOSED/APPROVED/REJECTED) :param dataset_id: optional dataset filter :param limit: page size (default 100) :param offset: starting offset (default 0) :return: Paginated[ExampleRead]
     * <p><b>200</b> - Successful response
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param quality The quality parameter
     * @param datasetId The datasetId parameter
     * @param limit The limit parameter
     * @param offset The offset parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return ResponseEntity&lt;PaginatedExampleRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<PaginatedExampleRead>> listExamplesWithHttpInfo(@jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable String quality, @jakarta.annotation.Nullable String datasetId, @jakarta.annotation.Nullable Integer limit, @jakarta.annotation.Nullable Integer offset, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        ParameterizedTypeReference<PaginatedExampleRead> localVarReturnType = new ParameterizedTypeReference<PaginatedExampleRead>() {};
        return listExamplesRequestCreation(xAgentToken, quality, datasetId, limit, offset, xCorrelationId).toEntity(localVarReturnType);
    }

    /**
     * List examples for the caller&#39;s workspace (agent-tier).
     * :param http_request: Starlette request :param quality: optional quality filter (PROPOSED/APPROVED/REJECTED) :param dataset_id: optional dataset filter :param limit: page size (default 100) :param offset: starting offset (default 0) :return: Paginated[ExampleRead]
     * <p><b>200</b> - Successful response
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param quality The quality parameter
     * @param datasetId The datasetId parameter
     * @param limit The limit parameter
     * @param offset The offset parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec listExamplesWithResponseSpec(@jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable String quality, @jakarta.annotation.Nullable String datasetId, @jakarta.annotation.Nullable Integer limit, @jakarta.annotation.Nullable Integer offset, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        return listExamplesRequestCreation(xAgentToken, quality, datasetId, limit, offset, xCorrelationId);
    }
}
