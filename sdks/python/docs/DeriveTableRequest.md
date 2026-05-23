# DeriveTableRequest

Request body for POST /api/v1/tables:derive.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**dataset_id** | **UUID** |  | 
**name** | **str** |  | 
**sql** | **str** |  | 

## Example

```python
from flyquery_sdk.models.derive_table_request import DeriveTableRequest

# TODO update the JSON string below
json = "{}"
# create an instance of DeriveTableRequest from a JSON string
derive_table_request_instance = DeriveTableRequest.from_json(json)
# print the JSON string representation of the object
print(DeriveTableRequest.to_json())

# convert the object into a dict
derive_table_request_dict = derive_table_request_instance.to_dict()
# create an instance of DeriveTableRequest from a dict
derive_table_request_from_dict = DeriveTableRequest.from_dict(derive_table_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


