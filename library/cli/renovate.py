"""Renovate CLI helpers."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from library import RENOVATE_CONFIG_PATH
from library.cli import helpers
from library.utils import docker
from library.utils.console import console


def build_summary(output: str) -> dict[str, list[dict[str, object]]]:
    """Build a JSON summary from renovate output.

    Args:
        output: Renovate output logs.

    Returns:
        Summary JSON data.
    """
    updates: list[dict[str, object]] = []
    for line in output.splitlines():
        line = line.strip()
        if not line or not line.startswith("{"):
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if "branchesInformation" in record:
            for branch in record.get("branchesInformation", []):
                updates.extend(branch.get("upgrades", []))
            continue
        if "updates" in record:
            updates.extend(record.get("updates", []))
            continue
        if "depName" in record:
            updates.append(record)
    return {"updates": updates}


def _prepare_workspace(temp_path: Path, dockerfile_contents: str) -> None:
    """Prepare renovate workspace files.

    Args:
        temp_path: Workspace directory.
        dockerfile_contents: Dockerfile contents to write.
    """
    dockerfile_path = temp_path / "Dockerfile"
    config_source = RENOVATE_CONFIG_PATH
    config_path = temp_path / "renovate.json5"
    console.print("[cyan]Preparing renovate workspace...[/cyan]")
    dockerfile_path.write_text(dockerfile_contents, encoding="utf-8")
    config_path.write_text(config_source.read_text(encoding="utf-8"), encoding="utf-8")


def _run_renovate_container(temp_path: Path, verbose: bool) -> str:
    """Run renovate in a container.

    Args:
        temp_path: Workspace directory.
        verbose: Whether to emit verbose output.

    Returns:
        Renovate output logs.
    """
    command = [
        "--platform=local",
        "--require-config=ignored",
        "--dry-run=full",
    ]
    docker.pull("docker.io/renovate/renovate:latest")
    console.print("[cyan]Running renovate...[/cyan]")
    result = docker.run(
        "renovate/renovate:latest",
        command,
        volumes={str(temp_path): {"bind": "/repo", "mode": "rw"}},
        working_dir="/repo",
        environment={"LOG_FORMAT": "json", "LOG_LEVEL": "debug"},
        stdin_open=True,
        verbose=verbose,
    )
    return (result.stdout or "").strip()


def _report_summary(summary: dict[str, list[dict[str, object]]]) -> None:
    """Report renovate summary output.

    Args:
        summary: Renovate summary data.
    """
    updates = summary.get("updates", [])
    if updates:
        console.print(
            f"[yellow]Renovate found {len(updates)} update candidates.[/yellow]"
        )
    else:
        console.print("[green]Renovate: No updates found.[/green]")


def run_renovate(
    manifest_path: Path | None,
    dockerfile_path: Path | None,
    verbose: bool,
) -> dict[str, list[dict[str, object]]]:
    """Run renovate against a manifest or Dockerfile.

    Args:
        manifest_path: Path to the manifest file.
        dockerfile_path: Path to a local Dockerfile.
        verbose: Whether to emit verbose output.

    Returns:
        Summary JSON data.

    Raises:
        ValueError: If neither a manifest nor Dockerfile path is provided.
    """
    dockerfile_contents = helpers.resolve_dockerfile_contents(
        manifest_path, dockerfile_path
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        _prepare_workspace(temp_path, dockerfile_contents)
        output = _run_renovate_container(temp_path, verbose)

    console.print("[cyan]Generating JSON summary...[/cyan]")
    summary = build_summary(output)
    _report_summary(summary)
    return summary
