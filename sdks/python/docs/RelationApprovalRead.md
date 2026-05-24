# RelationApprovalRead

Compact response from POST /relations/{id}:approve.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**approved_by** | **str** |  | 
**id** | **UUID** |  | 
**status** | **str** |  | 
**updated_at** | **datetime** |  | 

## Example

```python
from flyquery_sdk.models.relation_approval_read import RelationApprovalRead

# TODO update the JSON string below
json = "{}"
# create an instance of RelationApprovalRead from a JSON string
relation_approval_read_instance = RelationApprovalRead.from_json(json)
# print the JSON string representation of the object
print(RelationApprovalRead.to_json())

# convert the object into a dict
relation_approval_read_dict = relation_approval_read_instance.to_dict()
# create an instance of RelationApprovalRead from a dict
relation_approval_read_from_dict = RelationApprovalRead.from_dict(relation_approval_read_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


