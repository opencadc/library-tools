"""Tests for the renovate CLI command."""

from __future__ import annotations

import json
import re

from library.cli import renovate
from tests.cli.conftest import cli, skip_if_docker_unavailable


def _extract_json_payload(output: str) -> dict[str, object]:
    """Extract a JSON payload from CLI output.

    Args:
        output: CLI output to parse.

    Returns:
        Parsed JSON payload.
    """
    ansi_escape = re.compile(r"\x1b\[[0-9;]*m")
    lines = [ansi_escape.sub("", line) for line in output.splitlines()]
    start_index = None
    for index in range(len(lines) - 1, -1, -1):
        if lines[index].startswith("{"):
            start_index = index
            break
    if start_index is None:
        for index in range(len(lines) - 1, -1, -1):
            if lines[index].startswith("["):
                start_index = index
                break
    if start_index is None:
        raise AssertionError("No JSON payload found in output")
    payload = "\n".join(lines[start_index:])
    return json.loads(payload)


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


def test_library_renovate_runs_on_dockerfile(cli_runner, fixtures_dir) -> None:
    """Run renovate against a local Dockerfile."""
    skip_if_docker_unavailable()
    dockerfile_path = fixtures_dir / "Dockerfile.hadolint.good"

    result = cli_runner.invoke(cli, ["renovate", "--dockerfile", str(dockerfile_path)])

    assert result.exit_code == 0
    assert "Renovate" in result.stdout
    assert (
        "Detected updates" in result.stdout
        or "No updates detected" in result.stdout
        or "Renovate found" in result.stdout
    )


def test_library_renovate_emits_json_output(cli_runner, fixtures_dir) -> None:
    """Emit JSON updates when requested."""
    skip_if_docker_unavailable()
    dockerfile_path = fixtures_dir / "Dockerfile.hadolint.good"

    result = cli_runner.invoke(
        cli, ["renovate", "--dockerfile", str(dockerfile_path), "--json"]
    )

    assert result.exit_code == 0
    payload = _extract_json_payload(result.stdout)
    assert "updates" in payload
