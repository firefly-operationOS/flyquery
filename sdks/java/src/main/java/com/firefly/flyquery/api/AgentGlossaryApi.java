package com.firefly.flyquery.api;

import com.firefly.flyquery.ApiClient;

import com.firefly.flyquery.model.GlossaryTermCreate;
import com.firefly.flyquery.model.GlossaryTermRead;
import com.firefly.flyquery.model.GlossaryTermUpdate;
import com.firefly.flyquery.model.HTTPValidationError;
import com.firefly.flyquery.model.PaginatedGlossaryTermRead;
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

@jakarta.annotation.Generated(value = "org.openapitools.codegen.languages.JavaClientCodegen", date = "2026-06-01T11:28:27.907207+02:00[Europe/Madrid]", comments = "Generator version: 7.22.0")
public class AgentGlossaryApi {
    private ApiClient apiClient;

    public AgentGlossaryApi() {
        this(new ApiClient());
    }

    public AgentGlossaryApi(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    public ApiClient getApiClient() {
        return apiClient;
    }

    public void setApiClient(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    /**
     * Create a glossary term (agent-tier).
     * 
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param glossaryTermCreate The glossaryTermCreate parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return GlossaryTermRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec createRequestCreation(@jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nonnull GlossaryTermCreate glossaryTermCreate, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        Object postBody = glossaryTermCreate;
        // verify the required parameter 'xAgentToken' is set
        if (xAgentToken == null) {
            throw new WebClientResponseException("Missing the required parameter 'xAgentToken' when calling create", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'glossaryTermCreate' is set
        if (glossaryTermCreate == null) {
            throw new WebClientResponseException("Missing the required parameter 'glossaryTermCreate' when calling create", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
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

        ParameterizedTypeReference<GlossaryTermRead> localVarReturnType = new ParameterizedTypeReference<GlossaryTermRead>() {};
        return apiClient.invokeAPI("/api/v1/agent/glossary", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Create a glossary term (agent-tier).
     * 
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param glossaryTermCreate The glossaryTermCreate parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return GlossaryTermRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<GlossaryTermRead> create(@jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nonnull GlossaryTermCreate glossaryTermCreate, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<GlossaryTermRead> localVarReturnType = new ParameterizedTypeReference<GlossaryTermRead>() {};
        return createRequestCreation(xAgentToken, glossaryTermCreate, xCorrelationId, idempotencyKey).bodyToMono(localVarReturnType);
    }

    /**
     * Create a glossary term (agent-tier).
     * 
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param glossaryTermCreate The glossaryTermCreate parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseEntity&lt;GlossaryTermRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<GlossaryTermRead>> createWithHttpInfo(@jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nonnull GlossaryTermCreate glossaryTermCreate, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<GlossaryTermRead> localVarReturnType = new ParameterizedTypeReference<GlossaryTermRead>() {};
        return createRequestCreation(xAgentToken, glossaryTermCreate, xCorrelationId, idempotencyKey).toEntity(localVarReturnType);
    }

    /**
     * Create a glossary term (agent-tier).
     * 
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param glossaryTermCreate The glossaryTermCreate parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec createWithResponseSpec(@jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nonnull GlossaryTermCreate glossaryTermCreate, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        return createRequestCreation(xAgentToken, glossaryTermCreate, xCorrelationId, idempotencyKey);
    }

    /**
     * Hard-delete a glossary term (agent-tier).
     * 
     * <p><b>204</b> - No Content
     * @param termId The termId parameter
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec deleteRequestCreation(@jakarta.annotation.Nonnull String termId, @jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'termId' is set
        if (termId == null) {
            throw new WebClientResponseException("Missing the required parameter 'termId' when calling delete", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xAgentToken' is set
        if (xAgentToken == null) {
            throw new WebClientResponseException("Missing the required parameter 'xAgentToken' when calling delete", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("term_id", termId);

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
        final String[] localVarAccepts = { };
        final List<MediaType> localVarAccept = apiClient.selectHeaderAccept(localVarAccepts);
        final String[] localVarContentTypes = { };
        final MediaType localVarContentType = apiClient.selectHeaderContentType(localVarContentTypes);

        String[] localVarAuthNames = new String[] { "AgentToken" };

        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return apiClient.invokeAPI("/api/v1/agent/glossary/{term_id}", HttpMethod.DELETE, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Hard-delete a glossary term (agent-tier).
     * 
     * <p><b>204</b> - No Content
     * @param termId The termId parameter
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<Void> delete(@jakarta.annotation.Nonnull String termId, @jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return deleteRequestCreation(termId, xAgentToken, xCorrelationId, idempotencyKey).bodyToMono(localVarReturnType);
    }

    /**
     * Hard-delete a glossary term (agent-tier).
     * 
     * <p><b>204</b> - No Content
     * @param termId The termId parameter
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<Void>> deleteWithHttpInfo(@jakarta.annotation.Nonnull String termId, @jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return deleteRequestCreation(termId, xAgentToken, xCorrelationId, idempotencyKey).toEntity(localVarReturnType);
    }

    /**
     * Hard-delete a glossary term (agent-tier).
     * 
     * <p><b>204</b> - No Content
     * @param termId The termId parameter
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec deleteWithResponseSpec(@jakarta.annotation.Nonnull String termId, @jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        return deleteRequestCreation(termId, xAgentToken, xCorrelationId, idempotencyKey);
    }

    /**
     * Fetch a single glossary term (agent-tier).
     * 
     * <p><b>200</b> - Successful response
     * @param termId The termId parameter
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return GlossaryTermRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec getTermRequestCreation(@jakarta.annotation.Nullable String termId, @jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'termId' is set
        if (termId == null) {
            throw new WebClientResponseException("Missing the required parameter 'termId' when calling getTerm", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xAgentToken' is set
        if (xAgentToken == null) {
            throw new WebClientResponseException("Missing the required parameter 'xAgentToken' when calling getTerm", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("term_id", termId);

        final MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<String, String>();
        final HttpHeaders headerParams = new HttpHeaders();
        final MultiValueMap<String, String> cookieParams = new LinkedMultiValueMap<String, String>();
        final MultiValueMap<String, Object> formParams = new LinkedMultiValueMap<String, Object>();

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

        ParameterizedTypeReference<GlossaryTermRead> localVarReturnType = new ParameterizedTypeReference<GlossaryTermRead>() {};
        return apiClient.invokeAPI("/api/v1/agent/glossary/{term_id}", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Fetch a single glossary term (agent-tier).
     * 
     * <p><b>200</b> - Successful response
     * @param termId The termId parameter
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return GlossaryTermRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<GlossaryTermRead> getTerm(@jakarta.annotation.Nullable String termId, @jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        ParameterizedTypeReference<GlossaryTermRead> localVarReturnType = new ParameterizedTypeReference<GlossaryTermRead>() {};
        return getTermRequestCreation(termId, xAgentToken, xCorrelationId).bodyToMono(localVarReturnType);
    }

    /**
     * Fetch a single glossary term (agent-tier).
     * 
     * <p><b>200</b> - Successful response
     * @param termId The termId parameter
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return ResponseEntity&lt;GlossaryTermRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<GlossaryTermRead>> getTermWithHttpInfo(@jakarta.annotation.Nullable String termId, @jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        ParameterizedTypeReference<GlossaryTermRead> localVarReturnType = new ParameterizedTypeReference<GlossaryTermRead>() {};
        return getTermRequestCreation(termId, xAgentToken, xCorrelationId).toEntity(localVarReturnType);
    }

    /**
     * Fetch a single glossary term (agent-tier).
     * 
     * <p><b>200</b> - Successful response
     * @param termId The termId parameter
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec getTermWithResponseSpec(@jakarta.annotation.Nullable String termId, @jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        return getTermRequestCreation(termId, xAgentToken, xCorrelationId);
    }

    /**
     * List glossary terms for the caller&#39;s workspace (agent-tier).
     * 
     * <p><b>200</b> - Successful response
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param limit The limit parameter
     * @param offset The offset parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return PaginatedGlossaryTermRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec listTermsRequestCreation(@jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable Integer limit, @jakarta.annotation.Nullable Integer offset, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'xAgentToken' is set
        if (xAgentToken == null) {
            throw new WebClientResponseException("Missing the required parameter 'xAgentToken' when calling listTerms", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        final MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<String, String>();
        final HttpHeaders headerParams = new HttpHeaders();
        final MultiValueMap<String, String> cookieParams = new LinkedMultiValueMap<String, String>();
        final MultiValueMap<String, Object> formParams = new LinkedMultiValueMap<String, Object>();

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

        ParameterizedTypeReference<PaginatedGlossaryTermRead> localVarReturnType = new ParameterizedTypeReference<PaginatedGlossaryTermRead>() {};
        return apiClient.invokeAPI("/api/v1/agent/glossary", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * List glossary terms for the caller&#39;s workspace (agent-tier).
     * 
     * <p><b>200</b> - Successful response
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param limit The limit parameter
     * @param offset The offset parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return PaginatedGlossaryTermRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<PaginatedGlossaryTermRead> listTerms(@jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable Integer limit, @jakarta.annotation.Nullable Integer offset, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        ParameterizedTypeReference<PaginatedGlossaryTermRead> localVarReturnType = new ParameterizedTypeReference<PaginatedGlossaryTermRead>() {};
        return listTermsRequestCreation(xAgentToken, limit, offset, xCorrelationId).bodyToMono(localVarReturnType);
    }

    /**
     * List glossary terms for the caller&#39;s workspace (agent-tier).
     * 
     * <p><b>200</b> - Successful response
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param limit The limit parameter
     * @param offset The offset parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return ResponseEntity&lt;PaginatedGlossaryTermRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<PaginatedGlossaryTermRead>> listTermsWithHttpInfo(@jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable Integer limit, @jakarta.annotation.Nullable Integer offset, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        ParameterizedTypeReference<PaginatedGlossaryTermRead> localVarReturnType = new ParameterizedTypeReference<PaginatedGlossaryTermRead>() {};
        return listTermsRequestCreation(xAgentToken, limit, offset, xCorrelationId).toEntity(localVarReturnType);
    }

    /**
     * List glossary terms for the caller&#39;s workspace (agent-tier).
     * 
     * <p><b>200</b> - Successful response
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param limit The limit parameter
     * @param offset The offset parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec listTermsWithResponseSpec(@jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nullable Integer limit, @jakarta.annotation.Nullable Integer offset, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        return listTermsRequestCreation(xAgentToken, limit, offset, xCorrelationId);
    }

    /**
     * Sparse-update a glossary term (agent-tier).
     * 
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param termId The termId parameter
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param glossaryTermUpdate The glossaryTermUpdate parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return GlossaryTermRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec updateRequestCreation(@jakarta.annotation.Nonnull String termId, @jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nonnull GlossaryTermUpdate glossaryTermUpdate, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        Object postBody = glossaryTermUpdate;
        // verify the required parameter 'termId' is set
        if (termId == null) {
            throw new WebClientResponseException("Missing the required parameter 'termId' when calling update", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xAgentToken' is set
        if (xAgentToken == null) {
            throw new WebClientResponseException("Missing the required parameter 'xAgentToken' when calling update", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'glossaryTermUpdate' is set
        if (glossaryTermUpdate == null) {
            throw new WebClientResponseException("Missing the required parameter 'glossaryTermUpdate' when calling update", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("term_id", termId);

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

        ParameterizedTypeReference<GlossaryTermRead> localVarReturnType = new ParameterizedTypeReference<GlossaryTermRead>() {};
        return apiClient.invokeAPI("/api/v1/agent/glossary/{term_id}", HttpMethod.PUT, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Sparse-update a glossary term (agent-tier).
     * 
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param termId The termId parameter
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param glossaryTermUpdate The glossaryTermUpdate parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return GlossaryTermRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<GlossaryTermRead> update(@jakarta.annotation.Nonnull String termId, @jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nonnull GlossaryTermUpdate glossaryTermUpdate, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<GlossaryTermRead> localVarReturnType = new ParameterizedTypeReference<GlossaryTermRead>() {};
        return updateRequestCreation(termId, xAgentToken, glossaryTermUpdate, xCorrelationId, idempotencyKey).bodyToMono(localVarReturnType);
    }

    /**
     * Sparse-update a glossary term (agent-tier).
     * 
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param termId The termId parameter
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param glossaryTermUpdate The glossaryTermUpdate parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseEntity&lt;GlossaryTermRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<GlossaryTermRead>> updateWithHttpInfo(@jakarta.annotation.Nonnull String termId, @jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nonnull GlossaryTermUpdate glossaryTermUpdate, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<GlossaryTermRead> localVarReturnType = new ParameterizedTypeReference<GlossaryTermRead>() {};
        return updateRequestCreation(termId, xAgentToken, glossaryTermUpdate, xCorrelationId, idempotencyKey).toEntity(localVarReturnType);
    }

    /**
     * Sparse-update a glossary term (agent-tier).
     * 
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param termId The termId parameter
     * @param xAgentToken Machine-to-machine bearer token. Replaces X-Tenant-Id and X-Workspace-Id on agent-tier endpoints -- the token&#39;s claims encode the tenant + workspace + scopes. Issue via &#x60;&#x60;POST /api/v1/agent-tokens&#x60;&#x60;.
     * @param glossaryTermUpdate The glossaryTermUpdate parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec updateWithResponseSpec(@jakarta.annotation.Nonnull String termId, @jakarta.annotation.Nonnull String xAgentToken, @jakarta.annotation.Nonnull GlossaryTermUpdate glossaryTermUpdate, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        return updateRequestCreation(termId, xAgentToken, glossaryTermUpdate, xCorrelationId, idempotencyKey);
    }
}
