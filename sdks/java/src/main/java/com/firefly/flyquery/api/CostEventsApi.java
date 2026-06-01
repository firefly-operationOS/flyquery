package com.firefly.flyquery.api;

import com.firefly.flyquery.ApiClient;

import com.firefly.flyquery.model.PaginatedCostEventRead;
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
public class CostEventsApi {
    private ApiClient apiClient;

    public CostEventsApi() {
        this(new ApiClient());
    }

    public CostEventsApi(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    public ApiClient getApiClient() {
        return apiClient;
    }

    public void setApiClient(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    /**
     * List cost events for the caller&#39;s workspace, newest first.
     * Filters ------- * &#x60;&#x60;actor&#x60;&#x60;     -- exact match * &#x60;&#x60;model&#x60;&#x60;     -- exact match (&#x60;&#x60;anthropic:claude-sonnet-4-6&#x60;&#x60; etc.) * &#x60;&#x60;operation&#x60;&#x60; -- exact match (&#x60;&#x60;grounding&#x60;&#x60; / &#x60;&#x60;generation&#x60;&#x60; / ...) * &#x60;&#x60;date_from&#x60;&#x60; -- inclusive lower bound on &#x60;&#x60;created_at&#x60;&#x60; * &#x60;&#x60;date_to&#x60;&#x60;   -- exclusive upper bound on &#x60;&#x60;created_at&#x60;&#x60;
     * <p><b>200</b> - Successful response
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param actor The actor parameter
     * @param model The model parameter
     * @param operation The operation parameter
     * @param dateFrom The dateFrom parameter
     * @param dateTo The dateTo parameter
     * @param limit The limit parameter
     * @param offset The offset parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return PaginatedCostEventRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec listEventsRequestCreation(@jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable String actor, @jakarta.annotation.Nullable String model, @jakarta.annotation.Nullable String operation, @jakarta.annotation.Nullable String dateFrom, @jakarta.annotation.Nullable String dateTo, @jakarta.annotation.Nullable Integer limit, @jakarta.annotation.Nullable Integer offset, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'xTenantId' is set
        if (xTenantId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xTenantId' when calling listEvents", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xWorkspaceId' is set
        if (xWorkspaceId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xWorkspaceId' when calling listEvents", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        final MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<String, String>();
        final HttpHeaders headerParams = new HttpHeaders();
        final MultiValueMap<String, String> cookieParams = new LinkedMultiValueMap<String, String>();
        final MultiValueMap<String, Object> formParams = new LinkedMultiValueMap<String, Object>();

        queryParams.putAll(apiClient.parameterToMultiValueMap(null, "actor", actor));
        queryParams.putAll(apiClient.parameterToMultiValueMap(null, "model", model));
        queryParams.putAll(apiClient.parameterToMultiValueMap(null, "operation", operation));
        queryParams.putAll(apiClient.parameterToMultiValueMap(null, "date_from", dateFrom));
        queryParams.putAll(apiClient.parameterToMultiValueMap(null, "date_to", dateTo));
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

        ParameterizedTypeReference<PaginatedCostEventRead> localVarReturnType = new ParameterizedTypeReference<PaginatedCostEventRead>() {};
        return apiClient.invokeAPI("/api/v1/cost-events", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * List cost events for the caller&#39;s workspace, newest first.
     * Filters ------- * &#x60;&#x60;actor&#x60;&#x60;     -- exact match * &#x60;&#x60;model&#x60;&#x60;     -- exact match (&#x60;&#x60;anthropic:claude-sonnet-4-6&#x60;&#x60; etc.) * &#x60;&#x60;operation&#x60;&#x60; -- exact match (&#x60;&#x60;grounding&#x60;&#x60; / &#x60;&#x60;generation&#x60;&#x60; / ...) * &#x60;&#x60;date_from&#x60;&#x60; -- inclusive lower bound on &#x60;&#x60;created_at&#x60;&#x60; * &#x60;&#x60;date_to&#x60;&#x60;   -- exclusive upper bound on &#x60;&#x60;created_at&#x60;&#x60;
     * <p><b>200</b> - Successful response
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param actor The actor parameter
     * @param model The model parameter
     * @param operation The operation parameter
     * @param dateFrom The dateFrom parameter
     * @param dateTo The dateTo parameter
     * @param limit The limit parameter
     * @param offset The offset parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return PaginatedCostEventRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<PaginatedCostEventRead> listEvents(@jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable String actor, @jakarta.annotation.Nullable String model, @jakarta.annotation.Nullable String operation, @jakarta.annotation.Nullable String dateFrom, @jakarta.annotation.Nullable String dateTo, @jakarta.annotation.Nullable Integer limit, @jakarta.annotation.Nullable Integer offset, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        ParameterizedTypeReference<PaginatedCostEventRead> localVarReturnType = new ParameterizedTypeReference<PaginatedCostEventRead>() {};
        return listEventsRequestCreation(xTenantId, xWorkspaceId, actor, model, operation, dateFrom, dateTo, limit, offset, xCorrelationId).bodyToMono(localVarReturnType);
    }

    /**
     * List cost events for the caller&#39;s workspace, newest first.
     * Filters ------- * &#x60;&#x60;actor&#x60;&#x60;     -- exact match * &#x60;&#x60;model&#x60;&#x60;     -- exact match (&#x60;&#x60;anthropic:claude-sonnet-4-6&#x60;&#x60; etc.) * &#x60;&#x60;operation&#x60;&#x60; -- exact match (&#x60;&#x60;grounding&#x60;&#x60; / &#x60;&#x60;generation&#x60;&#x60; / ...) * &#x60;&#x60;date_from&#x60;&#x60; -- inclusive lower bound on &#x60;&#x60;created_at&#x60;&#x60; * &#x60;&#x60;date_to&#x60;&#x60;   -- exclusive upper bound on &#x60;&#x60;created_at&#x60;&#x60;
     * <p><b>200</b> - Successful response
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param actor The actor parameter
     * @param model The model parameter
     * @param operation The operation parameter
     * @param dateFrom The dateFrom parameter
     * @param dateTo The dateTo parameter
     * @param limit The limit parameter
     * @param offset The offset parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return ResponseEntity&lt;PaginatedCostEventRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<PaginatedCostEventRead>> listEventsWithHttpInfo(@jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable String actor, @jakarta.annotation.Nullable String model, @jakarta.annotation.Nullable String operation, @jakarta.annotation.Nullable String dateFrom, @jakarta.annotation.Nullable String dateTo, @jakarta.annotation.Nullable Integer limit, @jakarta.annotation.Nullable Integer offset, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        ParameterizedTypeReference<PaginatedCostEventRead> localVarReturnType = new ParameterizedTypeReference<PaginatedCostEventRead>() {};
        return listEventsRequestCreation(xTenantId, xWorkspaceId, actor, model, operation, dateFrom, dateTo, limit, offset, xCorrelationId).toEntity(localVarReturnType);
    }

    /**
     * List cost events for the caller&#39;s workspace, newest first.
     * Filters ------- * &#x60;&#x60;actor&#x60;&#x60;     -- exact match * &#x60;&#x60;model&#x60;&#x60;     -- exact match (&#x60;&#x60;anthropic:claude-sonnet-4-6&#x60;&#x60; etc.) * &#x60;&#x60;operation&#x60;&#x60; -- exact match (&#x60;&#x60;grounding&#x60;&#x60; / &#x60;&#x60;generation&#x60;&#x60; / ...) * &#x60;&#x60;date_from&#x60;&#x60; -- inclusive lower bound on &#x60;&#x60;created_at&#x60;&#x60; * &#x60;&#x60;date_to&#x60;&#x60;   -- exclusive upper bound on &#x60;&#x60;created_at&#x60;&#x60;
     * <p><b>200</b> - Successful response
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param actor The actor parameter
     * @param model The model parameter
     * @param operation The operation parameter
     * @param dateFrom The dateFrom parameter
     * @param dateTo The dateTo parameter
     * @param limit The limit parameter
     * @param offset The offset parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec listEventsWithResponseSpec(@jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable String actor, @jakarta.annotation.Nullable String model, @jakarta.annotation.Nullable String operation, @jakarta.annotation.Nullable String dateFrom, @jakarta.annotation.Nullable String dateTo, @jakarta.annotation.Nullable Integer limit, @jakarta.annotation.Nullable Integer offset, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        return listEventsRequestCreation(xTenantId, xWorkspaceId, actor, model, operation, dateFrom, dateTo, limit, offset, xCorrelationId);
    }
}
