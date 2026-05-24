

# CallbackConfig

Webhook delivery target attached to an async ingest job.  Set on job creation (``IngestJobCreate.callback`` or the ``callback_*`` query params on ``POST /datasets/{id}/files:async``). On every terminal status transition the worker writes one row to ``flyquery_callback_outbox``; the ``CallbackWorker`` POSTs the canonical :class:`IngestJobRead` to ``url`` with header ``X-Flyquery-Signature: sha256=<hmac>`` if ``secret`` is provided.  Delivery is at-least-once with exponential backoff (5 attempts: 0s, 30s, 5m, 1h, 6h). After the last failed attempt the row is marked ``DEAD`` and surfaced via ``GET /ingest-jobs/{id}/callbacks``.

## Properties

| Name | Type | Description | Notes |
|------------ | ------------- | ------------- | -------------|
|**headers** | **Map&lt;String, String&gt;** | Extra HTTP headers merged onto every callback request. |  [optional] |
|**secret** | **String** | Shared secret for HMAC-SHA256 over the request body. |  [optional] |
|**url** | **URI** |  |  |



