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
public class AgentExamplesApi {
    private ApiClient apiClient;

    public AgentExamplesApi() {
        this(new ApiClient());
    }

    public AgentExamplesApi(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    public ApiClient getApiClient() {
        return apiClient;
    }

    public void setApiClient(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    /**
     * Create an example (agent-tier — source&#x3D;AGENT_LEARNED, quality&#x3D;PROPOSED).
     * :param http_request: Starlette request :param body: validated ExampleCreate :return: ExampleRead with created fields
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
        return apiClient.invokeAPI("/api/v1/agent/examples", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Create an example (agent-tier — source&#x3D;AGENT_LEARNED, quality&#x3D;PROPOSED).
     * :param http_request: Starlette request :param body: validated ExampleCreate :return: ExampleRead with created fields
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
     * Create an example (agent-tier — source&#x3D;AGENT_LEARNED, quality&#x3D;PROPOSED).
     * :param http_request: Starlette request :param body: validated ExampleCreate :return: ExampleRead with created fields
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
     * Create an example (agent-tier — source&#x3D;AGENT_LEARNED, quality&#x3D;PROPOSED).
     * :param http_request: Starlette request :param body: validated ExampleCreate :return: ExampleRead with created fields
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
     * List examples for the caller&#39;s workspace (agent-tier).
     * :param http_request: Starlette request :param quality: optional quality filter (PROPOSED/APPROVED/REJECTED) :param dataset_id: optional dataset filter :return: &#x60;&#x60;{\&quot;items\&quot;: [...]}&#x60;&#x60;
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
        return apiClient.invokeAPI("/api/v1/agent/examples", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * List examples for the caller&#39;s workspace (agent-tier).
     * :param http_request: Starlette request :param quality: optional quality filter (PROPOSED/APPROVED/REJECTED) :param dataset_id: optional dataset filter :return: &#x60;&#x60;{\&quot;items\&quot;: [...]}&#x60;&#x60;
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
     * List examples for the caller&#39;s workspace (agent-tier).
     * :param http_request: Starlette request :param quality: optional quality filter (PROPOSED/APPROVED/REJECTED) :param dataset_id: optional dataset filter :return: &#x60;&#x60;{\&quot;items\&quot;: [...]}&#x60;&#x60;
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
     * List examples for the caller&#39;s workspace (agent-tier).
     * :param http_request: Starlette request :param quality: optional quality filter (PROPOSED/APPROVED/REJECTED) :param dataset_id: optional dataset filter :return: &#x60;&#x60;{\&quot;items\&quot;: [...]}&#x60;&#x60;
     * <p><b>200</b> - Successful response
     * @param quality The quality parameter
     * @param datasetId The datasetId parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec listExamplesWithResponseSpec(@javax.annotation.Nullable String quality, @javax.annotation.Nullable String datasetId) throws WebClientResponseException {
        return listExamplesRequestCreation(quality, datasetId);
    }
}
