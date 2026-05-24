

# AgentTokenMintRequest

Request body for ``POST /api/v1/agent-tokens``.  ``workspace_allowlist`` is optional -- ``None`` means the token can be used in any workspace under the tenant. ``scopes`` defaults to ``[\"*\"]`` (all scopes); the verify path treats ``\"*\"`` as a wildcard. ``rate_limit_rpm`` is advisory metadata today and reserved for the per-token rate limiter we add later; ``expires_at`` is enforced by the verify path.  Every requested scope must be in :data:`flyquery.core.services.auth.scope_catalog.ALL_SCOPES` -- Pydantic validates this before the mint hits the database and surfaces an ``invalid_scope`` error envelope on the wire.

## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
|**expiresAt** | **OffsetDateTime** |  |  [optional] |
|**name** | **String** |  |  |
|**rateLimitRpm** | **Integer** |  |  [optional] |
|**scopes** | **List&lt;String&gt;** |  |  [optional] |
|**workspaceAllowlist** | **List&lt;String&gt;** |  |  [optional] |



