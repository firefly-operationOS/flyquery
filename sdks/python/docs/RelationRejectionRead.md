# RelationRejectionRead

Compact response from POST /relations/{id}:reject.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **UUID** |  | 
**status** | **str** |  | 
**updated_at** | **datetime** |  | 

## Example

```python
from flyquery_sdk.models.relation_rejection_read import RelationRejectionRead

# TODO update the JSON string below
json = "{}"
# create an instance of RelationRejectionRead from a JSON string
relation_rejection_read_instance = RelationRejectionRead.from_json(json)
# print the JSON string representation of the object
print(RelationRejectionRead.to_json())

# convert the object into a dict
relation_rejection_read_dict = relation_rejection_read_instance.to_dict()
# create an instance of RelationRejectionRead from a dict
relation_rejection_read_from_dict = RelationRejectionRead.from_dict(relation_rejection_read_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


