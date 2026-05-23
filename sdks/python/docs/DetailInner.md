# DetailInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**loc** | [**List[LocationInner]**](LocationInner.md) |  | 
**msg** | **str** |  | 
**type** | **str** |  | 

## Example

```python
from flyquery_sdk.models.detail_inner import DetailInner

# TODO update the JSON string below
json = "{}"
# create an instance of DetailInner from a JSON string
detail_inner_instance = DetailInner.from_json(json)
# print the JSON string representation of the object
print(DetailInner.to_json())

# convert the object into a dict
detail_inner_dict = detail_inner_instance.to_dict()
# create an instance of DetailInner from a dict
detail_inner_from_dict = DetailInner.from_dict(detail_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


