# RelationRead

One relation row, joined with its from/to table names for the API edge.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**approved_by** | **str** |  | [optional] 
**confidence** | [**Confidence**](Confidence.md) |  | 
**created_at** | **datetime** |  | 
**dataset_id** | **UUID** |  | 
**from_column_name** | **str** |  | 
**from_table_id** | **UUID** |  | 
**from_table_name** | **str** |  | [optional] 
**id** | **UUID** |  | 
**kind** | **str** |  | 
**reason** | **str** |  | [optional] 
**status** | **str** |  | 
**to_column_name** | **str** |  | 
**to_table_id** | **UUID** |  | 
**to_table_name** | **str** |  | [optional] 
**updated_at** | **datetime** |  | [optional] 

## Example

```python
from flyquery_sdk.models.relation_read import RelationRead

# TODO update the JSON string below
json = "{}"
# create an instance of RelationRead from a JSON string
relation_read_instance = RelationRead.from_json(json)
# print the JSON string representation of the object
print(RelationRead.to_json())

# convert the object into a dict
relation_read_dict = relation_read_instance.to_dict()
# create an instance of RelationRead from a dict
relation_read_from_dict = RelationRead.from_dict(relation_read_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


