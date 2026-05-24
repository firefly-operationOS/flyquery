# PaginatedDatasetRead


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**has_more** | **bool** |  | [optional] 
**items** | [**List[DatasetRead]**](DatasetRead.md) |  | [optional] 
**limit** | **int** |  | [optional] 
**offset** | **int** |  | [optional] 
**total** | **int** |  | [optional] 

## Example

```python
from flyquery_sdk.models.paginated_dataset_read import PaginatedDatasetRead

# TODO update the JSON string below
json = "{}"
# create an instance of PaginatedDatasetRead from a JSON string
paginated_dataset_read_instance = PaginatedDatasetRead.from_json(json)
# print the JSON string representation of the object
print(PaginatedDatasetRead.to_json())

# convert the object into a dict
paginated_dataset_read_dict = paginated_dataset_read_instance.to_dict()
# create an instance of PaginatedDatasetRead from a dict
paginated_dataset_read_from_dict = PaginatedDatasetRead.from_dict(paginated_dataset_read_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


