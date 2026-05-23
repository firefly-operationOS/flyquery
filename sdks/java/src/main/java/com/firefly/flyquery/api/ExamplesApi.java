package com.firefly.flyquery.api;

import com.firefly.flyquery.ApiClient;

import com.firefly.flyquery.model.ExampleCreate;
import com.firefly.flyquery.model.ExampleRead;
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

@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaClientCodegen", date = "2026-05-23T20:01:27.049906+02:00[Europe/Madrid]", comments = "Generator version: 7.22.0")
public class ExamplesApi {
    private ApiClient apiClient;

    public ExamplesApi() {
        this(new ApiClient());
    }

    public ExamplesApi(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    public ApiClient getApiClient() {
        return apiClient;
    }

    public void setApiClient(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    /**
     * Approve an example (quality → APPROVED).
     * 
     * <p><b>200</b> - Successful response
     * @param exampleId The exampleId parameter
     * @return ExampleRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec approveRequestCreation(@javax.annotation.Nullable String exampleId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'exampleId' is set
        if (exampleId == null) {
            throw new WebClientResponseException("Missing the required parameter 'exampleId' when calling approve", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("example_id", exampleId);

        final MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<String, String>();
        final HttpHeaders headerParams = new HttpHeaders();
        final MultiValueMap<String, String> cookieParams = new LinkedMultiValueMap<String, String>();
        final MultiValueMap<String, Object> formParams = new LinkedMultiValueMap<String, Object>();

        final String[] localVarAccepts = { 
            "application/json"
        };
        final List<MediaType> localVarAccept = apiClient.selectHeaderAccept(localVarAccepts);
        final String[] localVarContentTypes = { };
        final MediaType localVarContentType = apiClient.selectHeaderContentType(localVarContentTypes);

        String[] localVarAuthNames = new String[] {  };

        ParameterizedTypeReference<ExampleRead> localVarReturnType = new ParameterizedTypeReference<ExampleRead>() {};
        return apiClient.invokeAPI("/api/v1/examples/{example_id}:approve", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Approve an example (quality → APPROVED).
     * 
     * <p><b>200</b> - Successful response
     * @param exampleId The exampleId parameter
     * @return ExampleRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ExampleRead> approve(@javax.annotation.Nullable String exampleId) throws WebClientResponseException {
        ParameterizedTypeReference<ExampleRead> localVarReturnType = new ParameterizedTypeReference<ExampleRead>() {};
        return approveRequestCreation(exampleId).bodyToMono(localVarReturnType);
    }

    /**
     * Approve an example (quality → APPROVED).
     * 
     * <p><b>200</b> - Successful response
     * @param exampleId The exampleId parameter
     * @return ResponseEntity&lt;ExampleRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<ExampleRead>> approveWithHttpInfo(@javax.annotation.Nullable String exampleId) throws WebClientResponseException {
        ParameterizedTypeReference<ExampleRead> localVarReturnType = new ParameterizedTypeReference<ExampleRead>() {};
        return approveRequestCreation(exampleId).toEntity(localVarReturnType);
    }

    /**
     * Approve an example (quality → APPROVED).
     * 
     * <p><b>200</b> - Successful response
     * @param exampleId The exampleId parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec approveWithResponseSpec(@javax.annotation.Nullable String exampleId) throws WebClientResponseException {
        return approveRequestCreation(exampleId);
    }

    /**
     * Create an example; defaults to source&#x3D;USER_CURATED, quality&#x3D;PROPOSED.
     * 
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param exampleCreate The exampleCreate parameter
     * @return ExampleRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec createRequestCreation(@javax.annotation.Nonnull ExampleCreate exampleCreate) throws WebClientResponseException {
        Object postBody = exampleCreate;
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

        final String[] localVarAccepts = { 
            "application/json"
        };
        final List<MediaType> localVarAccept = apiClient.selectHeaderAccept(localVarAccepts);
        final String[] localVarContentTypes = { 
            "application/json"
        };
        final MediaType localVarContentType = apiClient.selectHeaderContentType(localVarContentTypes);

        String[] localVarAuthNames = new String[] {  };

        ParameterizedTypeReference<ExampleRead> localVarReturnType = new ParameterizedTypeReference<ExampleRead>() {};
        return apiClient.invokeAPI("/api/v1/examples", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Create an example; defaults to source&#x3D;USER_CURATED, quality&#x3D;PROPOSED.
     * 
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param exampleCreate The exampleCreate parameter
     * @return ExampleRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ExampleRead> create(@javax.annotation.Nonnull ExampleCreate exampleCreate) throws WebClientResponseException {
        ParameterizedTypeReference<ExampleRead> localVarReturnType = new ParameterizedTypeReference<ExampleRead>() {};
        return createRequestCreation(exampleCreate).bodyToMono(localVarReturnType);
    }

    /**
     * Create an example; defaults to source&#x3D;USER_CURATED, quality&#x3D;PROPOSED.
     * 
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param exampleCreate The exampleCreate parameter
     * @return ResponseEntity&lt;ExampleRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<ExampleRead>> createWithHttpInfo(@javax.annotation.Nonnull ExampleCreate exampleCreate) throws WebClientResponseException {
        ParameterizedTypeReference<ExampleRead> localVarReturnType = new ParameterizedTypeReference<ExampleRead>() {};
        return createRequestCreation(exampleCreate).toEntity(localVarReturnType);
    }

    /**
     * Create an example; defaults to source&#x3D;USER_CURATED, quality&#x3D;PROPOSED.
     * 
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param exampleCreate The exampleCreate parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec createWithResponseSpec(@javax.annotation.Nonnull ExampleCreate exampleCreate) throws WebClientResponseException {
        return createRequestCreation(exampleCreate);
    }

    /**
     * List examples for the caller&#39;s workspace, with optional filters.
     * 
     * <p><b>200</b> - Successful response
     * @param quality The quality parameter
     * @param datasetId The datasetId parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec listExamplesRequestCreation(@javax.annotation.Nullable String quality, @javax.annotation.Nullable String datasetId) throws WebClientResponseException {
        Object postBody = null;
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        final MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<String, String>();
        final HttpHeaders headerParams = new HttpHeaders();
        final MultiValueMap<String, String> cookieParams = new LinkedMultiValueMap<String, String>();
        final MultiValueMap<String, Object> formParams = new LinkedMultiValueMap<String, Object>();

        queryParams.putAll(apiClient.parameterToMultiValueMap(null, "quality", quality));
        queryParams.putAll(apiClient.parameterToMultiValueMap(null, "dataset_id", datasetId));

        final String[] localVarAccepts = { };
        final List<MediaType> localVarAccept = apiClient.selectHeaderAccept(localVarAccepts);
        final String[] localVarContentTypes = { };
        final MediaType localVarContentType = apiClient.selectHeaderContentType(localVarContentTypes);

        String[] localVarAuthNames = new String[] {  };

        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return apiClient.invokeAPI("/api/v1/examples", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * List examples for the caller&#39;s workspace, with optional filters.
     * 
     * <p><b>200</b> - Successful response
     * @param quality The quality parameter
     * @param datasetId The datasetId parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<Void> listExamples(@javax.annotation.Nullable String quality, @javax.annotation.Nullable String datasetId) throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return listExamplesRequestCreation(quality, datasetId).bodyToMono(localVarReturnType);
    }

    /**
     * List examples for the caller&#39;s workspace, with optional filters.
     * 
     * <p><b>200</b> - Successful response
     * @param quality The quality parameter
     * @param datasetId The datasetId parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<Void>> listExamplesWithHttpInfo(@javax.annotation.Nullable String quality, @javax.annotation.Nullable String datasetId) throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return listExamplesRequestCreation(quality, datasetId).toEntity(localVarReturnType);
    }

    /**
     * List examples for the caller&#39;s workspace, with optional filters.
     * 
     * <p><b>200</b> - Successful response
     * @param quality The quality parameter
     * @param datasetId The datasetId parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec listExamplesWithResponseSpec(@javax.annotation.Nullable String quality, @javax.annotation.Nullable String datasetId) throws WebClientResponseException {
        return listExamplesRequestCreation(quality, datasetId);
    }

    /**
     * Reject an example (quality → REJECTED).
     * 
     * <p><b>200</b> - Successful response
     * @param exampleId The exampleId parameter
     * @return ExampleRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec rejectRequestCreation(@javax.annotation.Nonnull String exampleId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'exampleId' is set
        if (exampleId == null) {
            throw new WebClientResponseException("Missing the required parameter 'exampleId' when calling reject", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("example_id", exampleId);

        final MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<String, String>();
        final HttpHeaders headerParams = new HttpHeaders();
        final MultiValueMap<String, String> cookieParams = new LinkedMultiValueMap<String, String>();
        final MultiValueMap<String, Object> formParams = new LinkedMultiValueMap<String, Object>();

        final String[] localVarAccepts = { 
            "application/json"
        };
        final List<MediaType> localVarAccept = apiClient.selectHeaderAccept(localVarAccepts);
        final String[] localVarContentTypes = { };
        final MediaType localVarContentType = apiClient.selectHeaderContentType(localVarContentTypes);

        String[] localVarAuthNames = new String[] {  };

        ParameterizedTypeReference<ExampleRead> localVarReturnType = new ParameterizedTypeReference<ExampleRead>() {};
        return apiClient.invokeAPI("/api/v1/examples/{example_id}:reject", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Reject an example (quality → REJECTED).
     * 
     * <p><b>200</b> - Successful response
     * @param exampleId The exampleId parameter
     * @return ExampleRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ExampleRead> reject(@javax.annotation.Nonnull String exampleId) throws WebClientResponseException {
        ParameterizedTypeReference<ExampleRead> localVarReturnType = new ParameterizedTypeReference<ExampleRead>() {};
        return rejectRequestCreation(exampleId).bodyToMono(localVarReturnType);
    }

    /**
     * Reject an example (quality → REJECTED).
     * 
     * <p><b>200</b> - Successful response
     * @param exampleId The exampleId parameter
     * @return ResponseEntity&lt;ExampleRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<ExampleRead>> rejectWithHttpInfo(@javax.annotation.Nonnull String exampleId) throws WebClientResponseException {
        ParameterizedTypeReference<ExampleRead> localVarReturnType = new ParameterizedTypeReference<ExampleRead>() {};
        return rejectRequestCreation(exampleId).toEntity(localVarReturnType);
    }

    /**
     * Reject an example (quality → REJECTED).
     * 
     * <p><b>200</b> - Successful response
     * @param exampleId The exampleId parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec rejectWithResponseSpec(@javax.annotation.Nonnull String exampleId) throws WebClientResponseException {
        return rejectRequestCreation(exampleId);
    }
}
