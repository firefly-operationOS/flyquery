package com.firefly.flyquery.api;

import com.firefly.flyquery.ApiClient;

import com.firefly.flyquery.model.SchemaChangeRead;
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
public class SchemaChangesApi {
    private ApiClient apiClient;

    public SchemaChangesApi() {
        this(new ApiClient());
    }

    public SchemaChangesApi(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    public ApiClient getApiClient() {
        return apiClient;
    }

    public void setApiClient(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    /**
     * Flip a RENAMED_CANDIDATE row to RENAMED.
     * Validates that the change exists and is in state RENAMED_CANDIDATE. Sets approved_by (the current actor / tenant_id), approved_at (now), change &#x3D; &#39;RENAMED&#39;. Also updates last_changed_at on the corresponding schema_objects column row.
     * <p><b>200</b> - Successful response
     * @param changeId The changeId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return SchemaChangeRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec confirmRequestCreation(@jakarta.annotation.Nullable String changeId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'changeId' is set
        if (changeId == null) {
            throw new WebClientResponseException("Missing the required parameter 'changeId' when calling confirm", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xTenantId' is set
        if (xTenantId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xTenantId' when calling confirm", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xWorkspaceId' is set
        if (xWorkspaceId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xWorkspaceId' when calling confirm", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("change_id", changeId);

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

        ParameterizedTypeReference<SchemaChangeRead> localVarReturnType = new ParameterizedTypeReference<SchemaChangeRead>() {};
        return apiClient.invokeAPI("/api/v1/schema-changes/{change_id}:confirm", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Flip a RENAMED_CANDIDATE row to RENAMED.
     * Validates that the change exists and is in state RENAMED_CANDIDATE. Sets approved_by (the current actor / tenant_id), approved_at (now), change &#x3D; &#39;RENAMED&#39;. Also updates last_changed_at on the corresponding schema_objects column row.
     * <p><b>200</b> - Successful response
     * @param changeId The changeId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return SchemaChangeRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<SchemaChangeRead> confirm(@jakarta.annotation.Nullable String changeId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<SchemaChangeRead> localVarReturnType = new ParameterizedTypeReference<SchemaChangeRead>() {};
        return confirmRequestCreation(changeId, xTenantId, xWorkspaceId, xCorrelationId, idempotencyKey).bodyToMono(localVarReturnType);
    }

    /**
     * Flip a RENAMED_CANDIDATE row to RENAMED.
     * Validates that the change exists and is in state RENAMED_CANDIDATE. Sets approved_by (the current actor / tenant_id), approved_at (now), change &#x3D; &#39;RENAMED&#39;. Also updates last_changed_at on the corresponding schema_objects column row.
     * <p><b>200</b> - Successful response
     * @param changeId The changeId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseEntity&lt;SchemaChangeRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<SchemaChangeRead>> confirmWithHttpInfo(@jakarta.annotation.Nullable String changeId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<SchemaChangeRead> localVarReturnType = new ParameterizedTypeReference<SchemaChangeRead>() {};
        return confirmRequestCreation(changeId, xTenantId, xWorkspaceId, xCorrelationId, idempotencyKey).toEntity(localVarReturnType);
    }

    /**
     * Flip a RENAMED_CANDIDATE row to RENAMED.
     * Validates that the change exists and is in state RENAMED_CANDIDATE. Sets approved_by (the current actor / tenant_id), approved_at (now), change &#x3D; &#39;RENAMED&#39;. Also updates last_changed_at on the corresponding schema_objects column row.
     * <p><b>200</b> - Successful response
     * @param changeId The changeId parameter
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec confirmWithResponseSpec(@jakarta.annotation.Nullable String changeId, @jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable UUID xCorrelationId, @jakarta.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        return confirmRequestCreation(changeId, xTenantId, xWorkspaceId, xCorrelationId, idempotencyKey);
    }
}
