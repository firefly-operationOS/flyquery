package com.firefly.flyquery.api;

import com.firefly.flyquery.ApiClient;

import com.firefly.flyquery.model.DeriveTableRequest;
import com.firefly.flyquery.model.DeriveTableResponse;
import com.firefly.flyquery.model.HTTPValidationError;

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

@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaClientCodegen", date = "2026-05-24T00:36:39.059958+02:00[Europe/Madrid]", comments = "Generator version: 7.22.0")
public class TablesDeriveApi {
    private ApiClient apiClient;

    public TablesDeriveApi() {
        this(new ApiClient());
    }

    public TablesDeriveApi(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    public ApiClient getApiClient() {
        return apiClient;
    }

    public void setApiClient(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    /**
     * Materialise a SELECT result as a new DERIVED table.
     * :param http_request: Starlette request (tenant context headers) :param body: dataset_id + name + sql (must be a SELECT) :return: DeriveTableResponse with the new table_id :raises DeriveTableForbidden: when sql is not a SELECT :raises DeriveTableError: when DuckDB execution fails
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param deriveTableRequest The deriveTableRequest parameter
     * @return DeriveTableResponse
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec deriveRequestCreation(@javax.annotation.Nonnull DeriveTableRequest deriveTableRequest) throws WebClientResponseException {
        Object postBody = deriveTableRequest;
        // verify the required parameter 'deriveTableRequest' is set
        if (deriveTableRequest == null) {
            throw new WebClientResponseException("Missing the required parameter 'deriveTableRequest' when calling derive", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        final MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<String, String>();
        final HttpHeaders headerParams = new HttpHeaders();
        final MultiValueMap<String, String> cookieParams = new LinkedMultiValueMap<String, String>();
        final MultiValueMap<String, Object> formParams = new LinkedMultiValueMap<String, Object>();

        final String[] localVarAccepts = { 
            "application/json"
        };
        final List<MediaType> localVarAccept = apiClient.selectHeaderAccept(localVarAccepts);
        final String[] localVarContentTypes = { 
            "application/json"
        };
        final MediaType localVarContentType = apiClient.selectHeaderContentType(localVarContentTypes);

        String[] localVarAuthNames = new String[] {  };

        ParameterizedTypeReference<DeriveTableResponse> localVarReturnType = new ParameterizedTypeReference<DeriveTableResponse>() {};
        return apiClient.invokeAPI("/api/v1/tables:derive", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Materialise a SELECT result as a new DERIVED table.
     * :param http_request: Starlette request (tenant context headers) :param body: dataset_id + name + sql (must be a SELECT) :return: DeriveTableResponse with the new table_id :raises DeriveTableForbidden: when sql is not a SELECT :raises DeriveTableError: when DuckDB execution fails
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param deriveTableRequest The deriveTableRequest parameter
     * @return DeriveTableResponse
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<DeriveTableResponse> derive(@javax.annotation.Nonnull DeriveTableRequest deriveTableRequest) throws WebClientResponseException {
        ParameterizedTypeReference<DeriveTableResponse> localVarReturnType = new ParameterizedTypeReference<DeriveTableResponse>() {};
        return deriveRequestCreation(deriveTableRequest).bodyToMono(localVarReturnType);
    }

    /**
     * Materialise a SELECT result as a new DERIVED table.
     * :param http_request: Starlette request (tenant context headers) :param body: dataset_id + name + sql (must be a SELECT) :return: DeriveTableResponse with the new table_id :raises DeriveTableForbidden: when sql is not a SELECT :raises DeriveTableError: when DuckDB execution fails
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param deriveTableRequest The deriveTableRequest parameter
     * @return ResponseEntity&lt;DeriveTableResponse&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<DeriveTableResponse>> deriveWithHttpInfo(@javax.annotation.Nonnull DeriveTableRequest deriveTableRequest) throws WebClientResponseException {
        ParameterizedTypeReference<DeriveTableResponse> localVarReturnType = new ParameterizedTypeReference<DeriveTableResponse>() {};
        return deriveRequestCreation(deriveTableRequest).toEntity(localVarReturnType);
    }

    /**
     * Materialise a SELECT result as a new DERIVED table.
     * :param http_request: Starlette request (tenant context headers) :param body: dataset_id + name + sql (must be a SELECT) :return: DeriveTableResponse with the new table_id :raises DeriveTableForbidden: when sql is not a SELECT :raises DeriveTableError: when DuckDB execution fails
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param deriveTableRequest The deriveTableRequest parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec deriveWithResponseSpec(@javax.annotation.Nonnull DeriveTableRequest deriveTableRequest) throws WebClientResponseException {
        return deriveRequestCreation(deriveTableRequest);
    }
}
