# CallbackDeliveryListResponse

Paginated callback-delivery audit log.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**items** | [**List[CallbackDeliveryRead]**](CallbackDeliveryRead.md) |  | 
**limit** | **int** |  | 
**offset** | **int** |  | 
**total** | **int** |  | 

## Example

```python
from flyquery_sdk.models.callback_delivery_list_response import CallbackDeliveryListResponse

# TODO update the JSON string below
json = "{}"
# create an instance of CallbackDeliveryListResponse from a JSON string
callback_delivery_list_response_instance = CallbackDeliveryListResponse.from_json(json)
# print the JSON string representation of the object
print(CallbackDeliveryListResponse.to_json())

# convert the object into a dict
callback_delivery_list_response_dict = callback_delivery_list_response_instance.to_dict()
# create an instance of CallbackDeliveryListResponse from a dict
callback_delivery_list_response_from_dict = CallbackDeliveryListResponse.from_dict(callback_delivery_list_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


