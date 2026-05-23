

# AgentTokenCreated

Mint response: includes the full ``token`` ONCE.  Subsequent reads only ever expose ``prefix`` -- the secret hash is stored server-side and never returned. Callers MUST capture the token at mint time; there is no recovery path.

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
|**token** | **String** |  |  |
|**workspaceAllowlist** | **List&lt;String&gt;** |  |  |



