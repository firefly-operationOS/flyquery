# Copyright 2026 Firefly Software Solutions Inc
"""flyquery CLI entry point."""

from __future__ import annotations

import sys

import click


@click.group()
@click.version_option()
def main() -> None:
    """flyquery command-line interface."""


@main.command()
@click.option("--host", default="0.0.0.0", show_default=True)
@click.option("--port", default=8520, show_default=True, type=int)
def serve(host: str, port: int) -> None:
    """Run the API server."""
    import uvicorn

    uvicorn.run("flyquery.main:app", host=host, port=port)


@main.command()
def version() -> None:
    """Print the package version."""
    from flyquery import __version__

    click.echo(__version__)


if __name__ == "__main__":
    sys.exit(main())
