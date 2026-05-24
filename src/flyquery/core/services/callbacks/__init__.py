# Copyright 2026 Firefly Software Solutions Inc
"""Callback delivery service: outbox + worker.

See ``flyquery_callback_outbox`` migration 0013 for the durable
transactional outbox that decouples async-job completion from
webhook delivery latency.
"""
