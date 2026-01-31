"""CLI test fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from library.utils import docker

from library.cli.main import cli

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture()
def fixtures_dir() -> Path:
    """Provide the CLI fixtures directory."""
    return FIXTURES


@pytest.fixture()
def cli_runner() -> CliRunner:
    """Provide a Typer CLI runner instance."""
    return CliRunner()


def skip_if_docker_unavailable() -> None:
    """Skip tests when the Docker daemon is unavailable."""
    try:
        docker.get_client().ping()
    except Exception as exc:
        pytest.skip(f"Docker unavailable: {exc}")


__all__ = [
    "cli",
    "cli_runner",
    "fixtures_dir",
    "skip_if_docker_unavailable",
    "FIXTURES",
]
