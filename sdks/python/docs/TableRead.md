# TableRead

Response for GET /tables/{id}.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**business_owner** | **str** |  | 
**created_at** | **datetime** |  | 
**current_snapshot_id** | **UUID** |  | 
**dataset_id** | **UUID** |  | 
**description** | **str** |  | 
**description_source** | **str** |  | 
**id** | **UUID** |  | 
**is_active** | **bool** |  | 
**kind** | **str** |  | 
**n_columns** | **int** |  | [optional] 
**name** | **str** |  | 
**qualified_name** | **str** |  | 
**sheet_or_json_path** | **str** |  | 
**source_file_id** | **UUID** |  | 
**tenant_id** | **str** |  | 
**updated_at** | **datetime** |  | 
**workspace_id** | **UUID** |  | 

## Example

```python
from flyquery_sdk.models.table_read import TableRead

# TODO update the JSON string below
json = "{}"
# create an instance of TableRead from a JSON string
table_read_instance = TableRead.from_json(json)
# print the JSON string representation of the object
print(TableRead.to_json())

# convert the object into a dict
table_read_dict = table_read_instance.to_dict()
# create an instance of TableRead from a dict
table_read_from_dict = TableRead.from_dict(table_read_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


