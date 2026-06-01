package com.firefly.flyquery.api;

import com.firefly.flyquery.ApiClient;

import com.firefly.flyquery.model.HTTPValidationError;
import com.firefly.flyquery.model.PaginatedSemanticDimensionRead;
import com.firefly.flyquery.model.PaginatedSemanticVersionRead;
import com.firefly.flyquery.model.SemanticDimensionCreate;
import com.firefly.flyquery.model.SemanticDimensionRead;
import com.firefly.flyquery.model.SemanticDimensionUpdate;
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
public class SemanticDimensionsApi {
    private ApiClient apiClient;

    public SemanticDimensionsApi() {
        this(new ApiClient());
    }

    public SemanticDimensionsApi(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    public ApiClient getApiClient() {
        return apiClient;
    }

    public void setApiClient(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    /**
     * Create a new semantic dimension in DRAFT status.
     * 
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param semanticDimensionCreate The semanticDimensionCreate parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return SemanticDimensionRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec createRequestCreation(@jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nonnull SemanticDimensionCreate semanticDimensionCreate, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        Object postBody = semanticDimensionCreate;
        // verify the required parameter 'xTenantId' is set
        if (xTenantId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xTenantId' when calling create", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xWorkspaceId' is set
        if (xWorkspaceId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xWorkspaceId' when calling create", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'semanticDimensionCreate' is set
        if (semanticDimensionCreate == null) {
            throw new WebClientResponseException("Missing the required parameter 'semanticDimensionCreate' when calling create", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
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

        ParameterizedTypeReference<SemanticDimensionRead> localVarReturnType = new ParameterizedTypeReference<SemanticDimensionRead>() {};
        return apiClient.invokeAPI("/api/v1/semantic/dimensions", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Create a new semantic dimension in DRAFT status.
     * 
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param semanticDimensionCreate The semanticDimensionCreate parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return SemanticDimensionRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<SemanticDimensionRead> create(@jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nonnull SemanticDimensionCreate semanticDimensionCreate, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<SemanticDimensionRead> localVarReturnType = new ParameterizedTypeReference<SemanticDimensionRead>() {};
        return createRequestCreation(xTenantId, xWorkspaceId, semanticDimensionCreate, xCorrelationId, idempotencyKey).bodyToMono(localVarReturnType);
    }

    /**
     * Create a new semantic dimension in DRAFT status.
     * 
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param semanticDimensionCreate The semanticDimensionCreate parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseEntity&lt;SemanticDimensionRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<SemanticDimensionRead>> createWithHttpInfo(@jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nonnull SemanticDimensionCreate semanticDimensionCreate, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<SemanticDimensionRead> localVarReturnType = new ParameterizedTypeReference<SemanticDimensionRead>() {};
        return createRequestCreation(xTenantId, xWorkspaceId, semanticDimensionCreate, xCorrelationId, idempotencyKey).toEntity(localVarReturnType);
    }

    /**
     * Create a new semantic dimension in DRAFT status.
     * 
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param semanticDimensionCreate The semanticDimensionCreate parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec createWithResponseSpec(@jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nonnull SemanticDimensionCreate semanticDimensionCreate, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        return createRequestCreation(xTenantId, xWorkspaceId, semanticDimensionCreate, xCorrelationId, idempotencyKey);
    }

    /**
     * Fetch a single semantic dimension by id.
     * 
     * <p><b>200</b> - Successful response
     * @param dimensionId The dimensionId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return SemanticDimensionRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec getDimensionRequestCreation(@jakarta.annotation.Nonnull String dimensionId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'dimensionId' is set
        if (dimensionId == null) {
            throw new WebClientResponseException("Missing the required parameter 'dimensionId' when calling getDimension", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xTenantId' is set
        if (xTenantId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xTenantId' when calling getDimension", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xWorkspaceId' is set
        if (xWorkspaceId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xWorkspaceId' when calling getDimension", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("dimension_id", dimensionId);

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

        ParameterizedTypeReference<SemanticDimensionRead> localVarReturnType = new ParameterizedTypeReference<SemanticDimensionRead>() {};
        return apiClient.invokeAPI("/api/v1/semantic/dimensions/{dimension_id}", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Fetch a single semantic dimension by id.
     * 
     * <p><b>200</b> - Successful response
     * @param dimensionId The dimensionId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return SemanticDimensionRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<SemanticDimensionRead> getDimension(@jakarta.annotation.Nonnull String dimensionId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        ParameterizedTypeReference<SemanticDimensionRead> localVarReturnType = new ParameterizedTypeReference<SemanticDimensionRead>() {};
        return getDimensionRequestCreation(dimensionId, xTenantId, xWorkspaceId, xCorrelationId).bodyToMono(localVarReturnType);
    }

    /**
     * Fetch a single semantic dimension by id.
     * 
     * <p><b>200</b> - Successful response
     * @param dimensionId The dimensionId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return ResponseEntity&lt;SemanticDimensionRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<SemanticDimensionRead>> getDimensionWithHttpInfo(@jakarta.annotation.Nonnull String dimensionId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        ParameterizedTypeReference<SemanticDimensionRead> localVarReturnType = new ParameterizedTypeReference<SemanticDimensionRead>() {};
        return getDimensionRequestCreation(dimensionId, xTenantId, xWorkspaceId, xCorrelationId).toEntity(localVarReturnType);
    }

    /**
     * Fetch a single semantic dimension by id.
     * 
     * <p><b>200</b> - Successful response
     * @param dimensionId The dimensionId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec getDimensionWithResponseSpec(@jakarta.annotation.Nonnull String dimensionId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        return getDimensionRequestCreation(dimensionId, xTenantId, xWorkspaceId, xCorrelationId);
    }

    /**
     * Return version history for a dimension, oldest first.
     * 
     * <p><b>200</b> - Successful response
     * @param dimensionId The dimensionId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return PaginatedSemanticVersionRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec historyRequestCreation(@jakarta.annotation.Nonnull String dimensionId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'dimensionId' is set
        if (dimensionId == null) {
            throw new WebClientResponseException("Missing the required parameter 'dimensionId' when calling history", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xTenantId' is set
        if (xTenantId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xTenantId' when calling history", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xWorkspaceId' is set
        if (xWorkspaceId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xWorkspaceId' when calling history", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("dimension_id", dimensionId);

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

        ParameterizedTypeReference<PaginatedSemanticVersionRead> localVarReturnType = new ParameterizedTypeReference<PaginatedSemanticVersionRead>() {};
        return apiClient.invokeAPI("/api/v1/semantic/dimensions/{dimension_id}/history", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Return version history for a dimension, oldest first.
     * 
     * <p><b>200</b> - Successful response
     * @param dimensionId The dimensionId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return PaginatedSemanticVersionRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<PaginatedSemanticVersionRead> history(@jakarta.annotation.Nonnull String dimensionId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        ParameterizedTypeReference<PaginatedSemanticVersionRead> localVarReturnType = new ParameterizedTypeReference<PaginatedSemanticVersionRead>() {};
        return historyRequestCreation(dimensionId, xTenantId, xWorkspaceId, xCorrelationId).bodyToMono(localVarReturnType);
    }

    /**
     * Return version history for a dimension, oldest first.
     * 
     * <p><b>200</b> - Successful response
     * @param dimensionId The dimensionId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return ResponseEntity&lt;PaginatedSemanticVersionRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<PaginatedSemanticVersionRead>> historyWithHttpInfo(@jakarta.annotation.Nonnull String dimensionId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        ParameterizedTypeReference<PaginatedSemanticVersionRead> localVarReturnType = new ParameterizedTypeReference<PaginatedSemanticVersionRead>() {};
        return historyRequestCreation(dimensionId, xTenantId, xWorkspaceId, xCorrelationId).toEntity(localVarReturnType);
    }

    /**
     * Return version history for a dimension, oldest first.
     * 
     * <p><b>200</b> - Successful response
     * @param dimensionId The dimensionId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec historyWithResponseSpec(@jakarta.annotation.Nonnull String dimensionId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        return historyRequestCreation(dimensionId, xTenantId, xWorkspaceId, xCorrelationId);
    }

    /**
     * List semantic dimensions for the caller&#39;s workspace (optional status filter).
     * 
     * <p><b>200</b> - Successful response
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param datasetId The datasetId parameter
     * @param status The status parameter
     * @param limit The limit parameter
     * @param offset The offset parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return PaginatedSemanticDimensionRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec listDimensionsRequestCreation(@jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable String datasetId, @jakarta.annotation.Nullable String status, @jakarta.annotation.Nullable Integer limit, @jakarta.annotation.Nullable Integer offset, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'xTenantId' is set
        if (xTenantId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xTenantId' when calling listDimensions", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xWorkspaceId' is set
        if (xWorkspaceId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xWorkspaceId' when calling listDimensions", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        final MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<String, String>();
        final HttpHeaders headerParams = new HttpHeaders();
        final MultiValueMap<String, String> cookieParams = new LinkedMultiValueMap<String, String>();
        final MultiValueMap<String, Object> formParams = new LinkedMultiValueMap<String, Object>();

        queryParams.putAll(apiClient.parameterToMultiValueMap(null, "dataset_id", datasetId));
        queryParams.putAll(apiClient.parameterToMultiValueMap(null, "status", status));
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

        ParameterizedTypeReference<PaginatedSemanticDimensionRead> localVarReturnType = new ParameterizedTypeReference<PaginatedSemanticDimensionRead>() {};
        return apiClient.invokeAPI("/api/v1/semantic/dimensions", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * List semantic dimensions for the caller&#39;s workspace (optional status filter).
     * 
     * <p><b>200</b> - Successful response
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param datasetId The datasetId parameter
     * @param status The status parameter
     * @param limit The limit parameter
     * @param offset The offset parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return PaginatedSemanticDimensionRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<PaginatedSemanticDimensionRead> listDimensions(@jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable String datasetId, @jakarta.annotation.Nullable String status, @jakarta.annotation.Nullable Integer limit, @jakarta.annotation.Nullable Integer offset, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        ParameterizedTypeReference<PaginatedSemanticDimensionRead> localVarReturnType = new ParameterizedTypeReference<PaginatedSemanticDimensionRead>() {};
        return listDimensionsRequestCreation(xTenantId, xWorkspaceId, datasetId, status, limit, offset, xCorrelationId).bodyToMono(localVarReturnType);
    }

    /**
     * List semantic dimensions for the caller&#39;s workspace (optional status filter).
     * 
     * <p><b>200</b> - Successful response
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param datasetId The datasetId parameter
     * @param status The status parameter
     * @param limit The limit parameter
     * @param offset The offset parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return ResponseEntity&lt;PaginatedSemanticDimensionRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<PaginatedSemanticDimensionRead>> listDimensionsWithHttpInfo(@jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable String datasetId, @jakarta.annotation.Nullable String status, @jakarta.annotation.Nullable Integer limit, @jakarta.annotation.Nullable Integer offset, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        ParameterizedTypeReference<PaginatedSemanticDimensionRead> localVarReturnType = new ParameterizedTypeReference<PaginatedSemanticDimensionRead>() {};
        return listDimensionsRequestCreation(xTenantId, xWorkspaceId, datasetId, status, limit, offset, xCorrelationId).toEntity(localVarReturnType);
    }

    /**
     * List semantic dimensions for the caller&#39;s workspace (optional status filter).
     * 
     * <p><b>200</b> - Successful response
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param datasetId The datasetId parameter
     * @param status The status parameter
     * @param limit The limit parameter
     * @param offset The offset parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec listDimensionsWithResponseSpec(@jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable String datasetId, @jakarta.annotation.Nullable String status, @jakarta.annotation.Nullable Integer limit, @jakarta.annotation.Nullable Integer offset, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        return listDimensionsRequestCreation(xTenantId, xWorkspaceId, datasetId, status, limit, offset, xCorrelationId);
    }

    /**
     * Validate, compile, and publish a dimension (status → PUBLISHED).
     * 
     * <p><b>200</b> - Successful response
     * @param dimensionId The dimensionId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return SemanticDimensionRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec publishRequestCreation(@jakarta.annotation.Nonnull String dimensionId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'dimensionId' is set
        if (dimensionId == null) {
            throw new WebClientResponseException("Missing the required parameter 'dimensionId' when calling publish", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xTenantId' is set
        if (xTenantId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xTenantId' when calling publish", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xWorkspaceId' is set
        if (xWorkspaceId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xWorkspaceId' when calling publish", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("dimension_id", dimensionId);

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
        final String[] localVarContentTypes = { };
        final MediaType localVarContentType = apiClient.selectHeaderContentType(localVarContentTypes);

        String[] localVarAuthNames = new String[] { "WorkspaceContext", "TenantContext" };

        ParameterizedTypeReference<SemanticDimensionRead> localVarReturnType = new ParameterizedTypeReference<SemanticDimensionRead>() {};
        return apiClient.invokeAPI("/api/v1/semantic/dimensions/{dimension_id}:publish", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Validate, compile, and publish a dimension (status → PUBLISHED).
     * 
     * <p><b>200</b> - Successful response
     * @param dimensionId The dimensionId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return SemanticDimensionRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<SemanticDimensionRead> publish(@jakarta.annotation.Nonnull String dimensionId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<SemanticDimensionRead> localVarReturnType = new ParameterizedTypeReference<SemanticDimensionRead>() {};
        return publishRequestCreation(dimensionId, xTenantId, xWorkspaceId, xCorrelationId, idempotencyKey).bodyToMono(localVarReturnType);
    }

    /**
     * Validate, compile, and publish a dimension (status → PUBLISHED).
     * 
     * <p><b>200</b> - Successful response
     * @param dimensionId The dimensionId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseEntity&lt;SemanticDimensionRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<SemanticDimensionRead>> publishWithHttpInfo(@jakarta.annotation.Nonnull String dimensionId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<SemanticDimensionRead> localVarReturnType = new ParameterizedTypeReference<SemanticDimensionRead>() {};
        return publishRequestCreation(dimensionId, xTenantId, xWorkspaceId, xCorrelationId, idempotencyKey).toEntity(localVarReturnType);
    }

    /**
     * Validate, compile, and publish a dimension (status → PUBLISHED).
     * 
     * <p><b>200</b> - Successful response
     * @param dimensionId The dimensionId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec publishWithResponseSpec(@jakarta.annotation.Nonnull String dimensionId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        return publishRequestCreation(dimensionId, xTenantId, xWorkspaceId, xCorrelationId, idempotencyKey);
    }

    /**
     * Retire a dimension (status → RETIRED).
     * 
     * <p><b>200</b> - Successful response
     * @param dimensionId The dimensionId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return SemanticDimensionRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec retireRequestCreation(@jakarta.annotation.Nonnull String dimensionId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'dimensionId' is set
        if (dimensionId == null) {
            throw new WebClientResponseException("Missing the required parameter 'dimensionId' when calling retire", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xTenantId' is set
        if (xTenantId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xTenantId' when calling retire", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xWorkspaceId' is set
        if (xWorkspaceId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xWorkspaceId' when calling retire", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("dimension_id", dimensionId);

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
        final String[] localVarContentTypes = { };
        final MediaType localVarContentType = apiClient.selectHeaderContentType(localVarContentTypes);

        String[] localVarAuthNames = new String[] { "WorkspaceContext", "TenantContext" };

        ParameterizedTypeReference<SemanticDimensionRead> localVarReturnType = new ParameterizedTypeReference<SemanticDimensionRead>() {};
        return apiClient.invokeAPI("/api/v1/semantic/dimensions/{dimension_id}:retire", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Retire a dimension (status → RETIRED).
     * 
     * <p><b>200</b> - Successful response
     * @param dimensionId The dimensionId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return SemanticDimensionRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<SemanticDimensionRead> retire(@jakarta.annotation.Nonnull String dimensionId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<SemanticDimensionRead> localVarReturnType = new ParameterizedTypeReference<SemanticDimensionRead>() {};
        return retireRequestCreation(dimensionId, xTenantId, xWorkspaceId, xCorrelationId, idempotencyKey).bodyToMono(localVarReturnType);
    }

    /**
     * Retire a dimension (status → RETIRED).
     * 
     * <p><b>200</b> - Successful response
     * @param dimensionId The dimensionId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseEntity&lt;SemanticDimensionRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<SemanticDimensionRead>> retireWithHttpInfo(@jakarta.annotation.Nonnull String dimensionId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<SemanticDimensionRead> localVarReturnType = new ParameterizedTypeReference<SemanticDimensionRead>() {};
        return retireRequestCreation(dimensionId, xTenantId, xWorkspaceId, xCorrelationId, idempotencyKey).toEntity(localVarReturnType);
    }

    /**
     * Retire a dimension (status → RETIRED).
     * 
     * <p><b>200</b> - Successful response
     * @param dimensionId The dimensionId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec retireWithResponseSpec(@jakarta.annotation.Nonnull String dimensionId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        return retireRequestCreation(dimensionId, xTenantId, xWorkspaceId, xCorrelationId, idempotencyKey);
    }

    /**
     * Sparse-update a dimension; re-validates + recompiles if published.
     * 
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param dimensionId The dimensionId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param semanticDimensionUpdate The semanticDimensionUpdate parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return SemanticDimensionRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec updateRequestCreation(@jakarta.annotation.Nonnull String dimensionId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nonnull SemanticDimensionUpdate semanticDimensionUpdate, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        Object postBody = semanticDimensionUpdate;
        // verify the required parameter 'dimensionId' is set
        if (dimensionId == null) {
            throw new WebClientResponseException("Missing the required parameter 'dimensionId' when calling update", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xTenantId' is set
        if (xTenantId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xTenantId' when calling update", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xWorkspaceId' is set
        if (xWorkspaceId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xWorkspaceId' when calling update", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'semanticDimensionUpdate' is set
        if (semanticDimensionUpdate == null) {
            throw new WebClientResponseException("Missing the required parameter 'semanticDimensionUpdate' when calling update", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("dimension_id", dimensionId);

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

        ParameterizedTypeReference<SemanticDimensionRead> localVarReturnType = new ParameterizedTypeReference<SemanticDimensionRead>() {};
        return apiClient.invokeAPI("/api/v1/semantic/dimensions/{dimension_id}", HttpMethod.PUT, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Sparse-update a dimension; re-validates + recompiles if published.
     * 
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param dimensionId The dimensionId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param semanticDimensionUpdate The semanticDimensionUpdate parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return SemanticDimensionRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<SemanticDimensionRead> update(@jakarta.annotation.Nonnull String dimensionId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nonnull SemanticDimensionUpdate semanticDimensionUpdate, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<SemanticDimensionRead> localVarReturnType = new ParameterizedTypeReference<SemanticDimensionRead>() {};
        return updateRequestCreation(dimensionId, xTenantId, xWorkspaceId, semanticDimensionUpdate, xCorrelationId, idempotencyKey).bodyToMono(localVarReturnType);
    }

    /**
     * Sparse-update a dimension; re-validates + recompiles if published.
     * 
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param dimensionId The dimensionId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param semanticDimensionUpdate The semanticDimensionUpdate parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseEntity&lt;SemanticDimensionRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<SemanticDimensionRead>> updateWithHttpInfo(@jakarta.annotation.Nonnull String dimensionId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nonnull SemanticDimensionUpdate semanticDimensionUpdate, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<SemanticDimensionRead> localVarReturnType = new ParameterizedTypeReference<SemanticDimensionRead>() {};
        return updateRequestCreation(dimensionId, xTenantId, xWorkspaceId, semanticDimensionUpdate, xCorrelationId, idempotencyKey).toEntity(localVarReturnType);
    }

    /**
     * Sparse-update a dimension; re-validates + recompiles if published.
     * 
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param dimensionId The dimensionId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param semanticDimensionUpdate The semanticDimensionUpdate parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec updateWithResponseSpec(@jakarta.annotation.Nonnull String dimensionId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nonnull SemanticDimensionUpdate semanticDimensionUpdate, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        return updateRequestCreation(dimensionId, xTenantId, xWorkspaceId, semanticDimensionUpdate, xCorrelationId, idempotencyKey);
    }
}
