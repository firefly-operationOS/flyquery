# SqlExecuteRequest

Request body for POST /api/v1/sql:execute.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**dataset_id** | **UUID** |  | 
**sql** | **str** |  | 

## Example

```python
from flyquery_sdk.models.sql_execute_request import SqlExecuteRequest

# TODO update the JSON string below
json = "{}"
# create an instance of SqlExecuteRequest from a JSON string
sql_execute_request_instance = SqlExecuteRequest.from_json(json)
# print the JSON string representation of the object
print(SqlExecuteRequest.to_json())

# convert the object into a dict
sql_execute_request_dict = sql_execute_request_instance.to_dict()
# create an instance of SqlExecuteRequest from a dict
sql_execute_request_from_dict = SqlExecuteRequest.from_dict(sql_execute_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


