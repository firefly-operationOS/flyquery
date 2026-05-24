/* Copyright 2026 Firefly Software Solutions Inc */
package com.firefly.flyquery;

import com.firefly.flyquery.api.AgentExamplesApi;
import com.firefly.flyquery.api.AgentQueryApi;
import com.firefly.flyquery.api.AgentSqlExecuteApi;
import com.firefly.flyquery.api.AgentTokensApi;
import com.firefly.flyquery.api.AgentVersionApi;
import com.firefly.flyquery.api.AuditEventsApi;
import com.firefly.flyquery.api.BillingApi;
import com.firefly.flyquery.api.ConversationsApi;
import com.firefly.flyquery.api.CostEventsApi;
import com.firefly.flyquery.api.DatasetsApi;
import com.firefly.flyquery.api.ExamplesApi;
import com.firefly.flyquery.api.FilesApi;
import com.firefly.flyquery.api.GlossaryApi;
import com.firefly.flyquery.api.IngestJobsApi;
import com.firefly.flyquery.api.QueriesApi;
import com.firefly.flyquery.api.QueryApi;
import com.firefly.flyquery.api.RelationsApi;
import com.firefly.flyquery.api.SchemaChangesApi;
import com.firefly.flyquery.api.SchemaObjectsApi;
import com.firefly.flyquery.api.SemanticDimensionsApi;
import com.firefly.flyquery.api.SemanticMetricsApi;
import com.firefly.flyquery.api.SqlExecuteApi;
import com.firefly.flyquery.api.StatsApi;
import com.firefly.flyquery.api.TablesApi;
import com.firefly.flyquery.api.TablesDeriveApi;
import com.firefly.flyquery.api.VersionApi;
import com.firefly.flyquery.api.WorkspacesApi;
import java.util.Objects;
import java.util.UUID;

/**
 * Tenant- and workspace-scoped flyquery client.
 *
 * <p>Mirror of {@code flyquery_sdk.client.FlyqueryClient} in the Python SDK. Constructs a single
 * {@link ApiClient} pre-configured with the four flyquery wire headers (X-Tenant-Id,
 * X-Workspace-Id, optionally X-Agent-Token, and a per-call Idempotency-Key) so call sites do not
 * have to repeat them on every API method.
 *
 * <p>The OpenAPI spec models these headers as parameters on every operation (so the generated
 * {@code *Api} methods accept them too), but in practice every call from a given client instance
 * shares the same tenant and workspace. Setting them as {@link ApiClient#addDefaultHeader defaults}
 * once eliminates the per-call boilerplate.
 *
 * <h2>Usage</h2>
 *
 * <pre>{@code
 * FlyqueryClient client = FlyqueryClient.builder()
 *     .baseUrl("https://flyquery.example.com")
 *     .tenantId("acme")
 *     .workspaceId("finance")
 *     .build();
 *
 * client.datasets().list().subscribe(page -> ...);
 *
 * // Per-call idempotency:
 * client.withIdempotencyKey("retry-42").agentQuery().query(req).subscribe(...);
 *
 * // Drop down to the raw ApiClient when you need a knob the wrapper doesn't expose:
 * client.apiClient().addDefaultHeader("X-Custom", "foo");
 * }</pre>
 *
 * <h2>Thread safety</h2>
 *
 * <p>The wrapper itself is immutable after construction; the underlying {@link ApiClient}'s
 * {@link reactor.core.publisher.Mono} returns make it safe to share one instance across threads.
 * Use {@link #withAgentToken(String)} or {@link #withIdempotencyKey(String)} to derive a
 * short-lived sibling client when you need to override a header for a single call.
 */
public final class FlyqueryClient {

  /** HTTP header carrying the tenant slug. Required on every non-agent endpoint. */
  public static final String HEADER_TENANT_ID = "X-Tenant-Id";

  /** HTTP header carrying the workspace UUID or slug. Required on every non-agent endpoint. */
  public static final String HEADER_WORKSPACE_ID = "X-Workspace-Id";

  /** HTTP header carrying the agent bearer token. Required on every {@code /api/v1/agent/*} endpoint. */
  public static final String HEADER_AGENT_TOKEN = "X-Agent-Token";

  /** HTTP header for replay-dedup on mutating endpoints (1-128 chars of [A-Za-z0-9_-]). */
  public static final String HEADER_IDEMPOTENCY_KEY = "Idempotency-Key";

  /** Optional client-supplied correlation id, echoed in logs and downstream calls. */
  public static final String HEADER_CORRELATION_ID = "X-Correlation-Id";

