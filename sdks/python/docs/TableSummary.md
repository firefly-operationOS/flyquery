# TableSummary

Summary of a table created/updated by an upload.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**n_columns** | **int** |  | 
**n_rows_estimate** | **int** |  | 
**name** | **str** |  | 
**table_id** | **str** |  | 

## Example

```python
from flyquery_sdk.models.table_summary import TableSummary

# TODO update the JSON string below
json = "{}"
# create an instance of TableSummary from a JSON string
table_summary_instance = TableSummary.from_json(json)
# print the JSON string representation of the object
print(TableSummary.to_json())

# convert the object into a dict
table_summary_dict = table_summary_instance.to_dict()
# create an instance of TableSummary from a dict
table_summary_from_dict = TableSummary.from_dict(table_summary_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


