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
public class GlossaryApi {
    private ApiClient apiClient;

    public GlossaryApi() {
        this(new ApiClient());
    }

    public GlossaryApi(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    public ApiClient getApiClient() {
        return apiClient;
    }

    public void setApiClient(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    /**
     * Create a glossary term; (workspace_id, term) must be unique.
     * 
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param glossaryTermCreate The glossaryTermCreate parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return GlossaryTermRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec createRequestCreation(@jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nonnull GlossaryTermCreate glossaryTermCreate, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        Object postBody = glossaryTermCreate;
        // verify the required parameter 'xTenantId' is set
        if (xTenantId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xTenantId' when calling create", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xWorkspaceId' is set
        if (xWorkspaceId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xWorkspaceId' when calling create", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
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

        if (xTenantId != null)
        headerParams.add("X-Tenant-Id", apiClient.parameterToString(xTenantId));
        if (xWorkspaceId != null)
        headerParams.add("X-Workspace-Id", apiClient.parameterToString(xWorkspaceId));
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

        String[] localVarAuthNames = new String[] { "WorkspaceContext", "TenantContext" };

        ParameterizedTypeReference<GlossaryTermRead> localVarReturnType = new ParameterizedTypeReference<GlossaryTermRead>() {};
        return apiClient.invokeAPI("/api/v1/glossary", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Create a glossary term; (workspace_id, term) must be unique.
     * 
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param glossaryTermCreate The glossaryTermCreate parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return GlossaryTermRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<GlossaryTermRead> create(@jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nonnull GlossaryTermCreate glossaryTermCreate, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<GlossaryTermRead> localVarReturnType = new ParameterizedTypeReference<GlossaryTermRead>() {};
        return createRequestCreation(xTenantId, xWorkspaceId, glossaryTermCreate, xCorrelationId, idempotencyKey).bodyToMono(localVarReturnType);
    }

    /**
     * Create a glossary term; (workspace_id, term) must be unique.
     * 
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param glossaryTermCreate The glossaryTermCreate parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseEntity&lt;GlossaryTermRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<GlossaryTermRead>> createWithHttpInfo(@jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nonnull GlossaryTermCreate glossaryTermCreate, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<GlossaryTermRead> localVarReturnType = new ParameterizedTypeReference<GlossaryTermRead>() {};
        return createRequestCreation(xTenantId, xWorkspaceId, glossaryTermCreate, xCorrelationId, idempotencyKey).toEntity(localVarReturnType);
    }

    /**
     * Create a glossary term; (workspace_id, term) must be unique.
     * 
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param glossaryTermCreate The glossaryTermCreate parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec createWithResponseSpec(@jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nonnull GlossaryTermCreate glossaryTermCreate, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        return createRequestCreation(xTenantId, xWorkspaceId, glossaryTermCreate, xCorrelationId, idempotencyKey);
    }

    /**
     * Hard-delete a glossary term.
     * 
     * <p><b>204</b> - No Content
     * @param termId The termId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec deleteRequestCreation(@jakarta.annotation.Nonnull String termId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'termId' is set
        if (termId == null) {
            throw new WebClientResponseException("Missing the required parameter 'termId' when calling delete", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xTenantId' is set
        if (xTenantId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xTenantId' when calling delete", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xWorkspaceId' is set
        if (xWorkspaceId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xWorkspaceId' when calling delete", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("term_id", termId);

        final MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<String, String>();
        final HttpHeaders headerParams = new HttpHeaders();
        final MultiValueMap<String, String> cookieParams = new LinkedMultiValueMap<String, String>();
        final MultiValueMap<String, Object> formParams = new LinkedMultiValueMap<String, Object>();

        if (xTenantId != null)
        headerParams.add("X-Tenant-Id", apiClient.parameterToString(xTenantId));
        if (xWorkspaceId != null)
        headerParams.add("X-Workspace-Id", apiClient.parameterToString(xWorkspaceId));
        if (xCorrelationId != null)
        headerParams.add("X-Correlation-Id", apiClient.parameterToString(xCorrelationId));
        if (idempotencyKey != null)
        headerParams.add("Idempotency-Key", apiClient.parameterToString(idempotencyKey));
        final String[] localVarAccepts = { };
        final List<MediaType> localVarAccept = apiClient.selectHeaderAccept(localVarAccepts);
        final String[] localVarContentTypes = { };
        final MediaType localVarContentType = apiClient.selectHeaderContentType(localVarContentTypes);

        String[] localVarAuthNames = new String[] { "WorkspaceContext", "TenantContext" };

        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return apiClient.invokeAPI("/api/v1/glossary/{term_id}", HttpMethod.DELETE, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Hard-delete a glossary term.
     * 
     * <p><b>204</b> - No Content
     * @param termId The termId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<Void> delete(@jakarta.annotation.Nonnull String termId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return deleteRequestCreation(termId, xTenantId, xWorkspaceId, xCorrelationId, idempotencyKey).bodyToMono(localVarReturnType);
    }

    /**
     * Hard-delete a glossary term.
     * 
     * <p><b>204</b> - No Content
     * @param termId The termId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<Void>> deleteWithHttpInfo(@jakarta.annotation.Nonnull String termId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return deleteRequestCreation(termId, xTenantId, xWorkspaceId, xCorrelationId, idempotencyKey).toEntity(localVarReturnType);
    }

    /**
     * Hard-delete a glossary term.
     * 
     * <p><b>204</b> - No Content
     * @param termId The termId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec deleteWithResponseSpec(@jakarta.annotation.Nonnull String termId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        return deleteRequestCreation(termId, xTenantId, xWorkspaceId, xCorrelationId, idempotencyKey);
    }

    /**
     * Fetch a single glossary term by id. Returns 404 if not found.
     * 
     * <p><b>200</b> - Successful response
     * @param termId The termId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return GlossaryTermRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec getTermRequestCreation(@jakarta.annotation.Nonnull String termId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'termId' is set
        if (termId == null) {
            throw new WebClientResponseException("Missing the required parameter 'termId' when calling getTerm", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xTenantId' is set
        if (xTenantId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xTenantId' when calling getTerm", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xWorkspaceId' is set
        if (xWorkspaceId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xWorkspaceId' when calling getTerm", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("term_id", termId);

        final MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<String, String>();
        final HttpHeaders headerParams = new HttpHeaders();
        final MultiValueMap<String, String> cookieParams = new LinkedMultiValueMap<String, String>();
        final MultiValueMap<String, Object> formParams = new LinkedMultiValueMap<String, Object>();

        if (xTenantId != null)
        headerParams.add("X-Tenant-Id", apiClient.parameterToString(xTenantId));
        if (xWorkspaceId != null)
        headerParams.add("X-Workspace-Id", apiClient.parameterToString(xWorkspaceId));
        if (xCorrelationId != null)
        headerParams.add("X-Correlation-Id", apiClient.parameterToString(xCorrelationId));
        final String[] localVarAccepts = { 
            "application/json"
        };
        final List<MediaType> localVarAccept = apiClient.selectHeaderAccept(localVarAccepts);
        final String[] localVarContentTypes = { };
        final MediaType localVarContentType = apiClient.selectHeaderContentType(localVarContentTypes);

        String[] localVarAuthNames = new String[] { "WorkspaceContext", "TenantContext" };

        ParameterizedTypeReference<GlossaryTermRead> localVarReturnType = new ParameterizedTypeReference<GlossaryTermRead>() {};
        return apiClient.invokeAPI("/api/v1/glossary/{term_id}", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Fetch a single glossary term by id. Returns 404 if not found.
     * 
     * <p><b>200</b> - Successful response
     * @param termId The termId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return GlossaryTermRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<GlossaryTermRead> getTerm(@jakarta.annotation.Nonnull String termId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        ParameterizedTypeReference<GlossaryTermRead> localVarReturnType = new ParameterizedTypeReference<GlossaryTermRead>() {};
        return getTermRequestCreation(termId, xTenantId, xWorkspaceId, xCorrelationId).bodyToMono(localVarReturnType);
    }

    /**
     * Fetch a single glossary term by id. Returns 404 if not found.
     * 
     * <p><b>200</b> - Successful response
     * @param termId The termId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return ResponseEntity&lt;GlossaryTermRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<GlossaryTermRead>> getTermWithHttpInfo(@jakarta.annotation.Nonnull String termId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        ParameterizedTypeReference<GlossaryTermRead> localVarReturnType = new ParameterizedTypeReference<GlossaryTermRead>() {};
        return getTermRequestCreation(termId, xTenantId, xWorkspaceId, xCorrelationId).toEntity(localVarReturnType);
    }

    /**
     * Fetch a single glossary term by id. Returns 404 if not found.
     * 
     * <p><b>200</b> - Successful response
     * @param termId The termId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec getTermWithResponseSpec(@jakarta.annotation.Nonnull String termId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        return getTermRequestCreation(termId, xTenantId, xWorkspaceId, xCorrelationId);
    }

    /**
     * Return paginated glossary terms for the caller&#39;s workspace.
     * &#x60;&#x60;total&#x60;&#x60; is not populated -- the underlying service does not compute a COUNT(*); consumers use &#x60;&#x60;has_more&#x60;&#x60; to decide whether to fetch another page.
     * <p><b>200</b> - Successful response
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param limit The limit parameter
     * @param offset The offset parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return PaginatedGlossaryTermRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec listTermsRequestCreation(@jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable Integer limit, @jakarta.annotation.Nullable Integer offset, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'xTenantId' is set
        if (xTenantId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xTenantId' when calling listTerms", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xWorkspaceId' is set
        if (xWorkspaceId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xWorkspaceId' when calling listTerms", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        final MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<String, String>();
        final HttpHeaders headerParams = new HttpHeaders();
        final MultiValueMap<String, String> cookieParams = new LinkedMultiValueMap<String, String>();
        final MultiValueMap<String, Object> formParams = new LinkedMultiValueMap<String, Object>();

        queryParams.putAll(apiClient.parameterToMultiValueMap(null, "limit", limit));
        queryParams.putAll(apiClient.parameterToMultiValueMap(null, "offset", offset));

        if (xTenantId != null)
        headerParams.add("X-Tenant-Id", apiClient.parameterToString(xTenantId));
        if (xWorkspaceId != null)
        headerParams.add("X-Workspace-Id", apiClient.parameterToString(xWorkspaceId));
        if (xCorrelationId != null)
        headerParams.add("X-Correlation-Id", apiClient.parameterToString(xCorrelationId));
        final String[] localVarAccepts = { 
            "application/json"
        };
        final List<MediaType> localVarAccept = apiClient.selectHeaderAccept(localVarAccepts);
        final String[] localVarContentTypes = { };
        final MediaType localVarContentType = apiClient.selectHeaderContentType(localVarContentTypes);

        String[] localVarAuthNames = new String[] { "WorkspaceContext", "TenantContext" };

        ParameterizedTypeReference<PaginatedGlossaryTermRead> localVarReturnType = new ParameterizedTypeReference<PaginatedGlossaryTermRead>() {};
        return apiClient.invokeAPI("/api/v1/glossary", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Return paginated glossary terms for the caller&#39;s workspace.
     * &#x60;&#x60;total&#x60;&#x60; is not populated -- the underlying service does not compute a COUNT(*); consumers use &#x60;&#x60;has_more&#x60;&#x60; to decide whether to fetch another page.
     * <p><b>200</b> - Successful response
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param limit The limit parameter
     * @param offset The offset parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return PaginatedGlossaryTermRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<PaginatedGlossaryTermRead> listTerms(@jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable Integer limit, @jakarta.annotation.Nullable Integer offset, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        ParameterizedTypeReference<PaginatedGlossaryTermRead> localVarReturnType = new ParameterizedTypeReference<PaginatedGlossaryTermRead>() {};
        return listTermsRequestCreation(xTenantId, xWorkspaceId, limit, offset, xCorrelationId).bodyToMono(localVarReturnType);
    }

    /**
     * Return paginated glossary terms for the caller&#39;s workspace.
     * &#x60;&#x60;total&#x60;&#x60; is not populated -- the underlying service does not compute a COUNT(*); consumers use &#x60;&#x60;has_more&#x60;&#x60; to decide whether to fetch another page.
     * <p><b>200</b> - Successful response
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param limit The limit parameter
     * @param offset The offset parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return ResponseEntity&lt;PaginatedGlossaryTermRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<PaginatedGlossaryTermRead>> listTermsWithHttpInfo(@jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable Integer limit, @jakarta.annotation.Nullable Integer offset, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        ParameterizedTypeReference<PaginatedGlossaryTermRead> localVarReturnType = new ParameterizedTypeReference<PaginatedGlossaryTermRead>() {};
        return listTermsRequestCreation(xTenantId, xWorkspaceId, limit, offset, xCorrelationId).toEntity(localVarReturnType);
    }

    /**
     * Return paginated glossary terms for the caller&#39;s workspace.
     * &#x60;&#x60;total&#x60;&#x60; is not populated -- the underlying service does not compute a COUNT(*); consumers use &#x60;&#x60;has_more&#x60;&#x60; to decide whether to fetch another page.
     * <p><b>200</b> - Successful response
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param limit The limit parameter
     * @param offset The offset parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec listTermsWithResponseSpec(@jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable Integer limit, @jakarta.annotation.Nullable Integer offset, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        return listTermsRequestCreation(xTenantId, xWorkspaceId, limit, offset, xCorrelationId);
    }

    /**
     * Sparse-update a glossary term.
     * 
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param termId The termId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param glossaryTermUpdate The glossaryTermUpdate parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return GlossaryTermRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec updateRequestCreation(@jakarta.annotation.Nonnull String termId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nonnull GlossaryTermUpdate glossaryTermUpdate, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        Object postBody = glossaryTermUpdate;
        // verify the required parameter 'termId' is set
        if (termId == null) {
            throw new WebClientResponseException("Missing the required parameter 'termId' when calling update", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xTenantId' is set
        if (xTenantId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xTenantId' when calling update", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xWorkspaceId' is set
        if (xWorkspaceId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xWorkspaceId' when calling update", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
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

        if (xTenantId != null)
        headerParams.add("X-Tenant-Id", apiClient.parameterToString(xTenantId));
        if (xWorkspaceId != null)
        headerParams.add("X-Workspace-Id", apiClient.parameterToString(xWorkspaceId));
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

        String[] localVarAuthNames = new String[] { "WorkspaceContext", "TenantContext" };

        ParameterizedTypeReference<GlossaryTermRead> localVarReturnType = new ParameterizedTypeReference<GlossaryTermRead>() {};
        return apiClient.invokeAPI("/api/v1/glossary/{term_id}", HttpMethod.PUT, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Sparse-update a glossary term.
     * 
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param termId The termId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param glossaryTermUpdate The glossaryTermUpdate parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return GlossaryTermRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<GlossaryTermRead> update(@jakarta.annotation.Nonnull String termId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nonnull GlossaryTermUpdate glossaryTermUpdate, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<GlossaryTermRead> localVarReturnType = new ParameterizedTypeReference<GlossaryTermRead>() {};
        return updateRequestCreation(termId, xTenantId, xWorkspaceId, glossaryTermUpdate, xCorrelationId, idempotencyKey).bodyToMono(localVarReturnType);
    }

    /**
     * Sparse-update a glossary term.
     * 
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param termId The termId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param glossaryTermUpdate The glossaryTermUpdate parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseEntity&lt;GlossaryTermRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<GlossaryTermRead>> updateWithHttpInfo(@jakarta.annotation.Nonnull String termId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nonnull GlossaryTermUpdate glossaryTermUpdate, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<GlossaryTermRead> localVarReturnType = new ParameterizedTypeReference<GlossaryTermRead>() {};
        return updateRequestCreation(termId, xTenantId, xWorkspaceId, glossaryTermUpdate, xCorrelationId, idempotencyKey).toEntity(localVarReturnType);
    }

    /**
     * Sparse-update a glossary term.
     * 
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param termId The termId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param glossaryTermUpdate The glossaryTermUpdate parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec updateWithResponseSpec(@jakarta.annotation.Nonnull String termId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nonnull GlossaryTermUpdate glossaryTermUpdate, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        return updateRequestCreation(termId, xTenantId, xWorkspaceId, glossaryTermUpdate, xCorrelationId, idempotencyKey);
    }
}
