/* Copyright 2026 Firefly Software Solutions Inc */
package com.firefly.flyquery;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.util.UUID;
import org.junit.jupiter.api.Test;

/**
 * Smoke tests for {@link FlyqueryClient}.
 *
 * <p>Only verifies construction + the four-header defaults wiring; the per-method API behaviour is
 * already covered by the generated {@code *ApiTest} classes.
 */
class FlyqueryClientTest {

  @Test
  void builderRequiresTenantAndWorkspace() {
    assertThrows(NullPointerException.class, () -> FlyqueryClient.builder().build());
    assertThrows(
        NullPointerException.class,
        () -> FlyqueryClient.builder().baseUrl("http://localhost:8520").build());
    assertThrows(
        NullPointerException.class,
        () ->
            FlyqueryClient.builder()
                .baseUrl("http://localhost:8520")
                .tenantId("acme")
                .build());
  }

  @Test
  void builderSetsFourHeaderContract() {
    FlyqueryClient client =
        FlyqueryClient.builder()
            .baseUrl("http://localhost:8520")
            .tenantId("acme")
            .workspaceId("finance")
            .agentToken("fly_pat_abc")
            .build();

    ApiClient api = client.apiClient();
    assertEquals("http://localhost:8520", api.getBasePath());
    assertEquals("acme", client.tenantId());
    assertEquals("finance", client.workspaceId());
    assertEquals("fly_pat_abc", client.agentToken());
  }

  @Test
  void userTierClientHasNoAgentToken() {
    FlyqueryClient client =
        FlyqueryClient.builder()
            .baseUrl("http://localhost:8520")
            .tenantId("acme")
            .workspaceId("finance")
            .build();

    assertNull(client.agentToken());
  }

  @Test
  void withIdempotencyKeyDerivesSiblingClient() {
    FlyqueryClient parent =
        FlyqueryClient.builder()
            .baseUrl("http://localhost:8520")
            .tenantId("acme")
            .workspaceId("finance")
            .build();
    FlyqueryClient derived = parent.withIdempotencyKey("retry-42");

    // Sibling preserves identity context.
    assertEquals(parent.tenantId(), derived.tenantId());
    assertEquals(parent.workspaceId(), derived.workspaceId());
    // But carries its own ApiClient so the parent isn't mutated.
    assertNotNull(derived.apiClient());
  }

  @Test
  void withAgentTokenDerivesSiblingClient() {
    FlyqueryClient userTier =
        FlyqueryClient.builder()
            .baseUrl("http://localhost:8520")
            .tenantId("acme")
            .workspaceId("finance")
            .build();
    FlyqueryClient agentTier = userTier.withAgentToken("fly_pat_xyz");

    assertNull(userTier.agentToken());
    assertEquals("fly_pat_xyz", agentTier.agentToken());
  }

  @Test
  void withCorrelationIdAccepted() {
    FlyqueryClient client =
        FlyqueryClient.builder()
            .baseUrl("http://localhost:8520")
            .tenantId("acme")
            .workspaceId("finance")
            .build();
    UUID corr = UUID.randomUUID();
    FlyqueryClient derived = client.withCorrelationId(corr);
    assertNotNull(derived);
    assertEquals(client.tenantId(), derived.tenantId());
  }

  @Test
  void apiAccessorsAreNonNull() {
    FlyqueryClient client =
        FlyqueryClient.builder()
            .baseUrl("http://localhost:8520")
            .tenantId("acme")
            .workspaceId("finance")
            .agentToken("fly_pat_abc")
            .build();
    // Just verify the surface compiles + returns instances. Per-method
    // behaviour is covered by the generated *ApiTest classes.
    assertNotNull(client.workspaces());
    assertNotNull(client.datasets());
    assertNotNull(client.files());
    assertNotNull(client.tables());
    assertNotNull(client.query());
    assertNotNull(client.conversations());
    assertNotNull(client.agentQuery());
    assertNotNull(client.agentSqlExecute());
    assertNotNull(client.agentExamples());
    assertNotNull(client.agentTokens());
    assertNotNull(client.ingestJobs());
    assertNotNull(client.semanticMetrics());
    assertNotNull(client.semanticDimensions());
    assertNotNull(client.glossary());
    assertNotNull(client.examples());
    assertNotNull(client.relations());
    assertNotNull(client.schemaObjects());
    assertNotNull(client.schemaChanges());
    assertNotNull(client.tablesDerive());
    assertNotNull(client.sqlExecute());
    assertNotNull(client.version());
    assertNotNull(client.agentVersion());
    // v1.0 (26.5.10) accessors.
    assertNotNull(client.queries());
    assertNotNull(client.billing());
    assertNotNull(client.stats());
    assertNotNull(client.auditEvents());
    assertNotNull(client.costEvents());
  }
}
