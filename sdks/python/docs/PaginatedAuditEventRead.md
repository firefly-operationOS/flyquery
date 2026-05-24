# PaginatedAuditEventRead


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**has_more** | **bool** |  | [optional] 
**items** | [**List[AuditEventRead]**](AuditEventRead.md) |  | [optional] 
**limit** | **int** |  | [optional] 
**offset** | **int** |  | [optional] 
**total** | **int** |  | [optional] 

## Example

```python
from flyquery_sdk.models.paginated_audit_event_read import PaginatedAuditEventRead

# TODO update the JSON string below
json = "{}"
# create an instance of PaginatedAuditEventRead from a JSON string
paginated_audit_event_read_instance = PaginatedAuditEventRead.from_json(json)
# print the JSON string representation of the object
print(PaginatedAuditEventRead.to_json())

# convert the object into a dict
paginated_audit_event_read_dict = paginated_audit_event_read_instance.to_dict()
# create an instance of PaginatedAuditEventRead from a dict
paginated_audit_event_read_from_dict = PaginatedAuditEventRead.from_dict(paginated_audit_event_read_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


