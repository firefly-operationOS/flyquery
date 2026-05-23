# AgentUsage

LLM usage + cost for a single pipeline stage.  Surfaced inside :class:`UsageSummary` so callers see exactly where the tokens went. ``cost_usd`` is computed by the fireflyframework-agentic cost tracker (per-model rate table).

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**agent** | **str** |  | 
**calls** | **int** |  | [optional] [default to 0]
**cost_usd** | **float** |  | [optional] [default to 0.0]
**input_tokens** | **int** |  | [optional] [default to 0]
**latency_ms** | **float** |  | [optional] [default to 0.0]
**model** | **str** |  | [optional] 
**output_tokens** | **int** |  | [optional] [default to 0]
**total_tokens** | **int** |  | [optional] [default to 0]

## Example

```python
from flyquery_sdk.models.agent_usage import AgentUsage

# TODO update the JSON string below
json = "{}"
# create an instance of AgentUsage from a JSON string
agent_usage_instance = AgentUsage.from_json(json)
# print the JSON string representation of the object
print(AgentUsage.to_json())

# convert the object into a dict
agent_usage_dict = agent_usage_instance.to_dict()
# create an instance of AgentUsage from a dict
agent_usage_from_dict = AgentUsage.from_dict(agent_usage_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


