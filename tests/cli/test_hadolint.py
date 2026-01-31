"""Tests for the lint CLI command."""

from __future__ import annotations

from pathlib import Path

from tests.cli.conftest import cli, skip_if_docker_unavailable


GOOD_DOCKERFILE = """\
FROM alpine:3.19
LABEL org.opencontainers.image.title="Sample"
LABEL org.opencontainers.image.description="Sample image"
LABEL org.opencontainers.image.vendor="CANFAR"
LABEL org.opencontainers.image.source="https://example.com/source"
LABEL org.opencontainers.image.licenses="Apache-2.0"
"""

BAD_DOCKERFILE = """\
FROM alpine:latest
"""


def _write_dockerfile(path: Path, contents: str) -> None:
    """Write Dockerfile contents to disk.

    Args:
        path: Path to the Dockerfile.
        contents: Dockerfile contents to write.
    """
    path.write_text(contents, encoding="utf-8")


def test_library_hadolint_accepts_dockerfile(cli_runner, tmp_path) -> None:
    """Lint a Dockerfile that should pass policies."""
    skip_if_docker_unavailable()
    dockerfile_path = tmp_path / "Dockerfile"
    _write_dockerfile(dockerfile_path, GOOD_DOCKERFILE)

    result = cli_runner.invoke(cli, ["lint", "--dockerfile", str(dockerfile_path)])

    assert result.exit_code == 0
    assert "Hadolint: No violations found" in result.stdout
    assert "Hadolint completed successfully" in result.stdout


def test_library_hadolint_reports_violations(cli_runner, tmp_path) -> None:
    """Lint a Dockerfile that should fail policies."""
    skip_if_docker_unavailable()
    dockerfile_path = tmp_path / "Dockerfile"
    _write_dockerfile(dockerfile_path, BAD_DOCKERFILE)

    result = cli_runner.invoke(cli, ["lint", "--dockerfile", str(dockerfile_path)])

    assert result.exit_code == 1
    assert "Hadolint violations found" in result.stdout
    assert "Hadolint failed with exit code" in result.stdout


def test_library_hadolint_accepts_verbose_flag(cli_runner, tmp_path) -> None:
    """Enable verbose output when linting."""
    skip_if_docker_unavailable()
    dockerfile_path = tmp_path / "Dockerfile"
    _write_dockerfile(dockerfile_path, GOOD_DOCKERFILE)

    result = cli_runner.invoke(
        cli, ["lint", "--dockerfile", str(dockerfile_path), "--verbose"]
    )

    assert result.exit_code == 0
    assert "Running hadolint" in result.stdout
