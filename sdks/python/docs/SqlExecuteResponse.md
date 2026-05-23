# SqlExecuteResponse

Response from POST /api/v1/sql:execute (sync).

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**ast_classification** | **str** |  | 
**elapsed_ms** | **int** |  | 
**execution_status** | **str** |  | 
**preview** | **List[Dict[str, object]]** |  | 
**query_id** | **UUID** |  | 
**row_count** | **int** |  | 
**sql** | **str** |  | 
**truncated** | **bool** |  | [optional] [default to False]

## Example

```python
from flyquery_sdk.models.sql_execute_response import SqlExecuteResponse

# TODO update the JSON string below
json = "{}"
# create an instance of SqlExecuteResponse from a JSON string
sql_execute_response_instance = SqlExecuteResponse.from_json(json)
# print the JSON string representation of the object
print(SqlExecuteResponse.to_json())

# convert the object into a dict
sql_execute_response_dict = sql_execute_response_instance.to_dict()
# create an instance of SqlExecuteResponse from a dict
sql_execute_response_from_dict = SqlExecuteResponse.from_dict(sql_execute_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


