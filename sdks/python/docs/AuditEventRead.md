# AuditEventRead

Append-only audit ledger row.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**actor** | **str** |  | 
**correlation_id** | **str** |  | [optional] 
**created_at** | **datetime** |  | 
**event_type** | **str** |  | 
**id** | **UUID** |  | 
**payload_json** | **Dict[str, object]** |  | [optional] 
**resource_id** | **str** |  | [optional] 
**resource_kind** | **str** |  | 
**tenant_id** | **str** |  | 
**workspace_id** | **UUID** |  | 

## Example

```python
from flyquery_sdk.models.audit_event_read import AuditEventRead

# TODO update the JSON string below
json = "{}"
# create an instance of AuditEventRead from a JSON string
audit_event_read_instance = AuditEventRead.from_json(json)
# print the JSON string representation of the object
print(AuditEventRead.to_json())

# convert the object into a dict
audit_event_read_dict = audit_event_read_instance.to_dict()
# create an instance of AuditEventRead from a dict
audit_event_read_from_dict = AuditEventRead.from_dict(audit_event_read_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


