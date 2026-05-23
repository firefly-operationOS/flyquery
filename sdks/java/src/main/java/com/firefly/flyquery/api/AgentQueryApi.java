package com.firefly.flyquery.api;

import com.firefly.flyquery.ApiClient;

import com.firefly.flyquery.model.AnswerResponse;
import com.firefly.flyquery.model.ExplainResponse;
import com.firefly.flyquery.model.HTTPValidationError;
import com.firefly.flyquery.model.QueryRequest;
import com.firefly.flyquery.model.ValidateResponse;

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
public class AgentQueryApi {
    private ApiClient apiClient;

    public AgentQueryApi() {
        this(new ApiClient());
    }

    public AgentQueryApi(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    public ApiClient getApiClient() {
        return apiClient;
    }

    public void setApiClient(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    /**
     * Run Grounding + Generation only (agent-tier).
     * :param http_request: Starlette request :param body: validated QueryRequest :return: ExplainResponse with candidate SQL and reasoning
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param queryRequest The queryRequest parameter
     * @return ExplainResponse
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec explainRequestCreation(@javax.annotation.Nonnull QueryRequest queryRequest) throws WebClientResponseException {
        Object postBody = queryRequest;
        // verify the required parameter 'queryRequest' is set
        if (queryRequest == null) {
            throw new WebClientResponseException("Missing the required parameter 'queryRequest' when calling explain", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
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

        ParameterizedTypeReference<ExplainResponse> localVarReturnType = new ParameterizedTypeReference<ExplainResponse>() {};
        return apiClient.invokeAPI("/api/v1/agent/query:explain", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Run Grounding + Generation only (agent-tier).
     * :param http_request: Starlette request :param body: validated QueryRequest :return: ExplainResponse with candidate SQL and reasoning
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param queryRequest The queryRequest parameter
     * @return ExplainResponse
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ExplainResponse> explain(@javax.annotation.Nonnull QueryRequest queryRequest) throws WebClientResponseException {
        ParameterizedTypeReference<ExplainResponse> localVarReturnType = new ParameterizedTypeReference<ExplainResponse>() {};
        return explainRequestCreation(queryRequest).bodyToMono(localVarReturnType);
    }

    /**
     * Run Grounding + Generation only (agent-tier).
     * :param http_request: Starlette request :param body: validated QueryRequest :return: ExplainResponse with candidate SQL and reasoning
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param queryRequest The queryRequest parameter
     * @return ResponseEntity&lt;ExplainResponse&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<ExplainResponse>> explainWithHttpInfo(@javax.annotation.Nonnull QueryRequest queryRequest) throws WebClientResponseException {
        ParameterizedTypeReference<ExplainResponse> localVarReturnType = new ParameterizedTypeReference<ExplainResponse>() {};
        return explainRequestCreation(queryRequest).toEntity(localVarReturnType);
    }

    /**
     * Run Grounding + Generation only (agent-tier).
     * :param http_request: Starlette request :param body: validated QueryRequest :return: ExplainResponse with candidate SQL and reasoning
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param queryRequest The queryRequest parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec explainWithResponseSpec(@javax.annotation.Nonnull QueryRequest queryRequest) throws WebClientResponseException {
        return explainRequestCreation(queryRequest);
    }

    /**
     * Run the full NL → SQL → result pipeline (agent-tier).
     * :param http_request: Starlette request (provides tenant context + agent token) :param body: validated QueryRequest :return: AnswerResponse
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param queryRequest The queryRequest parameter
     * @return AnswerResponse
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec queryRequestCreation(@javax.annotation.Nonnull QueryRequest queryRequest) throws WebClientResponseException {
        Object postBody = queryRequest;
        // verify the required parameter 'queryRequest' is set
        if (queryRequest == null) {
            throw new WebClientResponseException("Missing the required parameter 'queryRequest' when calling query", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
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

        ParameterizedTypeReference<AnswerResponse> localVarReturnType = new ParameterizedTypeReference<AnswerResponse>() {};
        return apiClient.invokeAPI("/api/v1/agent/query", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Run the full NL → SQL → result pipeline (agent-tier).
     * :param http_request: Starlette request (provides tenant context + agent token) :param body: validated QueryRequest :return: AnswerResponse
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param queryRequest The queryRequest parameter
     * @return AnswerResponse
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<AnswerResponse> query(@javax.annotation.Nonnull QueryRequest queryRequest) throws WebClientResponseException {
        ParameterizedTypeReference<AnswerResponse> localVarReturnType = new ParameterizedTypeReference<AnswerResponse>() {};
        return queryRequestCreation(queryRequest).bodyToMono(localVarReturnType);
    }

    /**
     * Run the full NL → SQL → result pipeline (agent-tier).
     * :param http_request: Starlette request (provides tenant context + agent token) :param body: validated QueryRequest :return: AnswerResponse
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param queryRequest The queryRequest parameter
     * @return ResponseEntity&lt;AnswerResponse&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<AnswerResponse>> queryWithHttpInfo(@javax.annotation.Nonnull QueryRequest queryRequest) throws WebClientResponseException {
        ParameterizedTypeReference<AnswerResponse> localVarReturnType = new ParameterizedTypeReference<AnswerResponse>() {};
        return queryRequestCreation(queryRequest).toEntity(localVarReturnType);
    }

    /**
     * Run the full NL → SQL → result pipeline (agent-tier).
     * :param http_request: Starlette request (provides tenant context + agent token) :param body: validated QueryRequest :return: AnswerResponse
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param queryRequest The queryRequest parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec queryWithResponseSpec(@javax.annotation.Nonnull QueryRequest queryRequest) throws WebClientResponseException {
        return queryRequestCreation(queryRequest);
    }

    /**
     * Run the pipeline as SSE stream (agent-tier).
     * :param http_request: Starlette request :param body: validated QueryRequest :return: StreamingResponse with text/event-stream
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param queryRequest The queryRequest parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec streamRequestCreation(@javax.annotation.Nonnull QueryRequest queryRequest) throws WebClientResponseException {
        Object postBody = queryRequest;
        // verify the required parameter 'queryRequest' is set
        if (queryRequest == null) {
            throw new WebClientResponseException("Missing the required parameter 'queryRequest' when calling stream", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
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

        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return apiClient.invokeAPI("/api/v1/agent/query/stream", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Run the pipeline as SSE stream (agent-tier).
     * :param http_request: Starlette request :param body: validated QueryRequest :return: StreamingResponse with text/event-stream
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param queryRequest The queryRequest parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<Void> stream(@javax.annotation.Nonnull QueryRequest queryRequest) throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return streamRequestCreation(queryRequest).bodyToMono(localVarReturnType);
    }

    /**
     * Run the pipeline as SSE stream (agent-tier).
     * :param http_request: Starlette request :param body: validated QueryRequest :return: StreamingResponse with text/event-stream
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param queryRequest The queryRequest parameter
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<Void>> streamWithHttpInfo(@javax.annotation.Nonnull QueryRequest queryRequest) throws WebClientResponseException {
        ParameterizedTypeReference<Void> localVarReturnType = new ParameterizedTypeReference<Void>() {};
        return streamRequestCreation(queryRequest).toEntity(localVarReturnType);
    }

    /**
     * Run the pipeline as SSE stream (agent-tier).
     * :param http_request: Starlette request :param body: validated QueryRequest :return: StreamingResponse with text/event-stream
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param queryRequest The queryRequest parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec streamWithResponseSpec(@javax.annotation.Nonnull QueryRequest queryRequest) throws WebClientResponseException {
        return streamRequestCreation(queryRequest);
    }

    /**
     * Run Grounding + Generation + AST + ScopeGuard (agent-tier).
     * :param http_request: Starlette request :param body: validated QueryRequest :return: ValidateResponse
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param queryRequest The queryRequest parameter
     * @return ValidateResponse
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec validateRequestCreation(@javax.annotation.Nonnull QueryRequest queryRequest) throws WebClientResponseException {
        Object postBody = queryRequest;
        // verify the required parameter 'queryRequest' is set
        if (queryRequest == null) {
            throw new WebClientResponseException("Missing the required parameter 'queryRequest' when calling validate", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
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

        ParameterizedTypeReference<ValidateResponse> localVarReturnType = new ParameterizedTypeReference<ValidateResponse>() {};
        return apiClient.invokeAPI("/api/v1/agent/query:validate", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Run Grounding + Generation + AST + ScopeGuard (agent-tier).
     * :param http_request: Starlette request :param body: validated QueryRequest :return: ValidateResponse
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param queryRequest The queryRequest parameter
     * @return ValidateResponse
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ValidateResponse> validate(@javax.annotation.Nonnull QueryRequest queryRequest) throws WebClientResponseException {
        ParameterizedTypeReference<ValidateResponse> localVarReturnType = new ParameterizedTypeReference<ValidateResponse>() {};
        return validateRequestCreation(queryRequest).bodyToMono(localVarReturnType);
    }

    /**
     * Run Grounding + Generation + AST + ScopeGuard (agent-tier).
     * :param http_request: Starlette request :param body: validated QueryRequest :return: ValidateResponse
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param queryRequest The queryRequest parameter
     * @return ResponseEntity&lt;ValidateResponse&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<ValidateResponse>> validateWithHttpInfo(@javax.annotation.Nonnull QueryRequest queryRequest) throws WebClientResponseException {
        ParameterizedTypeReference<ValidateResponse> localVarReturnType = new ParameterizedTypeReference<ValidateResponse>() {};
        return validateRequestCreation(queryRequest).toEntity(localVarReturnType);
    }

    /**
     * Run Grounding + Generation + AST + ScopeGuard (agent-tier).
     * :param http_request: Starlette request :param body: validated QueryRequest :return: ValidateResponse
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param queryRequest The queryRequest parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec validateWithResponseSpec(@javax.annotation.Nonnull QueryRequest queryRequest) throws WebClientResponseException {
        return validateRequestCreation(queryRequest);
    }
}
