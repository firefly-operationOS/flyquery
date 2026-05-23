# UsageSummary

Aggregated cost + latency across the whole pipeline.  Returned on every query / ingest response so clients can show consumption to end users and stream into a billing pipeline. The per-stage breakdown stays in ``by_agent`` for debugging.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**by_agent** | [**List[AgentUsage]**](AgentUsage.md) |  | [optional] 
**total_cost_usd** | **float** |  | [optional] [default to 0.0]
**total_input_tokens** | **int** |  | [optional] [default to 0]
**total_latency_ms** | **float** |  | [optional] [default to 0.0]
**total_output_tokens** | **int** |  | [optional] [default to 0]
**total_tokens** | **int** |  | [optional] [default to 0]

## Example

```python
from flyquery_sdk.models.usage_summary import UsageSummary

# TODO update the JSON string below
json = "{}"
# create an instance of UsageSummary from a JSON string
usage_summary_instance = UsageSummary.from_json(json)
# print the JSON string representation of the object
print(UsageSummary.to_json())

# convert the object into a dict
usage_summary_dict = usage_summary_instance.to_dict()
# create an instance of UsageSummary from a dict
usage_summary_from_dict = UsageSummary.from_dict(usage_summary_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