  private final ApiClient apiClient;
  private final String tenantId;
  private final String workspaceId;
  private final String agentToken;

  private FlyqueryClient(ApiClient apiClient, String tenantId, String workspaceId, String agentToken) {
    this.apiClient = apiClient;
    this.tenantId = tenantId;
    this.workspaceId = workspaceId;
    this.agentToken = agentToken;
  }

  /** Returns a fresh builder for the four-header contract. */
  public static Builder builder() {
    return new Builder();
  }

  /** The underlying generated client. Mutate carefully -- shared across every accessor. */
  public ApiClient apiClient() {
    return apiClient;
  }

  /** Tenant slug bound at construction. */
  public String tenantId() {
    return tenantId;
  }

  /** Workspace UUID or slug bound at construction. */
  public String workspaceId() {
    return workspaceId;
  }

  /** Currently-bound agent token, or {@code null} for user-tier clients. */
  public String agentToken() {
    return agentToken;
  }

  /**
   * Returns a sibling client that adds an {@code Idempotency-Key} header to every request. The
   * resulting client shares the underlying {@link ApiClient} pool -- do not close the wrapper
   * returned here independently of the parent.
   *
   * <p>Convention from {@code flyquery_sdk}: use a fresh UUID per logical write, retried as-is on
   * network errors. The server caches the response for 24h so a retry returns the original
   * payload.
   */
  public FlyqueryClient withIdempotencyKey(String key) {
    Objects.requireNonNull(key, "Idempotency-Key must not be null");
    ApiClient derived = cloneApiClient();
    derived.addDefaultHeader(HEADER_IDEMPOTENCY_KEY, key);
    return new FlyqueryClient(derived, tenantId, workspaceId, agentToken);
  }

  /**
   * Returns a sibling client that swaps in (or sets) an agent bearer token. Use this when an
   * application juggles both user-tier and agent-tier credentials.
   */
  public FlyqueryClient withAgentToken(String token) {
    Objects.requireNonNull(token, "agent token must not be null");
    ApiClient derived = cloneApiClient();
    derived.addDefaultHeader(HEADER_AGENT_TOKEN, token);
    return new FlyqueryClient(derived, tenantId, workspaceId, token);
  }

  /**
   * Returns a sibling client that adds an {@code X-Correlation-Id} header. Pass the same value
   * across a logical workflow so the service emits a single correlation thread across logs and
   * downstream calls.
   */
  public FlyqueryClient withCorrelationId(UUID correlationId) {
    Objects.requireNonNull(correlationId, "correlation id must not be null");
    ApiClient derived = cloneApiClient();
    derived.addDefaultHeader(HEADER_CORRELATION_ID, correlationId.toString());
    return new FlyqueryClient(derived, tenantId, workspaceId, agentToken);
  }

  // ----------------------------------------------------------------------
  // API accessors -- one instance per resource family.
  // ----------------------------------------------------------------------

  public WorkspacesApi workspaces() {
    return new WorkspacesApi(apiClient);
  }

  public DatasetsApi datasets() {
    return new DatasetsApi(apiClient);
  }

  public FilesApi files() {
    return new FilesApi(apiClient);
  }

  public TablesApi tables() {
    return new TablesApi(apiClient);
  }

  public TablesDeriveApi tablesDerive() {
    return new TablesDeriveApi(apiClient);
  }

  public SchemaObjectsApi schemaObjects() {
    return new SchemaObjectsApi(apiClient);
  }

  public SchemaChangesApi schemaChanges() {
    return new SchemaChangesApi(apiClient);
  }

  public RelationsApi relations() {
    return new RelationsApi(apiClient);
  }

  public ExamplesApi examples() {
    return new ExamplesApi(apiClient);
  }

  public GlossaryApi glossary() {
    return new GlossaryApi(apiClient);
  }

  public SemanticMetricsApi semanticMetrics() {
    return new SemanticMetricsApi(apiClient);
  }

  public SemanticDimensionsApi semanticDimensions() {
    return new SemanticDimensionsApi(apiClient);
  }

  public ConversationsApi conversations() {
    return new ConversationsApi(apiClient);
  }

  public QueryApi query() {
    return new QueryApi(apiClient);
  }

  public SqlExecuteApi sqlExecute() {
    return new SqlExecuteApi(apiClient);
  }

  public IngestJobsApi ingestJobs() {
    return new IngestJobsApi(apiClient);
  }

  public AgentTokensApi agentTokens() {
    return new AgentTokensApi(apiClient);
  }

