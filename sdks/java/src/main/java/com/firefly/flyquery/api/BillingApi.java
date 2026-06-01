package com.firefly.flyquery.api;

import com.firefly.flyquery.ApiClient;

import com.firefly.flyquery.model.BillingRollup;
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
public class BillingApi {
    private ApiClient apiClient;

    public BillingApi() {
        this(new ApiClient());
    }

    public BillingApi(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    public ApiClient getApiClient() {
        return apiClient;
    }

    public void setApiClient(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    /**
     * Aggregate LLM cost into &#x60;&#x60;day&#x60;&#x60; / &#x60;&#x60;week&#x60;&#x60; / &#x60;&#x60;month&#x60;&#x60; buckets.
     * Query params ------------ * &#x60;&#x60;period&#x60;&#x60;    -- &#x60;&#x60;day&#x60;&#x60; (default) / &#x60;&#x60;week&#x60;&#x60; / &#x60;&#x60;month&#x60;&#x60; * &#x60;&#x60;date_from&#x60;&#x60; -- inclusive lower bound on &#x60;&#x60;created_at&#x60;&#x60; * &#x60;&#x60;date_to&#x60;&#x60;   -- exclusive upper bound on &#x60;&#x60;created_at&#x60;&#x60;  Response shape: :class:&#x60;BillingRollup&#x60;. Buckets with zero cost are omitted from the breakdown (no empty days).
     * <p><b>200</b> - Successful response
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param period The period parameter
     * @param dateFrom The dateFrom parameter
     * @param dateTo The dateTo parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return BillingRollup
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec rollupRequestCreation(@jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable String period, @jakarta.annotation.Nullable String dateFrom, @jakarta.annotation.Nullable String dateTo, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'xTenantId' is set
        if (xTenantId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xTenantId' when calling rollup", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'xWorkspaceId' is set
        if (xWorkspaceId == null) {
            throw new WebClientResponseException("Missing the required parameter 'xWorkspaceId' when calling rollup", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        final MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<String, String>();
        final HttpHeaders headerParams = new HttpHeaders();
        final MultiValueMap<String, String> cookieParams = new LinkedMultiValueMap<String, String>();
        final MultiValueMap<String, Object> formParams = new LinkedMultiValueMap<String, Object>();

        queryParams.putAll(apiClient.parameterToMultiValueMap(null, "period", period));
        queryParams.putAll(apiClient.parameterToMultiValueMap(null, "date_from", dateFrom));
        queryParams.putAll(apiClient.parameterToMultiValueMap(null, "date_to", dateTo));

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

        ParameterizedTypeReference<BillingRollup> localVarReturnType = new ParameterizedTypeReference<BillingRollup>() {};
        return apiClient.invokeAPI("/api/v1/billing", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Aggregate LLM cost into &#x60;&#x60;day&#x60;&#x60; / &#x60;&#x60;week&#x60;&#x60; / &#x60;&#x60;month&#x60;&#x60; buckets.
     * Query params ------------ * &#x60;&#x60;period&#x60;&#x60;    -- &#x60;&#x60;day&#x60;&#x60; (default) / &#x60;&#x60;week&#x60;&#x60; / &#x60;&#x60;month&#x60;&#x60; * &#x60;&#x60;date_from&#x60;&#x60; -- inclusive lower bound on &#x60;&#x60;created_at&#x60;&#x60; * &#x60;&#x60;date_to&#x60;&#x60;   -- exclusive upper bound on &#x60;&#x60;created_at&#x60;&#x60;  Response shape: :class:&#x60;BillingRollup&#x60;. Buckets with zero cost are omitted from the breakdown (no empty days).
     * <p><b>200</b> - Successful response
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param period The period parameter
     * @param dateFrom The dateFrom parameter
     * @param dateTo The dateTo parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return BillingRollup
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<BillingRollup> rollup(@jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable String period, @jakarta.annotation.Nullable String dateFrom, @jakarta.annotation.Nullable String dateTo, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        ParameterizedTypeReference<BillingRollup> localVarReturnType = new ParameterizedTypeReference<BillingRollup>() {};
        return rollupRequestCreation(xTenantId, xWorkspaceId, period, dateFrom, dateTo, xCorrelationId).bodyToMono(localVarReturnType);
    }

    /**
     * Aggregate LLM cost into &#x60;&#x60;day&#x60;&#x60; / &#x60;&#x60;week&#x60;&#x60; / &#x60;&#x60;month&#x60;&#x60; buckets.
     * Query params ------------ * &#x60;&#x60;period&#x60;&#x60;    -- &#x60;&#x60;day&#x60;&#x60; (default) / &#x60;&#x60;week&#x60;&#x60; / &#x60;&#x60;month&#x60;&#x60; * &#x60;&#x60;date_from&#x60;&#x60; -- inclusive lower bound on &#x60;&#x60;created_at&#x60;&#x60; * &#x60;&#x60;date_to&#x60;&#x60;   -- exclusive upper bound on &#x60;&#x60;created_at&#x60;&#x60;  Response shape: :class:&#x60;BillingRollup&#x60;. Buckets with zero cost are omitted from the breakdown (no empty days).
     * <p><b>200</b> - Successful response
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param period The period parameter
     * @param dateFrom The dateFrom parameter
     * @param dateTo The dateTo parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return ResponseEntity&lt;BillingRollup&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<BillingRollup>> rollupWithHttpInfo(@jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable String period, @jakarta.annotation.Nullable String dateFrom, @jakarta.annotation.Nullable String dateTo, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        ParameterizedTypeReference<BillingRollup> localVarReturnType = new ParameterizedTypeReference<BillingRollup>() {};
        return rollupRequestCreation(xTenantId, xWorkspaceId, period, dateFrom, dateTo, xCorrelationId).toEntity(localVarReturnType);
    }

    /**
     * Aggregate LLM cost into &#x60;&#x60;day&#x60;&#x60; / &#x60;&#x60;week&#x60;&#x60; / &#x60;&#x60;month&#x60;&#x60; buckets.
     * Query params ------------ * &#x60;&#x60;period&#x60;&#x60;    -- &#x60;&#x60;day&#x60;&#x60; (default) / &#x60;&#x60;week&#x60;&#x60; / &#x60;&#x60;month&#x60;&#x60; * &#x60;&#x60;date_from&#x60;&#x60; -- inclusive lower bound on &#x60;&#x60;created_at&#x60;&#x60; * &#x60;&#x60;date_to&#x60;&#x60;   -- exclusive upper bound on &#x60;&#x60;created_at&#x60;&#x60;  Response shape: :class:&#x60;BillingRollup&#x60;. Buckets with zero cost are omitted from the breakdown (no empty days).
     * <p><b>200</b> - Successful response
     * @param xTenantId Tenant slug. Required on every non-agent endpoint -- bounds the row-level security policy and appears in every audit event. Must match the JWT tenant claim if Authorization is also present.
     * @param xWorkspaceId Workspace identifier. Accepts either the workspace UUID or its slug -- the slug form lets SDKs avoid carrying UUIDs around. Used to scope every query, ingest, and schema KB operation.
     * @param period The period parameter
     * @param dateFrom The dateFrom parameter
     * @param dateTo The dateTo parameter
     * @param xCorrelationId Optional client-supplied correlation id. The service uses this in every log line and downstream call. If absent the service mints a new UUID and echoes it in the response header.
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec rollupWithResponseSpec(@jakarta.annotation.Nonnull String xTenantId, @jakarta.annotation.Nonnull String xWorkspaceId, @jakarta.annotation.Nullable String period, @jakarta.annotation.Nullable String dateFrom, @jakarta.annotation.Nullable String dateTo, @jakarta.annotation.Nullable UUID xCorrelationId) throws WebClientResponseException {
        return rollupRequestCreation(xTenantId, xWorkspaceId, period, dateFrom, dateTo, xCorrelationId);
    }
}
