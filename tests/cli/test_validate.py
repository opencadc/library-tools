"""Tests for the validate CLI command."""

from __future__ import annotations

from tests.cli.conftest import cli


def test_library_validate_success(cli_runner, fixtures_dir) -> None:
    """Validate a manifest via the CLI."""
    result = cli_runner.invoke(
        cli, ["validate", str(fixtures_dir / "manifest.valid.yml")]
    )
    assert result.exit_code == 0


def test_library_validate_failure(cli_runner, fixtures_dir) -> None:
    """Invalid manifests fail validation and return a non-zero exit code."""
    result = cli_runner.invoke(
        cli, ["validate", str(fixtures_dir / "manifest.invalid.yml")]
    )

    assert result.exit_code != 0
    assert result.exception is not None
