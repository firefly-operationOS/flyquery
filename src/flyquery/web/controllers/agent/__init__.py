# Copyright 2026 Firefly Software Solutions Inc
"""Agent-tier REST controllers — /api/v1/agent/* routes.

These controllers mirror the user-tier controllers but require a valid
``X-Agent-Token`` with the appropriate scope instead of a JWT bearer token.
They delegate to the same services as their user-tier counterparts.
"""
