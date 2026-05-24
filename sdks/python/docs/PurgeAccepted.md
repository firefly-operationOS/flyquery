# PurgeAccepted

202 Accepted envelope for purge-style endpoints.  ``status`` is always ``\"accepted\"`` (mirrors the workspaces purge contract). ``tombstone_expires_at`` is a human-readable hint -- consumers receive an ISO-8601 timestamp when the retention job actually deletes the SQL row; today the value is the ``+90d`` placeholder (90 days mirrors ``conv_ttl_days``).

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **str** | Always &#39;accepted&#39; for 202 responses. | [optional] [default to 'accepted']
**tombstone_expires_at** | **str** | When the SQL row is expected to be hard-deleted. ISO-8601 once a retention job is wired; today returns a coarse hint such as &#39;+90d&#39;. | 

## Example

```python
from flyquery_sdk.models.purge_accepted import PurgeAccepted

# TODO update the JSON string below
json = "{}"
# create an instance of PurgeAccepted from a JSON string
purge_accepted_instance = PurgeAccepted.from_json(json)
# print the JSON string representation of the object
print(PurgeAccepted.to_json())

# convert the object into a dict
purge_accepted_dict = purge_accepted_instance.to_dict()
# create an instance of PurgeAccepted from a dict
purge_accepted_from_dict = PurgeAccepted.from_dict(purge_accepted_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


