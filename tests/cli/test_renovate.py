"""Tests for the renovate CLI command."""

from __future__ import annotations

from pathlib import Path

from library.cli import renovate
from tests.cli.conftest import cli, skip_if_docker_unavailable


def _write_dockerfile(path: Path) -> None:
    """Write a minimal Dockerfile for renovate scanning.

    Args:
        path: Path to the Dockerfile.
    """
    path.write_text("FROM alpine:3.19\n", encoding="utf-8")


def test_build_summary_collects_updates() -> None:
    """Build summary should aggregate update records."""
    output = "\n".join(
        [
            '{"depName": "ghcr.io/astral-sh/uv", "newVersion": "0.9.1"}',
            '{"updates": [{"depName": "ghcr.io/prefix-dev/pixi", "newVersion": "0.63.2"}]}',
            '{"branchesInformation": [{"upgrades": [{"depName": "python", "newVersion": "3.13.2"}]}]}',
        ]
    )

    summary = renovate.build_summary(output)

    updates = summary.get("updates", [])
    dep_names = {update.get("depName") for update in updates}
    assert {"ghcr.io/astral-sh/uv", "ghcr.io/prefix-dev/pixi", "python"} <= dep_names


def test_library_renovate_runs_on_dockerfile(cli_runner, tmp_path) -> None:
    """Run renovate against a local Dockerfile."""
    skip_if_docker_unavailable()
    dockerfile_path = tmp_path / "Dockerfile"
    _write_dockerfile(dockerfile_path)

    result = cli_runner.invoke(cli, ["renovate", "--dockerfile", str(dockerfile_path)])

    assert result.exit_code == 0
    assert "Renovate" in result.stdout
    assert (
        "Detected updates" in result.stdout
        or "No updates detected" in result.stdout
        or "Renovate found" in result.stdout
    )
