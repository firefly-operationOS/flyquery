

# PurgeAccepted

202 Accepted envelope for purge-style endpoints.  ``status`` is always ``\"accepted\"`` (mirrors the workspaces purge contract). ``tombstone_expires_at`` is a human-readable hint -- consumers receive an ISO-8601 timestamp when the retention job actually deletes the SQL row; today the value is the ``+90d`` placeholder (90 days mirrors ``conv_ttl_days``).

## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
|**status** | **String** | Always &#39;accepted&#39; for 202 responses. |  [optional] |
|**tombstoneExpiresAt** | **String** | When the SQL row is expected to be hard-deleted. ISO-8601 once a retention job is wired; today returns a coarse hint such as &#39;+90d&#39;. |  |



