"""Tests for the validate CLI command."""

from __future__ import annotations

from tests.cli.conftest import cli


def test_library_validate_success(cli_runner, fixtures_dir) -> None:
    """Validate a manifest via the CLI."""
    result = cli_runner.invoke(
        cli, ["validate", str(fixtures_dir / "manifest.valid.yml")]
    )
    assert result.exit_code == 0
