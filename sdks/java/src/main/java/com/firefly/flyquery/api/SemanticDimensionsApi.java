package com.firefly.flyquery.api;

import com.firefly.flyquery.ApiClient;

import com.firefly.flyquery.model.HTTPValidationError;
import com.firefly.flyquery.model.SemanticDimensionCreate;
import com.firefly.flyquery.model.SemanticDimensionRead;
import com.firefly.flyquery.model.SemanticDimensionUpdate;

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
     * @param semanticDimensionCreate The semanticDimensionCreate parameter
     * @return SemanticDimensionRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec createRequestCreation(@javax.annotation.Nonnull SemanticDimensionCreate semanticDimensionCreate) throws WebClientResponseException {
        Object postBody = semanticDimensionCreate;
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

        final String[] localVarAccepts = { 
            "application/json"
        };
        final List<MediaType> localVarAccept = apiClient.selectHeaderAccept(localVarAccepts);
        final String[] localVarContentTypes = { 
            "application/json"
        };
        final MediaType localVarContentType = apiClient.selectHeaderContentType(localVarContentTypes);

        String[] localVarAuthNames = new String[] {  };

        ParameterizedTypeReference<SemanticDimensionRead> localVarReturnType = new ParameterizedTypeReference<SemanticDimensionRead>() {};
        return apiClient.invokeAPI("/api/v1/semantic/dimensions", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Create a new semantic dimension in DRAFT status.
     * 
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param semanticDimensionCreate The semanticDimensionCreate parameter
     * @return SemanticDimensionRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<SemanticDimensionRead> create(@javax.annotation.Nonnull SemanticDimensionCreate semanticDimensionCreate) throws WebClientResponseException {
        ParameterizedTypeReference<SemanticDimensionRead> localVarReturnType = new ParameterizedTypeReference<SemanticDimensionRead>() {};
        return createRequestCreation(semanticDimensionCreate).bodyToMono(localVarReturnType);
    }

    /**
     * Create a new semantic dimension in DRAFT status.
     * 
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param semanticDimensionCreate The semanticDimensionCreate parameter
     * @return ResponseEntity&lt;SemanticDimensionRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<SemanticDimensionRead>> createWithHttpInfo(@javax.annotation.Nonnull SemanticDimensionCreate semanticDimensionCreate) throws WebClientResponseException {
        ParameterizedTypeReference<SemanticDimensionRead> localVarReturnType = new ParameterizedTypeReference<SemanticDimensionRead>() {};
        return createRequestCreation(semanticDimensionCreate).toEntity(localVarReturnType);
    }

    /**
     * Create a new semantic dimension in DRAFT status.
     * 
     * <p><b>201</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param semanticDimensionCreate The semanticDimensionCreate parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec createWithResponseSpec(@javax.annotation.Nonnull SemanticDimensionCreate semanticDimensionCreate) throws WebClientResponseException {
        return createRequestCreation(semanticDimensionCreate);
    }

    /**
     * Fetch a single semantic dimension by id.
     * 
     * <p><b>200</b> - Successful response
     * @param dimensionId The dimensionId parameter
     * @return SemanticDimensionRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec getDimensionRequestCreation(@javax.annotation.Nullable String dimensionId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'dimensionId' is set
        if (dimensionId == null) {
            throw new WebClientResponseException("Missing the required parameter 'dimensionId' when calling getDimension", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("dimension_id", dimensionId);

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

        ParameterizedTypeReference<SemanticDimensionRead> localVarReturnType = new ParameterizedTypeReference<SemanticDimensionRead>() {};
        return apiClient.invokeAPI("/api/v1/semantic/dimensions/{dimension_id}", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Fetch a single semantic dimension by id.
     * 
     * <p><b>200</b> - Successful response
     * @param dimensionId The dimensionId parameter
     * @return SemanticDimensionRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<SemanticDimensionRead> getDimension(@javax.annotation.Nullable String dimensionId) throws WebClientResponseException {
        ParameterizedTypeReference<SemanticDimensionRead> localVarReturnType = new ParameterizedTypeReference<SemanticDimensionRead>() {};
        return getDimensionRequestCreation(dimensionId).bodyToMono(localVarReturnType);
    }

    /**
     * Fetch a single semantic dimension by id.
     * 
     * <p><b>200</b> - Successful response
     * @param dimensionId The dimensionId parameter
     * @return ResponseEntity&lt;SemanticDimensionRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<SemanticDimensionRead>> getDimensionWithHttpInfo(@javax.annotation.Nullable String dimensionId) throws WebClientResponseException {
        ParameterizedTypeReference<SemanticDimensionRead> localVarReturnType = new ParameterizedTypeReference<SemanticDimensionRead>() {};
        return getDimensionRequestCreation(dimensionId).toEntity(localVarReturnType);
    }

    /**
     * Fetch a single semantic dimension by id.
     * 
     * <p><b>200</b> - Successful response
     * @param dimensionId The dimensionId parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec getDimensionWithResponseSpec(@javax.annotation.Nullable String dimensionId) throws WebClientResponseException {
        return getDimensionRequestCreation(dimensionId);
    }

    /**
     * Return version history for a dimension, oldest first.
     * 
     * <p><b>200</b> - Successful response
     * @param dimensionId The dimensionId parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec historyRequestCreation(@javax.annotation.Nonnull String dimensionId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'dimensionId' is set
        if (dimensionId == null) {
            throw new WebClientResponseException("Missing the required parameter 'dimensionId' when calling history", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("dimension_id", dimensionId);

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
        return apiClient.invokeAPI("/api/v1/semantic/dimensions/{dimension_id}/history", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Return version history for a dimension, oldest first.
     * 
     * <p><b>200</b> - Successful response
     * @param dimensionId The dimensionId parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<Void> history(@javax.annotation.Nonnull String dimensionId) throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return historyRequestCreation(dimensionId).bodyToMono(localVarReturnType);
    }

    /**
     * Return version history for a dimension, oldest first.
     * 
     * <p><b>200</b> - Successful response
     * @param dimensionId The dimensionId parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<Void>> historyWithHttpInfo(@javax.annotation.Nonnull String dimensionId) throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return historyRequestCreation(dimensionId).toEntity(localVarReturnType);
    }

    /**
     * Return version history for a dimension, oldest first.
     * 
     * <p><b>200</b> - Successful response
     * @param dimensionId The dimensionId parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec historyWithResponseSpec(@javax.annotation.Nonnull String dimensionId) throws WebClientResponseException {
        return historyRequestCreation(dimensionId);
    }

    /**
     * List all semantic dimensions for the caller&#39;s workspace.
     * 
     * <p><b>200</b> - Successful response
     * @param datasetId The datasetId parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec listDimensionsRequestCreation(@javax.annotation.Nullable String datasetId) throws WebClientResponseException {
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
        return apiClient.invokeAPI("/api/v1/semantic/dimensions", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * List all semantic dimensions for the caller&#39;s workspace.
     * 
     * <p><b>200</b> - Successful response
     * @param datasetId The datasetId parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<Void> listDimensions(@javax.annotation.Nullable String datasetId) throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return listDimensionsRequestCreation(datasetId).bodyToMono(localVarReturnType);
    }

    /**
     * List all semantic dimensions for the caller&#39;s workspace.
     * 
     * <p><b>200</b> - Successful response
     * @param datasetId The datasetId parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<Void>> listDimensionsWithHttpInfo(@javax.annotation.Nullable String datasetId) throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return listDimensionsRequestCreation(datasetId).toEntity(localVarReturnType);
    }

    /**
     * List all semantic dimensions for the caller&#39;s workspace.
     * 
     * <p><b>200</b> - Successful response
     * @param datasetId The datasetId parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec listDimensionsWithResponseSpec(@javax.annotation.Nullable String datasetId) throws WebClientResponseException {
        return listDimensionsRequestCreation(datasetId);
    }

    /**
     * Validate, compile, and publish a dimension (status → PUBLISHED).
     * 
     * <p><b>200</b> - Successful response
     * @param dimensionId The dimensionId parameter
     * @return SemanticDimensionRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec publishRequestCreation(@javax.annotation.Nonnull String dimensionId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'dimensionId' is set
        if (dimensionId == null) {
            throw new WebClientResponseException("Missing the required parameter 'dimensionId' when calling publish", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("dimension_id", dimensionId);

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

        ParameterizedTypeReference<SemanticDimensionRead> localVarReturnType = new ParameterizedTypeReference<SemanticDimensionRead>() {};
        return apiClient.invokeAPI("/api/v1/semantic/dimensions/{dimension_id}:publish", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Validate, compile, and publish a dimension (status → PUBLISHED).
     * 
     * <p><b>200</b> - Successful response
     * @param dimensionId The dimensionId parameter
     * @return SemanticDimensionRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<SemanticDimensionRead> publish(@javax.annotation.Nonnull String dimensionId) throws WebClientResponseException {
        ParameterizedTypeReference<SemanticDimensionRead> localVarReturnType = new ParameterizedTypeReference<SemanticDimensionRead>() {};
        return publishRequestCreation(dimensionId).bodyToMono(localVarReturnType);
    }

    /**
     * Validate, compile, and publish a dimension (status → PUBLISHED).
     * 
     * <p><b>200</b> - Successful response
     * @param dimensionId The dimensionId parameter
     * @return ResponseEntity&lt;SemanticDimensionRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<SemanticDimensionRead>> publishWithHttpInfo(@javax.annotation.Nonnull String dimensionId) throws WebClientResponseException {
        ParameterizedTypeReference<SemanticDimensionRead> localVarReturnType = new ParameterizedTypeReference<SemanticDimensionRead>() {};
        return publishRequestCreation(dimensionId).toEntity(localVarReturnType);
    }

    /**
     * Validate, compile, and publish a dimension (status → PUBLISHED).
     * 
     * <p><b>200</b> - Successful response
     * @param dimensionId The dimensionId parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec publishWithResponseSpec(@javax.annotation.Nonnull String dimensionId) throws WebClientResponseException {
        return publishRequestCreation(dimensionId);
    }

    /**
     * Retire a dimension (status → RETIRED).
     * 
     * <p><b>200</b> - Successful response
     * @param dimensionId The dimensionId parameter
     * @return SemanticDimensionRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec retireRequestCreation(@javax.annotation.Nonnull String dimensionId) throws WebClientResponseException {
        Object postBody = null;
        // verify the required parameter 'dimensionId' is set
        if (dimensionId == null) {
            throw new WebClientResponseException("Missing the required parameter 'dimensionId' when calling retire", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
        }
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

        pathParams.put("dimension_id", dimensionId);

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

        ParameterizedTypeReference<SemanticDimensionRead> localVarReturnType = new ParameterizedTypeReference<SemanticDimensionRead>() {};
        return apiClient.invokeAPI("/api/v1/semantic/dimensions/{dimension_id}:retire", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Retire a dimension (status → RETIRED).
     * 
     * <p><b>200</b> - Successful response
     * @param dimensionId The dimensionId parameter
     * @return SemanticDimensionRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<SemanticDimensionRead> retire(@javax.annotation.Nonnull String dimensionId) throws WebClientResponseException {
        ParameterizedTypeReference<SemanticDimensionRead> localVarReturnType = new ParameterizedTypeReference<SemanticDimensionRead>() {};
        return retireRequestCreation(dimensionId).bodyToMono(localVarReturnType);
    }

    /**
     * Retire a dimension (status → RETIRED).
     * 
     * <p><b>200</b> - Successful response
     * @param dimensionId The dimensionId parameter
     * @return ResponseEntity&lt;SemanticDimensionRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<SemanticDimensionRead>> retireWithHttpInfo(@javax.annotation.Nonnull String dimensionId) throws WebClientResponseException {
        ParameterizedTypeReference<SemanticDimensionRead> localVarReturnType = new ParameterizedTypeReference<SemanticDimensionRead>() {};
        return retireRequestCreation(dimensionId).toEntity(localVarReturnType);
    }

    /**
     * Retire a dimension (status → RETIRED).
     * 
     * <p><b>200</b> - Successful response
     * @param dimensionId The dimensionId parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec retireWithResponseSpec(@javax.annotation.Nonnull String dimensionId) throws WebClientResponseException {
        return retireRequestCreation(dimensionId);
    }

    /**
     * Sparse-update a dimension; re-validates YAML if definition changes.
     * 
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param dimensionId The dimensionId parameter
     * @param semanticDimensionUpdate The semanticDimensionUpdate parameter
     * @return SemanticDimensionRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec updateRequestCreation(@javax.annotation.Nonnull String dimensionId, @javax.annotation.Nonnull SemanticDimensionUpdate semanticDimensionUpdate) throws WebClientResponseException {
        Object postBody = semanticDimensionUpdate;
        // verify the required parameter 'dimensionId' is set
        if (dimensionId == null) {
            throw new WebClientResponseException("Missing the required parameter 'dimensionId' when calling update", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
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

        final String[] localVarAccepts = { 
            "application/json"
        };
        final List<MediaType> localVarAccept = apiClient.selectHeaderAccept(localVarAccepts);
        final String[] localVarContentTypes = { 
            "application/json"
        };
        final MediaType localVarContentType = apiClient.selectHeaderContentType(localVarContentTypes);

        String[] localVarAuthNames = new String[] {  };

        ParameterizedTypeReference<SemanticDimensionRead> localVarReturnType = new ParameterizedTypeReference<SemanticDimensionRead>() {};
        return apiClient.invokeAPI("/api/v1/semantic/dimensions/{dimension_id}", HttpMethod.PUT, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Sparse-update a dimension; re-validates YAML if definition changes.
     * 
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param dimensionId The dimensionId parameter
     * @param semanticDimensionUpdate The semanticDimensionUpdate parameter
     * @return SemanticDimensionRead
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<SemanticDimensionRead> update(@javax.annotation.Nonnull String dimensionId, @javax.annotation.Nonnull SemanticDimensionUpdate semanticDimensionUpdate) throws WebClientResponseException {
        ParameterizedTypeReference<SemanticDimensionRead> localVarReturnType = new ParameterizedTypeReference<SemanticDimensionRead>() {};
        return updateRequestCreation(dimensionId, semanticDimensionUpdate).bodyToMono(localVarReturnType);
    }

    /**
     * Sparse-update a dimension; re-validates YAML if definition changes.
     * 
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param dimensionId The dimensionId parameter
     * @param semanticDimensionUpdate The semanticDimensionUpdate parameter
     * @return ResponseEntity&lt;SemanticDimensionRead&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<SemanticDimensionRead>> updateWithHttpInfo(@javax.annotation.Nonnull String dimensionId, @javax.annotation.Nonnull SemanticDimensionUpdate semanticDimensionUpdate) throws WebClientResponseException {
        ParameterizedTypeReference<SemanticDimensionRead> localVarReturnType = new ParameterizedTypeReference<SemanticDimensionRead>() {};
        return updateRequestCreation(dimensionId, semanticDimensionUpdate).toEntity(localVarReturnType);
    }

    /**
     * Sparse-update a dimension; re-validates YAML if definition changes.
     * 
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param dimensionId The dimensionId parameter
     * @param semanticDimensionUpdate The semanticDimensionUpdate parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec updateWithResponseSpec(@javax.annotation.Nonnull String dimensionId, @javax.annotation.Nonnull SemanticDimensionUpdate semanticDimensionUpdate) throws WebClientResponseException {
        return updateRequestCreation(dimensionId, semanticDimensionUpdate);
    }
}
