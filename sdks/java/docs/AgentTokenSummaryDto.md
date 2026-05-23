

# AgentTokenSummaryDto

Token surface as listed back to user-tier callers -- secret omitted.  Every read path through ``GET /api/v1/agent-tokens`` returns this shape. The raw token is *only* available on the :class:`AgentTokenCreated` returned by the mint endpoint and is never round-tripped through any other endpoint.

## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
|**createdAt** | **OffsetDateTime** |  |  |
|**createdBy** | **String** |  |  |
|**expiresAt** | **OffsetDateTime** |  |  |
|**id** | **String** |  |  |
|**lastUsedAt** | **OffsetDateTime** |  |  |
|**name** | **String** |  |  |
|**prefix** | **String** |  |  |
|**rateLimitRpm** | **Integer** |  |  |
|**revokedAt** | **OffsetDateTime** |  |  |
|**scopes** | **List&lt;String&gt;** |  |  |
|**workspaceAllowlist** | **List&lt;String&gt;** |  |  |



