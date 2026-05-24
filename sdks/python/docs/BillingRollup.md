# BillingRollup

Response from GET /api/v1/billing.  ``period`` is the bucket granularity that was applied; ``date_from`` and ``date_to`` echo the request bounds so consumers can render \"showing X to Y\" headers without keeping local state.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**breakdown** | [**List[BillingBreakdownItem]**](BillingBreakdownItem.md) |  | 
**date_from** | **datetime** |  | [optional] 
**date_to** | **datetime** |  | [optional] 
**period** | **str** |  | 
**total_cost_cents** | [**TotalCostCents**](TotalCostCents.md) |  | 

## Example

```python
from flyquery_sdk.models.billing_rollup import BillingRollup

# TODO update the JSON string below
json = "{}"
# create an instance of BillingRollup from a JSON string
billing_rollup_instance = BillingRollup.from_json(json)
# print the JSON string representation of the object
print(BillingRollup.to_json())

# convert the object into a dict
billing_rollup_dict = billing_rollup_instance.to_dict()
# create an instance of BillingRollup from a dict
billing_rollup_from_dict = BillingRollup.from_dict(billing_rollup_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


