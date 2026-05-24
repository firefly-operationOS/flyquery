

# BillingRollup

Response from GET /api/v1/billing.  ``period`` is the bucket granularity that was applied; ``date_from`` and ``date_to`` echo the request bounds so consumers can render \"showing X to Y\" headers without keeping local state.

## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
|**breakdown** | [**List&lt;BillingBreakdownItem&gt;**](BillingBreakdownItem.md) |  |  |
|**dateFrom** | **OffsetDateTime** |  |  [optional] |
|**dateTo** | **OffsetDateTime** |  |  [optional] |
|**period** | **String** |  |  |
|**totalCostCents** | [**TotalCostCents**](TotalCostCents.md) |  |  |



