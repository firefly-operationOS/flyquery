package com.firefly.flyquery.api;

import com.firefly.flyquery.ApiClient;

import com.firefly.flyquery.model.PaginatedRelationRead;
import com.firefly.flyquery.model.RelationApprovalRead;
import com.firefly.flyquery.model.RelationRejectionRead;
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
public class RelationsApi {
    private ApiClient apiClient;

    public RelationsApi() {
        this(new ApiClient());
    }

    public RelationsApi(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    public ApiClient getApiClient() {
        return apiClient;
    }

    public void setApiClient(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    /**
     * Approve a PROPOSED relation.
     * 
     * <p><b>200</b> - Successful response
     * @param relationId The relationId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return RelationApprovalRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec approveRelationRequestCreation(@jakarta.annotation.Nullable String relationId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'relationId' is set
        if (relationId == null) {
            throw new WebClientResponseException("Missing the required parameter 'relationId' when calling approveRelation", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xTenantId' is set
        if (xTenantId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xTenantId' when calling approveRelation", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xWorkspaceId' is set
        if (xWorkspaceId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xWorkspaceId' when calling approveRelation", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("relation_id", relationId);

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

        ParameterizedTypeReference<RelationApprovalRead> localVarReturnType = new ParameterizedTypeReference<RelationApprovalRead>() {};
        return apiClient.invokeAPI("/api/v1/relations/{relation_id}:approve", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Approve a PROPOSED relation.
     * 
     * <p><b>200</b> - Successful response
     * @param relationId The relationId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return RelationApprovalRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<RelationApprovalRead> approveRelation(@jakarta.annotation.Nullable String relationId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<RelationApprovalRead> localVarReturnType = new ParameterizedTypeReference<RelationApprovalRead>() {};
        return approveRelationRequestCreation(relationId, xTenantId, xWorkspaceId, xCorrelationId, idempotencyKey).bodyToMono(localVarReturnType);
    }

    /**
     * Approve a PROPOSED relation.
     * 
     * <p><b>200</b> - Successful response
     * @param relationId The relationId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseEntity&lt;RelationApprovalRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<RelationApprovalRead>> approveRelationWithHttpInfo(@jakarta.annotation.Nullable String relationId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<RelationApprovalRead> localVarReturnType = new ParameterizedTypeReference<RelationApprovalRead>() {};
        return approveRelationRequestCreation(relationId, xTenantId, xWorkspaceId, xCorrelationId, idempotencyKey).toEntity(localVarReturnType);
    }

    /**
     * Approve a PROPOSED relation.
     * 
     * <p><b>200</b> - Successful response
     * @param relationId The relationId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec approveRelationWithResponseSpec(@jakarta.annotation.Nullable String relationId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        return approveRelationRequestCreation(relationId, xTenantId, xWorkspaceId, xCorrelationId, idempotencyKey);
    }

    /**
     * List relations for a dataset (all statuses by default).
     * Optional &#x60;&#x60;status&#x60;&#x60; filter restricts to one of &#x60;&#x60;PROPOSED&#x60;&#x60;, &#x60;&#x60;APPROVED&#x60;&#x60;, &#x60;&#x60;REJECTED&#x60;&#x60;.
     * <p><b>200</b> - Successful response
     * @param datasetId The datasetId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param status The status parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return PaginatedRelationRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec listRelationsRequestCreation(@jakarta.annotation.Nonnull String datasetId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable String status, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'datasetId' is set
        if (datasetId == null) {
            throw new WebClientResponseException("Missing the required parameter 'datasetId' when calling listRelations", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xTenantId' is set
        if (xTenantId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xTenantId' when calling listRelations", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xWorkspaceId' is set
        if (xWorkspaceId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xWorkspaceId' when calling listRelations", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("dataset_id", datasetId);

        final MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<String, String>();
        final HttpHeaders headerParams = new HttpHeaders();
        final MultiValueMap<String, String> cookieParams = new LinkedMultiValueMap<String, String>();
        final MultiValueMap<String, Object> formParams = new LinkedMultiValueMap<String, Object>();

        queryParams.putAll(apiClient.parameterToMultiValueMap(null, "status", status));

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

        ParameterizedTypeReference<PaginatedRelationRead> localVarReturnType = new ParameterizedTypeReference<PaginatedRelationRead>() {};
        return apiClient.invokeAPI("/api/v1/datasets/{dataset_id}/relations", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * List relations for a dataset (all statuses by default).
     * Optional &#x60;&#x60;status&#x60;&#x60; filter restricts to one of &#x60;&#x60;PROPOSED&#x60;&#x60;, &#x60;&#x60;APPROVED&#x60;&#x60;, &#x60;&#x60;REJECTED&#x60;&#x60;.
     * <p><b>200</b> - Successful response
     * @param datasetId The datasetId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param status The status parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return PaginatedRelationRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<PaginatedRelationRead> listRelations(@jakarta.annotation.Nonnull String datasetId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable String status, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        ParameterizedTypeReference<PaginatedRelationRead> localVarReturnType = new ParameterizedTypeReference<PaginatedRelationRead>() {};
        return listRelationsRequestCreation(datasetId, xTenantId, xWorkspaceId, status, xCorrelationId).bodyToMono(localVarReturnType);
    }

    /**
     * List relations for a dataset (all statuses by default).
     * Optional &#x60;&#x60;status&#x60;&#x60; filter restricts to one of &#x60;&#x60;PROPOSED&#x60;&#x60;, &#x60;&#x60;APPROVED&#x60;&#x60;, &#x60;&#x60;REJECTED&#x60;&#x60;.
     * <p><b>200</b> - Successful response
     * @param datasetId The datasetId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param status The status parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return ResponseEntity&lt;PaginatedRelationRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<PaginatedRelationRead>> listRelationsWithHttpInfo(@jakarta.annotation.Nonnull String datasetId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable String status, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        ParameterizedTypeReference<PaginatedRelationRead> localVarReturnType = new ParameterizedTypeReference<PaginatedRelationRead>() {};
        return listRelationsRequestCreation(datasetId, xTenantId, xWorkspaceId, status, xCorrelationId).toEntity(localVarReturnType);
    }

    /**
     * List relations for a dataset (all statuses by default).
     * Optional &#x60;&#x60;status&#x60;&#x60; filter restricts to one of &#x60;&#x60;PROPOSED&#x60;&#x60;, &#x60;&#x60;APPROVED&#x60;&#x60;, &#x60;&#x60;REJECTED&#x60;&#x60;.
     * <p><b>200</b> - Successful response
     * @param datasetId The datasetId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param status The status parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec listRelationsWithResponseSpec(@jakarta.annotation.Nonnull String datasetId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable String status, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        return listRelationsRequestCreation(datasetId, xTenantId, xWorkspaceId, status, xCorrelationId);
    }

    /**
     * Reject a PROPOSED relation.
     * 
     * <p><b>200</b> - Successful response
     * @param relationId The relationId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return RelationRejectionRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec rejectRelationRequestCreation(@jakarta.annotation.Nonnull String relationId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'relationId' is set
        if (relationId == null) {
            throw new WebClientResponseException("Missing the required parameter 'relationId' when calling rejectRelation", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xTenantId' is set
        if (xTenantId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xTenantId' when calling rejectRelation", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xWorkspaceId' is set
        if (xWorkspaceId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xWorkspaceId' when calling rejectRelation", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("relation_id", relationId);

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

        ParameterizedTypeReference<RelationRejectionRead> localVarReturnType = new ParameterizedTypeReference<RelationRejectionRead>() {};
        return apiClient.invokeAPI("/api/v1/relations/{relation_id}:reject", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Reject a PROPOSED relation.
     * 
     * <p><b>200</b> - Successful response
     * @param relationId The relationId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return RelationRejectionRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<RelationRejectionRead> rejectRelation(@jakarta.annotation.Nonnull String relationId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<RelationRejectionRead> localVarReturnType = new ParameterizedTypeReference<RelationRejectionRead>() {};
        return rejectRelationRequestCreation(relationId, xTenantId, xWorkspaceId, xCorrelationId, idempotencyKey).bodyToMono(localVarReturnType);
    }

    /**
     * Reject a PROPOSED relation.
     * 
     * <p><b>200</b> - Successful response
     * @param relationId The relationId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseEntity&lt;RelationRejectionRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<RelationRejectionRead>> rejectRelationWithHttpInfo(@jakarta.annotation.Nonnull String relationId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<RelationRejectionRead> localVarReturnType = new ParameterizedTypeReference<RelationRejectionRead>() {};
        return rejectRelationRequestCreation(relationId, xTenantId, xWorkspaceId, xCorrelationId, idempotencyKey).toEntity(localVarReturnType);
    }

    /**
     * Reject a PROPOSED relation.
     * 
     * <p><b>200</b> - Successful response
     * @param relationId The relationId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec rejectRelationWithResponseSpec(@jakarta.annotation.Nonnull String relationId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        return rejectRelationRequestCreation(relationId, xTenantId, xWorkspaceId, xCorrelationId, idempotencyKey);
    }
}
