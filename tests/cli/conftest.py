"""CLI test fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

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


__all__ = ["cli", "cli_runner", "fixtures_dir", "FIXTURES"]
