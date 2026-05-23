package com.firefly.flyquery.api;

import com.firefly.flyquery.ApiClient;

import com.firefly.flyquery.model.HTTPValidationError;
import com.firefly.flyquery.model.SemanticMetricCreate;
import com.firefly.flyquery.model.SemanticMetricRead;
import com.firefly.flyquery.model.SemanticMetricUpdate;

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
public class SemanticMetricsApi {
    private ApiClient apiClient;

    public SemanticMetricsApi() {
        this(new ApiClient());
    }

    public SemanticMetricsApi(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    public ApiClient getApiClient() {
        return apiClient;
    }

    public void setApiClient(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    /**
     * Create a new semantic metric in DRAFT status.
     * 
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param semanticMetricCreate The semanticMetricCreate parameter
     * @return SemanticMetricRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec createRequestCreation(@javax.annotation.Nonnull SemanticMetricCreate semanticMetricCreate) throws WebClientResponseException {
        Object postBody = semanticMetricCreate;
        // verify the required parameter 'semanticMetricCreate' is set
        if (semanticMetricCreate == null) {
            throw new WebClientResponseException("Missing the required parameter 'semanticMetricCreate' when calling create", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
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

        ParameterizedTypeReference<SemanticMetricRead> localVarReturnType = new ParameterizedTypeReference<SemanticMetricRead>() {};
        return apiClient.invokeAPI("/api/v1/semantic/metrics", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Create a new semantic metric in DRAFT status.
     * 
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param semanticMetricCreate The semanticMetricCreate parameter
     * @return SemanticMetricRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<SemanticMetricRead> create(@javax.annotation.Nonnull SemanticMetricCreate semanticMetricCreate) throws WebClientResponseException {
        ParameterizedTypeReference<SemanticMetricRead> localVarReturnType = new ParameterizedTypeReference<SemanticMetricRead>() {};
        return createRequestCreation(semanticMetricCreate).bodyToMono(localVarReturnType);
    }

    /**
     * Create a new semantic metric in DRAFT status.
     * 
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param semanticMetricCreate The semanticMetricCreate parameter
     * @return ResponseEntity&lt;SemanticMetricRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<SemanticMetricRead>> createWithHttpInfo(@javax.annotation.Nonnull SemanticMetricCreate semanticMetricCreate) throws WebClientResponseException {
        ParameterizedTypeReference<SemanticMetricRead> localVarReturnType = new ParameterizedTypeReference<SemanticMetricRead>() {};
        return createRequestCreation(semanticMetricCreate).toEntity(localVarReturnType);
    }

    /**
     * Create a new semantic metric in DRAFT status.
     * 
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param semanticMetricCreate The semanticMetricCreate parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec createWithResponseSpec(@javax.annotation.Nonnull SemanticMetricCreate semanticMetricCreate) throws WebClientResponseException {
        return createRequestCreation(semanticMetricCreate);
    }

    /**
     * Fetch a single semantic metric by id.
     * 
     * <p><b>200</b> - Successful response
     * @param metricId The metricId parameter
     * @return SemanticMetricRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec getMetricRequestCreation(@javax.annotation.Nullable String metricId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'metricId' is set
        if (metricId == null) {
            throw new WebClientResponseException("Missing the required parameter 'metricId' when calling getMetric", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("metric_id", metricId);

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

        ParameterizedTypeReference<SemanticMetricRead> localVarReturnType = new ParameterizedTypeReference<SemanticMetricRead>() {};
        return apiClient.invokeAPI("/api/v1/semantic/metrics/{metric_id}", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Fetch a single semantic metric by id.
     * 
     * <p><b>200</b> - Successful response
     * @param metricId The metricId parameter
     * @return SemanticMetricRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<SemanticMetricRead> getMetric(@javax.annotation.Nullable String metricId) throws WebClientResponseException {
        ParameterizedTypeReference<SemanticMetricRead> localVarReturnType = new ParameterizedTypeReference<SemanticMetricRead>() {};
        return getMetricRequestCreation(metricId).bodyToMono(localVarReturnType);
    }

    /**
     * Fetch a single semantic metric by id.
     * 
     * <p><b>200</b> - Successful response
     * @param metricId The metricId parameter
     * @return ResponseEntity&lt;SemanticMetricRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<SemanticMetricRead>> getMetricWithHttpInfo(@javax.annotation.Nullable String metricId) throws WebClientResponseException {
        ParameterizedTypeReference<SemanticMetricRead> localVarReturnType = new ParameterizedTypeReference<SemanticMetricRead>() {};
        return getMetricRequestCreation(metricId).toEntity(localVarReturnType);
    }

    /**
     * Fetch a single semantic metric by id.
     * 
     * <p><b>200</b> - Successful response
     * @param metricId The metricId parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec getMetricWithResponseSpec(@javax.annotation.Nullable String metricId) throws WebClientResponseException {
        return getMetricRequestCreation(metricId);
    }

    /**
     * Return version history for a metric, oldest first.
     * 
     * <p><b>200</b> - Successful response
     * @param metricId The metricId parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec historyRequestCreation(@javax.annotation.Nonnull String metricId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'metricId' is set
        if (metricId == null) {
            throw new WebClientResponseException("Missing the required parameter 'metricId' when calling history", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("metric_id", metricId);

        final MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<String, String>();
        final HttpHeaders headerParams = new HttpHeaders();
        final MultiValueMap<String, String> cookieParams = new LinkedMultiValueMap<String, String>();
        final MultiValueMap<String, Object> formParams = new LinkedMultiValueMap<String, Object>();

        final String[] localVarAccepts = { };
        final List<MediaType> localVarAccept = apiClient.selectHeaderAccept(localVarAccepts);
        final String[] localVarContentTypes = { };
        final MediaType localVarContentType = apiClient.selectHeaderContentType(localVarContentTypes);

        String[] localVarAuthNames = new String[] {  };

        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return apiClient.invokeAPI("/api/v1/semantic/metrics/{metric_id}/history", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Return version history for a metric, oldest first.
     * 
     * <p><b>200</b> - Successful response
     * @param metricId The metricId parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<Void> history(@javax.annotation.Nonnull String metricId) throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return historyRequestCreation(metricId).bodyToMono(localVarReturnType);
    }

    /**
     * Return version history for a metric, oldest first.
     * 
     * <p><b>200</b> - Successful response
     * @param metricId The metricId parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<Void>> historyWithHttpInfo(@javax.annotation.Nonnull String metricId) throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return historyRequestCreation(metricId).toEntity(localVarReturnType);
    }

    /**
     * Return version history for a metric, oldest first.
     * 
     * <p><b>200</b> - Successful response
     * @param metricId The metricId parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec historyWithResponseSpec(@javax.annotation.Nonnull String metricId) throws WebClientResponseException {
        return historyRequestCreation(metricId);
    }

    /**
     * List all semantic metrics for the caller&#39;s workspace.
     * 
     * <p><b>200</b> - Successful response
     * @param datasetId The datasetId parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec listMetricsRequestCreation(@javax.annotation.Nullable String datasetId) throws WebClientResponseException {
        Object postBody = null;
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        final MultiValueMap<String, String> queryParams = new LinkedMultiValueMap<String, String>();
        final HttpHeaders headerParams = new HttpHeaders();
        final MultiValueMap<String, String> cookieParams = new LinkedMultiValueMap<String, String>();
        final MultiValueMap<String, Object> formParams = new LinkedMultiValueMap<String, Object>();

        queryParams.putAll(apiClient.parameterToMultiValueMap(null, "dataset_id", datasetId));

        final String[] localVarAccepts = { };
        final List<MediaType> localVarAccept = apiClient.selectHeaderAccept(localVarAccepts);
        final String[] localVarContentTypes = { };
        final MediaType localVarContentType = apiClient.selectHeaderContentType(localVarContentTypes);

        String[] localVarAuthNames = new String[] {  };

        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return apiClient.invokeAPI("/api/v1/semantic/metrics", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * List all semantic metrics for the caller&#39;s workspace.
     * 
     * <p><b>200</b> - Successful response
     * @param datasetId The datasetId parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<Void> listMetrics(@javax.annotation.Nullable String datasetId) throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return listMetricsRequestCreation(datasetId).bodyToMono(localVarReturnType);
    }

    /**
     * List all semantic metrics for the caller&#39;s workspace.
     * 
     * <p><b>200</b> - Successful response
     * @param datasetId The datasetId parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<Void>> listMetricsWithHttpInfo(@javax.annotation.Nullable String datasetId) throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return listMetricsRequestCreation(datasetId).toEntity(localVarReturnType);
    }

    /**
     * List all semantic metrics for the caller&#39;s workspace.
     * 
     * <p><b>200</b> - Successful response
     * @param datasetId The datasetId parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec listMetricsWithResponseSpec(@javax.annotation.Nullable String datasetId) throws WebClientResponseException {
        return listMetricsRequestCreation(datasetId);
    }

    /**
     * Validate, compile, and publish a metric (status → PUBLISHED).
     * 
     * <p><b>200</b> - Successful response
     * @param metricId The metricId parameter
     * @return SemanticMetricRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec publishRequestCreation(@javax.annotation.Nonnull String metricId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'metricId' is set
        if (metricId == null) {
            throw new WebClientResponseException("Missing the required parameter 'metricId' when calling publish", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("metric_id", metricId);

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

        ParameterizedTypeReference<SemanticMetricRead> localVarReturnType = new ParameterizedTypeReference<SemanticMetricRead>() {};
        return apiClient.invokeAPI("/api/v1/semantic/metrics/{metric_id}:publish", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Validate, compile, and publish a metric (status → PUBLISHED).
     * 
     * <p><b>200</b> - Successful response
     * @param metricId The metricId parameter
     * @return SemanticMetricRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<SemanticMetricRead> publish(@javax.annotation.Nonnull String metricId) throws WebClientResponseException {
        ParameterizedTypeReference<SemanticMetricRead> localVarReturnType = new ParameterizedTypeReference<SemanticMetricRead>() {};
        return publishRequestCreation(metricId).bodyToMono(localVarReturnType);
    }

    /**
     * Validate, compile, and publish a metric (status → PUBLISHED).
     * 
     * <p><b>200</b> - Successful response
     * @param metricId The metricId parameter
     * @return ResponseEntity&lt;SemanticMetricRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<SemanticMetricRead>> publishWithHttpInfo(@javax.annotation.Nonnull String metricId) throws WebClientResponseException {
        ParameterizedTypeReference<SemanticMetricRead> localVarReturnType = new ParameterizedTypeReference<SemanticMetricRead>() {};
        return publishRequestCreation(metricId).toEntity(localVarReturnType);
    }

    /**
     * Validate, compile, and publish a metric (status → PUBLISHED).
     * 
     * <p><b>200</b> - Successful response
     * @param metricId The metricId parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec publishWithResponseSpec(@javax.annotation.Nonnull String metricId) throws WebClientResponseException {
        return publishRequestCreation(metricId);
    }

    /**
     * Retire a metric (status → RETIRED).
     * 
     * <p><b>200</b> - Successful response
     * @param metricId The metricId parameter
     * @return SemanticMetricRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec retireRequestCreation(@javax.annotation.Nonnull String metricId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'metricId' is set
        if (metricId == null) {
            throw new WebClientResponseException("Missing the required parameter 'metricId' when calling retire", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("metric_id", metricId);

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

        ParameterizedTypeReference<SemanticMetricRead> localVarReturnType = new ParameterizedTypeReference<SemanticMetricRead>() {};
        return apiClient.invokeAPI("/api/v1/semantic/metrics/{metric_id}:retire", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Retire a metric (status → RETIRED).
     * 
     * <p><b>200</b> - Successful response
     * @param metricId The metricId parameter
     * @return SemanticMetricRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<SemanticMetricRead> retire(@javax.annotation.Nonnull String metricId) throws WebClientResponseException {
        ParameterizedTypeReference<SemanticMetricRead> localVarReturnType = new ParameterizedTypeReference<SemanticMetricRead>() {};
        return retireRequestCreation(metricId).bodyToMono(localVarReturnType);
    }

    /**
     * Retire a metric (status → RETIRED).
     * 
     * <p><b>200</b> - Successful response
     * @param metricId The metricId parameter
     * @return ResponseEntity&lt;SemanticMetricRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<SemanticMetricRead>> retireWithHttpInfo(@javax.annotation.Nonnull String metricId) throws WebClientResponseException {
        ParameterizedTypeReference<SemanticMetricRead> localVarReturnType = new ParameterizedTypeReference<SemanticMetricRead>() {};
        return retireRequestCreation(metricId).toEntity(localVarReturnType);
    }

    /**
     * Retire a metric (status → RETIRED).
     * 
     * <p><b>200</b> - Successful response
     * @param metricId The metricId parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec retireWithResponseSpec(@javax.annotation.Nonnull String metricId) throws WebClientResponseException {
        return retireRequestCreation(metricId);
    }

    /**
     * Sparse-update a metric; re-validates YAML if definition changes.
     * 
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param metricId The metricId parameter
     * @param semanticMetricUpdate The semanticMetricUpdate parameter
     * @return SemanticMetricRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec updateRequestCreation(@javax.annotation.Nonnull String metricId, @javax.annotation.Nonnull SemanticMetricUpdate semanticMetricUpdate) throws WebClientResponseException {
        Object postBody = semanticMetricUpdate;
        // verify the required parameter 'metricId' is set
        if (metricId == null) {
            throw new WebClientResponseException("Missing the required parameter 'metricId' when calling update", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // verify the required parameter 'semanticMetricUpdate' is set
        if (semanticMetricUpdate == null) {
            throw new WebClientResponseException("Missing the required parameter 'semanticMetricUpdate' when calling update", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("metric_id", metricId);

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

        ParameterizedTypeReference<SemanticMetricRead> localVarReturnType = new ParameterizedTypeReference<SemanticMetricRead>() {};
        return apiClient.invokeAPI("/api/v1/semantic/metrics/{metric_id}", HttpMethod.PUT, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Sparse-update a metric; re-validates YAML if definition changes.
     * 
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param metricId The metricId parameter
     * @param semanticMetricUpdate The semanticMetricUpdate parameter
     * @return SemanticMetricRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<SemanticMetricRead> update(@javax.annotation.Nonnull String metricId, @javax.annotation.Nonnull SemanticMetricUpdate semanticMetricUpdate) throws WebClientResponseException {
        ParameterizedTypeReference<SemanticMetricRead> localVarReturnType = new ParameterizedTypeReference<SemanticMetricRead>() {};
        return updateRequestCreation(metricId, semanticMetricUpdate).bodyToMono(localVarReturnType);
    }

    /**
     * Sparse-update a metric; re-validates YAML if definition changes.
     * 
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param metricId The metricId parameter
     * @param semanticMetricUpdate The semanticMetricUpdate parameter
     * @return ResponseEntity&lt;SemanticMetricRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<SemanticMetricRead>> updateWithHttpInfo(@javax.annotation.Nonnull String metricId, @javax.annotation.Nonnull SemanticMetricUpdate semanticMetricUpdate) throws WebClientResponseException {
        ParameterizedTypeReference<SemanticMetricRead> localVarReturnType = new ParameterizedTypeReference<SemanticMetricRead>() {};
        return updateRequestCreation(metricId, semanticMetricUpdate).toEntity(localVarReturnType);
    }

    /**
     * Sparse-update a metric; re-validates YAML if definition changes.
     * 
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param metricId The metricId parameter
     * @param semanticMetricUpdate The semanticMetricUpdate parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec updateWithResponseSpec(@javax.annotation.Nonnull String metricId, @javax.annotation.Nonnull SemanticMetricUpdate semanticMetricUpdate) throws WebClientResponseException {
        return updateRequestCreation(metricId, semanticMetricUpdate);
    }
}
