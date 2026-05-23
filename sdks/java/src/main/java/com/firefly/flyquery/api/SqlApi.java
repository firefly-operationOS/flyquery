package com.firefly.flyquery.api;

import com.firefly.flyquery.ApiClient;

import com.firefly.flyquery.model.HTTPValidationError;
import com.firefly.flyquery.model.SqlExecuteRequest;
import com.firefly.flyquery.model.SqlExecuteResponse;
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

@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaClientCodegen", date = "2026-05-23T22:03:38.852419+02:00[Europe/Madrid]", comments = "Generator version: 7.22.0")
public class SqlApi {
    private ApiClient apiClient;

    public SqlApi() {
        this(new ApiClient());
    }

    public SqlApi(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    public ApiClient getApiClient() {
        return apiClient;
    }

    public void setApiClient(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    /**
     * Execute a SQL statement directly against the workspace&#39;s dataset Parquet.
     * Requires the workspace flag &#x60;&#x60;allow_direct_sql&#x3D;true&#x60;&#x60;. The SQL is AST-classified and scope-checked; the agent pipeline is skipped.  :param http_request: Starlette request :param body: validated SqlExecuteRequest :return: SqlExecuteResponse with preview rows and execution metadata :raises DirectSqlForbidden: when workspace.allow_direct_sql is False
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param sqlExecuteRequest The sqlExecuteRequest parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return SqlExecuteResponse
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec executeRequestCreation(@javax.annotation.Nonnull String xTenantId, @javax.annotation.Nonnull String xWorkspaceId, @javax.annotation.Nonnull SqlExecuteRequest sqlExecuteRequest, @javax.annotation.Nullable UUID xCorrelationId, @javax.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        Object postBody = sqlExecuteRequest;
        // verify the required parameter 'xTenantId' is set
        if (xTenantId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xTenantId' when calling execute", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xWorkspaceId' is set
        if (xWorkspaceId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xWorkspaceId' when calling execute", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'sqlExecuteRequest' is set
        if (sqlExecuteRequest == null) {
            throw new WebClientResponseException("Missing the required parameter 'sqlExecuteRequest' when calling execute", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
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

        ParameterizedTypeReference<SqlExecuteResponse> localVarReturnType = new ParameterizedTypeReference<SqlExecuteResponse>() {};
        return apiClient.invokeAPI("/api/v1/sql:execute", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Execute a SQL statement directly against the workspace&#39;s dataset Parquet.
     * Requires the workspace flag &#x60;&#x60;allow_direct_sql&#x3D;true&#x60;&#x60;. The SQL is AST-classified and scope-checked; the agent pipeline is skipped.  :param http_request: Starlette request :param body: validated SqlExecuteRequest :return: SqlExecuteResponse with preview rows and execution metadata :raises DirectSqlForbidden: when workspace.allow_direct_sql is False
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param sqlExecuteRequest The sqlExecuteRequest parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return SqlExecuteResponse
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<SqlExecuteResponse> execute(@javax.annotation.Nonnull String xTenantId, @javax.annotation.Nonnull String xWorkspaceId, @javax.annotation.Nonnull SqlExecuteRequest sqlExecuteRequest, @javax.annotation.Nullable UUID xCorrelationId, @javax.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<SqlExecuteResponse> localVarReturnType = new ParameterizedTypeReference<SqlExecuteResponse>() {};
        return executeRequestCreation(xTenantId, xWorkspaceId, sqlExecuteRequest, xCorrelationId, idempotencyKey).bodyToMono(localVarReturnType);
    }

    /**
     * Execute a SQL statement directly against the workspace&#39;s dataset Parquet.
     * Requires the workspace flag &#x60;&#x60;allow_direct_sql&#x3D;true&#x60;&#x60;. The SQL is AST-classified and scope-checked; the agent pipeline is skipped.  :param http_request: Starlette request :param body: validated SqlExecuteRequest :return: SqlExecuteResponse with preview rows and execution metadata :raises DirectSqlForbidden: when workspace.allow_direct_sql is False
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param sqlExecuteRequest The sqlExecuteRequest parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseEntity&lt;SqlExecuteResponse&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<SqlExecuteResponse>> executeWithHttpInfo(@javax.annotation.Nonnull String xTenantId, @javax.annotation.Nonnull String xWorkspaceId, @javax.annotation.Nonnull SqlExecuteRequest sqlExecuteRequest, @javax.annotation.Nullable UUID xCorrelationId, @javax.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<SqlExecuteResponse> localVarReturnType = new ParameterizedTypeReference<SqlExecuteResponse>() {};
        return executeRequestCreation(xTenantId, xWorkspaceId, sqlExecuteRequest, xCorrelationId, idempotencyKey).toEntity(localVarReturnType);
    }

    /**
     * Execute a SQL statement directly against the workspace&#39;s dataset Parquet.
     * Requires the workspace flag &#x60;&#x60;allow_direct_sql&#x3D;true&#x60;&#x60;. The SQL is AST-classified and scope-checked; the agent pipeline is skipped.  :param http_request: Starlette request :param body: validated SqlExecuteRequest :return: SqlExecuteResponse with preview rows and execution metadata :raises DirectSqlForbidden: when workspace.allow_direct_sql is False
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param sqlExecuteRequest The sqlExecuteRequest parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec executeWithResponseSpec(@javax.annotation.Nonnull String xTenantId, @javax.annotation.Nonnull String xWorkspaceId, @javax.annotation.Nonnull SqlExecuteRequest sqlExecuteRequest, @javax.annotation.Nullable UUID xCorrelationId, @javax.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        return executeRequestCreation(xTenantId, xWorkspaceId, sqlExecuteRequest, xCorrelationId, idempotencyKey);
    }

    /**
     * Execute SQL and stream progress as Server-Sent Events.
     * Event sequence: 1. &#x60;&#x60;ast_classified&#x60;&#x60; — AST result + scope check outcome 2. &#x60;&#x60;executed&#x60;&#x60;       — DuckDB result 3. &#x60;&#x60;final&#x60;&#x60;          — full SqlExecuteResponse JSON  :param http_request: Starlette request :param body: validated SqlExecuteRequest :return: StreamingResponse with &#x60;&#x60;text/event-stream&#x60;&#x60;
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param sqlExecuteRequest The sqlExecuteRequest parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec executeStreamRequestCreation(@javax.annotation.Nonnull String xTenantId, @javax.annotation.Nonnull String xWorkspaceId, @javax.annotation.Nonnull SqlExecuteRequest sqlExecuteRequest, @javax.annotation.Nullable UUID xCorrelationId, @javax.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        Object postBody = sqlExecuteRequest;
        // verify the required parameter 'xTenantId' is set
        if (xTenantId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xTenantId' when calling executeStream", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xWorkspaceId' is set
        if (xWorkspaceId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xWorkspaceId' when calling executeStream", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'sqlExecuteRequest' is set
        if (sqlExecuteRequest == null) {
            throw new WebClientResponseException("Missing the required parameter 'sqlExecuteRequest' when calling executeStream", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
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

        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return apiClient.invokeAPI("/api/v1/sql:execute/stream", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Execute SQL and stream progress as Server-Sent Events.
     * Event sequence: 1. &#x60;&#x60;ast_classified&#x60;&#x60; — AST result + scope check outcome 2. &#x60;&#x60;executed&#x60;&#x60;       — DuckDB result 3. &#x60;&#x60;final&#x60;&#x60;          — full SqlExecuteResponse JSON  :param http_request: Starlette request :param body: validated SqlExecuteRequest :return: StreamingResponse with &#x60;&#x60;text/event-stream&#x60;&#x60;
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param sqlExecuteRequest The sqlExecuteRequest parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<Void> executeStream(@javax.annotation.Nonnull String xTenantId, @javax.annotation.Nonnull String xWorkspaceId, @javax.annotation.Nonnull SqlExecuteRequest sqlExecuteRequest, @javax.annotation.Nullable UUID xCorrelationId, @javax.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return executeStreamRequestCreation(xTenantId, xWorkspaceId, sqlExecuteRequest, xCorrelationId, idempotencyKey).bodyToMono(localVarReturnType);
    }

    /**
     * Execute SQL and stream progress as Server-Sent Events.
     * Event sequence: 1. &#x60;&#x60;ast_classified&#x60;&#x60; — AST result + scope check outcome 2. &#x60;&#x60;executed&#x60;&#x60;       — DuckDB result 3. &#x60;&#x60;final&#x60;&#x60;          — full SqlExecuteResponse JSON  :param http_request: Starlette request :param body: validated SqlExecuteRequest :return: StreamingResponse with &#x60;&#x60;text/event-stream&#x60;&#x60;
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param sqlExecuteRequest The sqlExecuteRequest parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<Void>> executeStreamWithHttpInfo(@javax.annotation.Nonnull String xTenantId, @javax.annotation.Nonnull String xWorkspaceId, @javax.annotation.Nonnull SqlExecuteRequest sqlExecuteRequest, @javax.annotation.Nullable UUID xCorrelationId, @javax.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return executeStreamRequestCreation(xTenantId, xWorkspaceId, sqlExecuteRequest, xCorrelationId, idempotencyKey).toEntity(localVarReturnType);
    }

    /**
     * Execute SQL and stream progress as Server-Sent Events.
     * Event sequence: 1. &#x60;&#x60;ast_classified&#x60;&#x60; — AST result + scope check outcome 2. &#x60;&#x60;executed&#x60;&#x60;       — DuckDB result 3. &#x60;&#x60;final&#x60;&#x60;          — full SqlExecuteResponse JSON  :param http_request: Starlette request :param body: validated SqlExecuteRequest :return: StreamingResponse with &#x60;&#x60;text/event-stream&#x60;&#x60;
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param sqlExecuteRequest The sqlExecuteRequest parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @param idempotencyKey Optional client-supplied idempotency key for mutating operations. The first request with a key persists its result; subsequent requests with the same key + same tenant return the cached response. Keys expire after 24h.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec executeStreamWithResponseSpec(@javax.annotation.Nonnull String xTenantId, @javax.annotation.Nonnull String xWorkspaceId, @javax.annotation.Nonnull SqlExecuteRequest sqlExecuteRequest, @javax.annotation.Nullable UUID xCorrelationId, @javax.annotation.Nullable String idempotencyKey) throws WebClientResponseException {
        return executeStreamRequestCreation(xTenantId, xWorkspaceId, sqlExecuteRequest, xCorrelationId, idempotencyKey);
    }
}