  public AgentQueryApi agentQuery() {
    return new AgentQueryApi(apiClient);
  }

  public AgentSqlExecuteApi agentSqlExecute() {
    return new AgentSqlExecuteApi(apiClient);
  }

  public AgentExamplesApi agentExamples() {
    return new AgentExamplesApi(apiClient);
  }

  public AgentVersionApi agentVersion() {
    return new AgentVersionApi(apiClient);
  }

  public VersionApi version() {
    return new VersionApi(apiClient);
  }

  // ----------------------------------------------------------------------
  // v1.0 (26.5.10) -- history + billing + stats + ops ledger accessors
  // ----------------------------------------------------------------------

  /** History reader -- {@code GET /api/v1/queries{,/{id},/{id}/result}}. */
  public QueriesApi queries() {
    return new QueriesApi(apiClient);
  }

  /** Cost rollup -- {@code GET /api/v1/billing} (day/week/month buckets). */
  public BillingApi billing() {
    return new BillingApi(apiClient);
  }

  /** Workspace summary -- {@code GET /api/v1/stats} (storage + 5 counts). */
  public StatsApi stats() {
    return new StatsApi(apiClient);
  }

  /** Audit-event ledger reader -- {@code GET /api/v1/audit-events}. */
  public AuditEventsApi auditEvents() {
    return new AuditEventsApi(apiClient);
  }

  /** Per-call LLM cost-event ledger reader -- {@code GET /api/v1/cost-events}. */
  public CostEventsApi costEvents() {
    return new CostEventsApi(apiClient);
  }

  // ----------------------------------------------------------------------
  // Internals
  // ----------------------------------------------------------------------

  private ApiClient cloneApiClient() {
    // ApiClient has no copy constructor or .clone(); re-instantiate against
    // the same WebClient pool and re-apply our defaults. The generated
    // ApiClient stores only a few fields beyond the WebClient.
    ApiClient copy = new ApiClient(apiClient.getWebClient());
    copy.setBasePath(apiClient.getBasePath());
    copy.addDefaultHeader(HEADER_TENANT_ID, tenantId);
    copy.addDefaultHeader(HEADER_WORKSPACE_ID, workspaceId);
    if (agentToken != null) {
      copy.addDefaultHeader(HEADER_AGENT_TOKEN, agentToken);
    }
    return copy;
  }

  /** Builder for {@link FlyqueryClient}. {@code baseUrl}, {@code tenantId}, and {@code workspaceId} are required. */
  public static final class Builder {
    private String baseUrl;
    private String tenantId;
    private String workspaceId;
    private String agentToken;
    private ApiClient apiClient;

    private Builder() {}

    /** REST endpoint base URL, e.g. {@code https://flyquery.example.com}. Required. */
    public Builder baseUrl(String baseUrl) {
      this.baseUrl = baseUrl;
      return this;
    }

    /** Tenant slug bound to {@link #HEADER_TENANT_ID} on every request. Required. */
    public Builder tenantId(String tenantId) {
      this.tenantId = tenantId;
      return this;
    }

    /** Workspace identifier (UUID or slug) bound to {@link #HEADER_WORKSPACE_ID}. Required. */
    public Builder workspaceId(String workspaceId) {
      this.workspaceId = workspaceId;
      return this;
    }

    /** Optional agent bearer token for {@code /api/v1/agent/*} endpoints. */
    public Builder agentToken(String agentToken) {
      this.agentToken = agentToken;
      return this;
    }

    /**
     * Use a caller-supplied {@link ApiClient} (e.g. one wired with a custom {@code WebClient} for
     * proxying, TLS, retries). The wrapper still appends the four-header defaults.
     */
    public Builder apiClient(ApiClient apiClient) {
      this.apiClient = apiClient;
      return this;
    }

    public FlyqueryClient build() {
      Objects.requireNonNull(tenantId, "tenantId is required");
      Objects.requireNonNull(workspaceId, "workspaceId is required");
      ApiClient client = apiClient != null ? apiClient : new ApiClient();
      if (baseUrl != null) {
        client.setBasePath(baseUrl);
      } else {
        Objects.requireNonNull(client.getBasePath(), "baseUrl is required (or pre-set on apiClient)");
      }
      client.addDefaultHeader(HEADER_TENANT_ID, tenantId);
      client.addDefaultHeader(HEADER_WORKSPACE_ID, workspaceId);
      if (agentToken != null) {
        client.addDefaultHeader(HEADER_AGENT_TOKEN, agentToken);
      }
      return new FlyqueryClient(client, tenantId, workspaceId, agentToken);
    }
  }
}
