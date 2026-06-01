# SemanticDimensionRead

Full read representation of a flyquery_semantic_dimensions row.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**compiled_sql_template** | **str** |  | 
**created_at** | **datetime** |  | 
**current_version** | **int** |  | 
**dataset_id** | **UUID** |  | 
**definition_yaml** | **str** |  | 
**description** | **str** |  | 
**dimension_type** | **str** |  | 
**id** | **UUID** |  | 
**label** | **str** |  | 
**metadata_json** | **Dict[str, object]** |  | [optional] 
**name** | **str** |  | 
**status** | **str** |  | 
**tenant_id** | **str** |  | 
**updated_at** | **datetime** |  | 
**workspace_id** | **UUID** |  | 

## Example

```python
from flyquery_sdk.models.semantic_dimension_read import SemanticDimensionRead

# TODO update the JSON string below
json = "{}"
# create an instance of SemanticDimensionRead from a JSON string
semantic_dimension_read_instance = SemanticDimensionRead.from_json(json)
# print the JSON string representation of the object
print(SemanticDimensionRead.to_json())

# convert the object into a dict
semantic_dimension_read_dict = semantic_dimension_read_instance.to_dict()
# create an instance of SemanticDimensionRead from a dict
semantic_dimension_read_from_dict = SemanticDimensionRead.from_dict(semantic_dimension_read_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


