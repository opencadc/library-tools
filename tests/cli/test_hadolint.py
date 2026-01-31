"""Tests for the lint CLI command."""

from __future__ import annotations

from tests.cli.conftest import cli, skip_if_docker_unavailable


def test_library_hadolint_accepts_dockerfile(cli_runner, fixtures_dir) -> None:
    """Lint a Dockerfile that should pass policies."""
    skip_if_docker_unavailable()
    dockerfile_path = fixtures_dir / "Dockerfile.hadolint.good"

    result = cli_runner.invoke(cli, ["lint", "--dockerfile", str(dockerfile_path)])

    assert result.exit_code == 0
    assert "Hadolint: No violations found" in result.stdout
    assert "Hadolint completed successfully" in result.stdout


def test_library_hadolint_reports_violations(cli_runner, fixtures_dir) -> None:
    """Lint a Dockerfile that should fail policies."""
    skip_if_docker_unavailable()
    dockerfile_path = fixtures_dir / "Dockerfile.hadolint.bad"

    result = cli_runner.invoke(cli, ["lint", "--dockerfile", str(dockerfile_path)])

    assert result.exit_code == 1
    assert "Hadolint violations found" in result.stdout
    assert "Hadolint failed with exit code" in result.stdout


def test_library_hadolint_accepts_verbose_flag(cli_runner, fixtures_dir) -> None:
    """Enable verbose output when linting."""
    skip_if_docker_unavailable()
    dockerfile_path = fixtures_dir / "Dockerfile.hadolint.good"

    result = cli_runner.invoke(
        cli, ["lint", "--dockerfile", str(dockerfile_path), "--verbose"]
    )

    assert result.exit_code == 0
    assert "Running hadolint" in result.stdout
