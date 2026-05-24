# CostEventRead

Append-only LLM cost ledger row.  ``cost_cents`` is a Decimal because partial cents are common at the per-call granularity (the cost tracker in fireflyframework-agentic rounds at aggregation time, not per row).

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**actor** | **str** |  | 
**correlation_id** | **str** |  | [optional] 
**cost_cents** | [**CostCents**](CostCents.md) |  | 
**created_at** | **datetime** |  | 
**id** | **UUID** |  | 
**ingest_job_id** | **UUID** |  | [optional] 
**input_tokens** | **int** |  | 
**model** | **str** |  | [optional] 
**operation** | **str** |  | 
**output_tokens** | **int** |  | 
**query_id** | **UUID** |  | [optional] 
**tenant_id** | **str** |  | 
**workspace_id** | **UUID** |  | 

## Example

```python
from flyquery_sdk.models.cost_event_read import CostEventRead

# TODO update the JSON string below
json = "{}"
# create an instance of CostEventRead from a JSON string
cost_event_read_instance = CostEventRead.from_json(json)
# print the JSON string representation of the object
print(CostEventRead.to_json())

# convert the object into a dict
cost_event_read_dict = cost_event_read_instance.to_dict()
# create an instance of CostEventRead from a dict
cost_event_read_from_dict = CostEventRead.from_dict(cost_event_read_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


