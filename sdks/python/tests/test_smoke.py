"""Verify the generated SDK can be imported and exposes the expected split API classes.

Each controller tag (workspaces, datasets, files, ...) must produce a
dedicated API class (WorkspacesApi, DatasetsApi, FilesApi, ...) rather
than collapsing everything into DefaultApi.
"""
import sys
import os

# Ensure the SDK package directory is on the path when running from repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def test_imports():
    from flyquery_sdk import ApiClient, Configuration  # noqa: F401
    assert ApiClient
    assert Configuration


def test_split_api_classes():
    """All major resource groups must have a dedicated API class."""
    from flyquery_sdk.api import (  # noqa: F401
        WorkspacesApi,
        DatasetsApi,
        FilesApi,
        TablesApi,
        SchemaApi,
        RelationsApi,
        SemanticApi,
        GlossaryApi,
        ExamplesApi,
        QueryApi,
        ConversationsApi,
        IngestApi,
        SqlApi,
        AgentTokensApi,
        MetaApi,
        AgentExamplesApi,
        AgentQueryApi,
        AgentSqlApi,
    )
    assert WorkspacesApi.__module__.endswith(".workspaces_api")
    assert DatasetsApi.__module__.endswith(".datasets_api")
    assert QueryApi.__module__.endswith(".query_api")
    assert FilesApi.__module__.endswith(".files_api")
    assert AgentQueryApi.__module__.endswith(".agent_query_api")


def test_configuration_can_be_constructed():
    from flyquery_sdk import Configuration
    cfg = Configuration(host="http://localhost:8520")
    assert cfg.host == "http://localhost:8520"


def test_api_client_can_be_constructed():
    from flyquery_sdk import ApiClient, Configuration
    cfg = Configuration(host="http://localhost:8520")
    client = ApiClient(configuration=cfg)
    assert client is not None
    # Don't close the async client in sync context — just verify construction
