# TurnRead

Single conversation turn.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**conversation_id** | **UUID** |  | 
**created_at** | **datetime** |  | 
**elapsed_ms** | **int** |  | 
**executed_sql** | **str** |  | 
**id** | **UUID** |  | 
**no_answer** | **bool** |  | 
**question** | **str** |  | 
**snapshot_pins_json** | **Dict[str, object]** |  | [optional] 
**summary** | **str** |  | 
**table_qnames_json** | **List[str]** |  | [optional] 
**tenant_id** | **str** |  | 
**turn_index** | **int** |  | 
**workspace_id** | **UUID** |  | 

## Example

```python
from flyquery_sdk.models.turn_read import TurnRead

# TODO update the JSON string below
json = "{}"
# create an instance of TurnRead from a JSON string
turn_read_instance = TurnRead.from_json(json)
# print the JSON string representation of the object
print(TurnRead.to_json())

# convert the object into a dict
turn_read_dict = turn_read_instance.to_dict()
# create an instance of TurnRead from a dict
turn_read_from_dict = TurnRead.from_dict(turn_read_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


