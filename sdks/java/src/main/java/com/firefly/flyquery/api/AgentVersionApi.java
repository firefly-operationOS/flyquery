package com.firefly.flyquery.api;

import com.firefly.flyquery.ApiClient;


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
public class AgentVersionApi {
    private ApiClient apiClient;

    public AgentVersionApi() {
        this(new ApiClient());
    }

    public AgentVersionApi(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    public ApiClient getApiClient() {
        return apiClient;
    }

    public void setApiClient(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    /**
     * Return service name + CalVer version tag.
     * Requires a valid &#x60;&#x60;X-Agent-Token&#x60;&#x60; with &#x60;&#x60;flyquery.audit:read&#x60;&#x60; scope. Missing or invalid tokens return 401 / 403 respectively.
     * <p><b>200</b> - Successful response
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec versionRequestCreation() throws WebClientResponseException {
        Object postBody = null;
        // create path and map variables
        final Map<String, Object> pathParams = new HashMap<String, Object>();

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
        return apiClient.invokeAPI("/api/v1/agent/version", HttpMethod.GET, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Return service name + CalVer version tag.
     * Requires a valid &#x60;&#x60;X-Agent-Token&#x60;&#x60; with &#x60;&#x60;flyquery.audit:read&#x60;&#x60; scope. Missing or invalid tokens return 401 / 403 respectively.
     * <p><b>200</b> - Successful response
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<Void> version() throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return versionRequestCreation().bodyToMono(localVarReturnType);
    }

    /**
     * Return service name + CalVer version tag.
     * Requires a valid &#x60;&#x60;X-Agent-Token&#x60;&#x60; with &#x60;&#x60;flyquery.audit:read&#x60;&#x60; scope. Missing or invalid tokens return 401 / 403 respectively.
     * <p><b>200</b> - Successful response
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<Void>> versionWithHttpInfo() throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return versionRequestCreation().toEntity(localVarReturnType);
    }

    /**
     * Return service name + CalVer version tag.
     * Requires a valid &#x60;&#x60;X-Agent-Token&#x60;&#x60; with &#x60;&#x60;flyquery.audit:read&#x60;&#x60; scope. Missing or invalid tokens return 401 / 403 respectively.
     * <p><b>200</b> - Successful response
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec versionWithResponseSpec() throws WebClientResponseException {
        return versionRequestCreation();
    }
}
