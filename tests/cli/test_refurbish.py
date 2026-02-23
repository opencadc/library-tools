"""Tests for the refurbish CLI command."""

from __future__ import annotations

import json
import re
from pathlib import Path

from yaml import safe_dump

from library.tools import defaults as runtime_defaults
from tests.cli.conftest import cli, skip_if_docker_unavailable


def _extract_json_payload(output: str) -> dict[str, object]:
    """Extract a JSON payload from CLI output."""
    ansi_escape = re.compile(r"\x1b\[[0-9;]*m")
    lines = [ansi_escape.sub("", line) for line in output.splitlines()]
    start_index = None
    for index in range(len(lines) - 1, -1, -1):
        if lines[index].startswith("{"):
            start_index = index
            break
    if start_index is None:
        raise AssertionError("No JSON payload found in output")
    payload = "\n".join(lines[start_index:])
    return json.loads(payload)


def _write_manifest(path: Path, dockerfile_path: Path) -> None:
    path.write_text(
        safe_dump(
            {
                "version": 1,
                "registry": {
                    "host": "images.canfar.net",
                    "project": "library",
                    "image": "sample-image",
                },
                "build": {
                    "context": str(dockerfile_path.parent.resolve()),
                    "file": dockerfile_path.name,
                    "tags": ["latest"],
                },
                "metadata": {
                    "discovery": {
                        "title": "Sample Image",
                        "description": "Sample description for testing.",
                        "source": "https://github.com/opencadc/canfar-library",
                        "url": "https://images.canfar.net/library/sample-image",
                        "documentation": "https://canfar.net/docs/user-guide",
                        "version": "1.0.0",
                        "revision": "1234567890123456789012345678901234567890",
                        "created": "2026-02-05T12:00:00Z",
                        "authors": [
                            {
                                "name": "Example Maintainer",
                                "email": "maintainer@example.com",
                            }
                        ],
                        "licenses": "MIT",
                        "keywords": ["sample", "testing"],
                        "domain": ["astronomy"],
                        "kind": ["headless"],
                        "tools": ["python"],
                    }
                },
                "config": runtime_defaults.default_config().model_dump(mode="python"),
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )


def test_library_refurbish_runs_with_manifest(
    cli_runner, fixtures_dir, tmp_path
) -> None:
    """Run refurbish against a manifest-resolved Dockerfile."""
    skip_if_docker_unavailable()
    dockerfile_path = (fixtures_dir / "Dockerfile.hadolint.good").resolve()
    manifest_path = tmp_path / ".library.manifest.yaml"
    _write_manifest(manifest_path, dockerfile_path)

    result = cli_runner.invoke(cli, ["refurbish", "--manifest", str(manifest_path)])

    assert result.exit_code == 0
    assert "Detected updates" in result.stdout or "No updates detected" in result.stdout


def test_library_refurbish_emits_json_output(
    cli_runner, fixtures_dir, tmp_path
) -> None:
    """Refurbish should emit JSON output when requested."""
    skip_if_docker_unavailable()
    dockerfile_path = (fixtures_dir / "Dockerfile.hadolint.good").resolve()
    manifest_path = tmp_path / ".library.manifest.yaml"
    _write_manifest(manifest_path, dockerfile_path)

    result = cli_runner.invoke(
        cli,
        ["refurbish", "--manifest", str(manifest_path), "--json"],
    )

    assert result.exit_code == 0
    payload = _extract_json_payload(result.stdout)
    assert "updates" in payload


def test_library_renovate_command_is_removed(cli_runner) -> None:
    """Legacy renovate command should not exist."""
    result = cli_runner.invoke(cli, ["renovate"])

    assert result.exit_code != 0
    assert result.exception is not None
