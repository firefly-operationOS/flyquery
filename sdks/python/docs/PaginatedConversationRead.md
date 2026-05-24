# PaginatedConversationRead


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**has_more** | **bool** |  | [optional] 
**items** | [**List[ConversationRead]**](ConversationRead.md) |  | [optional] 
**limit** | **int** |  | [optional] 
**offset** | **int** |  | [optional] 
**total** | **int** |  | [optional] 

## Example

```python
from flyquery_sdk.models.paginated_conversation_read import PaginatedConversationRead

# TODO update the JSON string below
json = "{}"
# create an instance of PaginatedConversationRead from a JSON string
paginated_conversation_read_instance = PaginatedConversationRead.from_json(json)
# print the JSON string representation of the object
print(PaginatedConversationRead.to_json())

# convert the object into a dict
paginated_conversation_read_dict = paginated_conversation_read_instance.to_dict()
# create an instance of PaginatedConversationRead from a dict
paginated_conversation_read_from_dict = PaginatedConversationRead.from_dict(paginated_conversation_read_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


