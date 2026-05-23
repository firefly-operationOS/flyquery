package com.firefly.flyquery.api;

import com.firefly.flyquery.ApiClient;

import com.firefly.flyquery.model.AnswerResponse;
import com.firefly.flyquery.model.BatchQueryRequest;
import com.firefly.flyquery.model.BatchQueryResponse;
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

@javax.annotation.Generated(value = "org.openapitools.codegen.languages.JavaClientCodegen", date = "2026-05-24T00:36:39.059958+02:00[Europe/Madrid]", comments = "Generator version: 7.22.0")
public class QueryApi {
    private ApiClient apiClient;

    public QueryApi() {
        this(new ApiClient());
    }

    public QueryApi(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    public ApiClient getApiClient() {
        return apiClient;
    }

    public void setApiClient(ApiClient apiClient) {
        this.apiClient = apiClient;
    }

    /**
     * Run multiple NL questions in parallel through the full pipeline.
     * Each item runs the same pipeline as &#x60;&#x60;POST /api/v1/query&#x60;&#x60;, fanned out via &#x60;&#x60;asyncio.gather&#x60;&#x60; with a Semaphore-style concurrency cap (mirrors the bulk-file endpoint). Per-question failures do NOT abort the batch -- failed items carry &#x60;&#x60;status&#x3D;\&quot;FAILED\&quot;&#x60;&#x60; + &#x60;&#x60;error&#x60;&#x60; and the response aggregates &#x60;&#x60;succeeded&#x60;&#x60; / &#x60;&#x60;failed&#x60;&#x60; counts.  Use this for dashboard refreshes (one batch with N panel queries), comparison reports (same question against M datasets), or SDK callers that want to amortise auth + tenant context across many questions.
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param batchQueryRequest The batchQueryRequest parameter
     * @return BatchQueryResponse
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    private ResponseSpec batchRequestCreation(@javax.annotation.Nonnull BatchQueryRequest batchQueryRequest) throws WebClientResponseException {
        Object postBody = batchQueryRequest;
        // verify the required parameter 'batchQueryRequest' is set
        if (batchQueryRequest == null) {
            throw new WebClientResponseException("Missing the required parameter 'batchQueryRequest' when calling batch", HttpStatus.BAD_REQUEST.value(), HttpStatus.BAD_REQUEST.getReasonPhrase(), null, null, null);
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

        ParameterizedTypeReference<BatchQueryResponse> localVarReturnType = new ParameterizedTypeReference<BatchQueryResponse>() {};
        return apiClient.invokeAPI("/api/v1/query:batch", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Run multiple NL questions in parallel through the full pipeline.
     * Each item runs the same pipeline as &#x60;&#x60;POST /api/v1/query&#x60;&#x60;, fanned out via &#x60;&#x60;asyncio.gather&#x60;&#x60; with a Semaphore-style concurrency cap (mirrors the bulk-file endpoint). Per-question failures do NOT abort the batch -- failed items carry &#x60;&#x60;status&#x3D;\&quot;FAILED\&quot;&#x60;&#x60; + &#x60;&#x60;error&#x60;&#x60; and the response aggregates &#x60;&#x60;succeeded&#x60;&#x60; / &#x60;&#x60;failed&#x60;&#x60; counts.  Use this for dashboard refreshes (one batch with N panel queries), comparison reports (same question against M datasets), or SDK callers that want to amortise auth + tenant context across many questions.
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param batchQueryRequest The batchQueryRequest parameter
     * @return BatchQueryResponse
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<BatchQueryResponse> batch(@javax.annotation.Nonnull BatchQueryRequest batchQueryRequest) throws WebClientResponseException {
        ParameterizedTypeReference<BatchQueryResponse> localVarReturnType = new ParameterizedTypeReference<BatchQueryResponse>() {};
        return batchRequestCreation(batchQueryRequest).bodyToMono(localVarReturnType);
    }

    /**
     * Run multiple NL questions in parallel through the full pipeline.
     * Each item runs the same pipeline as &#x60;&#x60;POST /api/v1/query&#x60;&#x60;, fanned out via &#x60;&#x60;asyncio.gather&#x60;&#x60; with a Semaphore-style concurrency cap (mirrors the bulk-file endpoint). Per-question failures do NOT abort the batch -- failed items carry &#x60;&#x60;status&#x3D;\&quot;FAILED\&quot;&#x60;&#x60; + &#x60;&#x60;error&#x60;&#x60; and the response aggregates &#x60;&#x60;succeeded&#x60;&#x60; / &#x60;&#x60;failed&#x60;&#x60; counts.  Use this for dashboard refreshes (one batch with N panel queries), comparison reports (same question against M datasets), or SDK callers that want to amortise auth + tenant context across many questions.
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param batchQueryRequest The batchQueryRequest parameter
     * @return ResponseEntity&lt;BatchQueryResponse&gt;
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public Mono<ResponseEntity<BatchQueryResponse>> batchWithHttpInfo(@javax.annotation.Nonnull BatchQueryRequest batchQueryRequest) throws WebClientResponseException {
        ParameterizedTypeReference<BatchQueryResponse> localVarReturnType = new ParameterizedTypeReference<BatchQueryResponse>() {};
        return batchRequestCreation(batchQueryRequest).toEntity(localVarReturnType);
    }

    /**
     * Run multiple NL questions in parallel through the full pipeline.
     * Each item runs the same pipeline as &#x60;&#x60;POST /api/v1/query&#x60;&#x60;, fanned out via &#x60;&#x60;asyncio.gather&#x60;&#x60; with a Semaphore-style concurrency cap (mirrors the bulk-file endpoint). Per-question failures do NOT abort the batch -- failed items carry &#x60;&#x60;status&#x3D;\&quot;FAILED\&quot;&#x60;&#x60; + &#x60;&#x60;error&#x60;&#x60; and the response aggregates &#x60;&#x60;succeeded&#x60;&#x60; / &#x60;&#x60;failed&#x60;&#x60; counts.  Use this for dashboard refreshes (one batch with N panel queries), comparison reports (same question against M datasets), or SDK callers that want to amortise auth + tenant context across many questions.
     * <p><b>200</b> - Successful response
     * <p><b>422</b> - Validation Error
     * @param batchQueryRequest The batchQueryRequest parameter
     * @return ResponseSpec
     * @throws WebClientResponseException if an error occurs while attempting to invoke the API
     */
    public ResponseSpec batchWithResponseSpec(@javax.annotation.Nonnull BatchQueryRequest batchQueryRequest) throws WebClientResponseException {
        return batchRequestCreation(batchQueryRequest);
    }

    /**
     * Run Grounding + Generation but stop before AST/execution.
     * Useful for previewing the generated SQL without paying execution costs.  :param http_request: Starlette request :param body: validated QueryRequest :return: ExplainResponse with candidate SQL and reasoning
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
        return apiClient.invokeAPI("/api/v1/query:explain", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Run Grounding + Generation but stop before AST/execution.
     * Useful for previewing the generated SQL without paying execution costs.  :param http_request: Starlette request :param body: validated QueryRequest :return: ExplainResponse with candidate SQL and reasoning
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
     * Run Grounding + Generation but stop before AST/execution.
     * Useful for previewing the generated SQL without paying execution costs.  :param http_request: Starlette request :param body: validated QueryRequest :return: ExplainResponse with candidate SQL and reasoning
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
     * Run Grounding + Generation but stop before AST/execution.
     * Useful for previewing the generated SQL without paying execution costs.  :param http_request: Starlette request :param body: validated QueryRequest :return: ExplainResponse with candidate SQL and reasoning
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
     * Run the full NL → SQL → result pipeline and return a synchronous answer.
     * :param http_request: Starlette request (provides tenant context headers) :param body: validated QueryRequest :return: AnswerResponse with SQL, preview rows, chart hint, and explanation
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
        return apiClient.invokeAPI("/api/v1/query", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Run the full NL → SQL → result pipeline and return a synchronous answer.
     * :param http_request: Starlette request (provides tenant context headers) :param body: validated QueryRequest :return: AnswerResponse with SQL, preview rows, chart hint, and explanation
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
     * Run the full NL → SQL → result pipeline and return a synchronous answer.
     * :param http_request: Starlette request (provides tenant context headers) :param body: validated QueryRequest :return: AnswerResponse with SQL, preview rows, chart hint, and explanation
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
     * Run the full NL → SQL → result pipeline and return a synchronous answer.
     * :param http_request: Starlette request (provides tenant context headers) :param body: validated QueryRequest :return: AnswerResponse with SQL, preview rows, chart hint, and explanation
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
     * Run the full pipeline as a Server-Sent Events stream.
     * Event sequence: 1. &#x60;&#x60;schema_linked&#x60;&#x60;   — after grounding completes 2. &#x60;&#x60;clarification&#x60;&#x60;   — (optional) when confidence &lt; threshold + missing_info 3. &#x60;&#x60;sql_generated&#x60;&#x60;   — after generation 4. &#x60;&#x60;executed&#x60;&#x60;        — after DuckDB execution 5. &#x60;&#x60;explained&#x60;&#x60;       — after ExplainerAgent 6. &#x60;&#x60;final&#x60;&#x60;           — full AnswerResponse JSON  :param http_request: Starlette request :param body: validated QueryRequest (body already consumed by pyfly) :return: StreamingResponse with &#x60;&#x60;text/event-stream&#x60;&#x60; content type
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
        return apiClient.invokeAPI("/api/v1/query/stream", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Run the full pipeline as a Server-Sent Events stream.
     * Event sequence: 1. &#x60;&#x60;schema_linked&#x60;&#x60;   — after grounding completes 2. &#x60;&#x60;clarification&#x60;&#x60;   — (optional) when confidence &lt; threshold + missing_info 3. &#x60;&#x60;sql_generated&#x60;&#x60;   — after generation 4. &#x60;&#x60;executed&#x60;&#x60;        — after DuckDB execution 5. &#x60;&#x60;explained&#x60;&#x60;       — after ExplainerAgent 6. &#x60;&#x60;final&#x60;&#x60;           — full AnswerResponse JSON  :param http_request: Starlette request :param body: validated QueryRequest (body already consumed by pyfly) :return: StreamingResponse with &#x60;&#x60;text/event-stream&#x60;&#x60; content type
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
     * Run the full pipeline as a Server-Sent Events stream.
     * Event sequence: 1. &#x60;&#x60;schema_linked&#x60;&#x60;   — after grounding completes 2. &#x60;&#x60;clarification&#x60;&#x60;   — (optional) when confidence &lt; threshold + missing_info 3. &#x60;&#x60;sql_generated&#x60;&#x60;   — after generation 4. &#x60;&#x60;executed&#x60;&#x60;        — after DuckDB execution 5. &#x60;&#x60;explained&#x60;&#x60;       — after ExplainerAgent 6. &#x60;&#x60;final&#x60;&#x60;           — full AnswerResponse JSON  :param http_request: Starlette request :param body: validated QueryRequest (body already consumed by pyfly) :return: StreamingResponse with &#x60;&#x60;text/event-stream&#x60;&#x60; content type
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
     * Run the full pipeline as a Server-Sent Events stream.
     * Event sequence: 1. &#x60;&#x60;schema_linked&#x60;&#x60;   — after grounding completes 2. &#x60;&#x60;clarification&#x60;&#x60;   — (optional) when confidence &lt; threshold + missing_info 3. &#x60;&#x60;sql_generated&#x60;&#x60;   — after generation 4. &#x60;&#x60;executed&#x60;&#x60;        — after DuckDB execution 5. &#x60;&#x60;explained&#x60;&#x60;       — after ExplainerAgent 6. &#x60;&#x60;final&#x60;&#x60;           — full AnswerResponse JSON  :param http_request: Starlette request :param body: validated QueryRequest (body already consumed by pyfly) :return: StreamingResponse with &#x60;&#x60;text/event-stream&#x60;&#x60; content type
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
     * Run Grounding + Generation + AST classification + ScopeGuard check.
     * Returns the classification and any scope error without executing the SQL.  :param http_request: Starlette request :param body: validated QueryRequest :return: ValidateResponse with AST classification and optional scope_error
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
        return apiClient.invokeAPI("/api/v1/query:validate", HttpMethod.POST, pathParams, queryParams, postBody, headerParams, cookieParams, formParams, localVarAccept, localVarContentType, localVarAuthNames, localVarReturnType);
    }

    /**
     * Run Grounding + Generation + AST classification + ScopeGuard check.
     * Returns the classification and any scope error without executing the SQL.  :param http_request: Starlette request :param body: validated QueryRequest :return: ValidateResponse with AST classification and optional scope_error
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
     * Run Grounding + Generation + AST classification + ScopeGuard check.
     * Returns the classification and any scope error without executing the SQL.  :param http_request: Starlette request :param body: validated QueryRequest :return: ValidateResponse with AST classification and optional scope_error
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
     * Run Grounding + Generation + AST classification + ScopeGuard check.
     * Returns the classification and any scope error without executing the SQL.  :param http_request: Starlette request :param body: validated QueryRequest :return: ValidateResponse with AST classification and optional scope_error
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
