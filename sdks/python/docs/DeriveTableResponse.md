# DeriveTableResponse

Response from POST /api/v1/tables:derive.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**dataset_id** | **UUID** |  | 
**name** | **str** |  | 
**table_id** | **UUID** |  | 

## Example

```python
from flyquery_sdk.models.derive_table_response import DeriveTableResponse

# TODO update the JSON string below
json = "{}"
# create an instance of DeriveTableResponse from a JSON string
derive_table_response_instance = DeriveTableResponse.from_json(json)
# print the JSON string representation of the object
print(DeriveTableResponse.to_json())

# convert the object into a dict
derive_table_response_dict = derive_table_response_instance.to_dict()
# create an instance of DeriveTableResponse from a dict
derive_table_response_from_dict = DeriveTableResponse.from_dict(derive_table_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


