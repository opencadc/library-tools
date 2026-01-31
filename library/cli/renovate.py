"""Renovate CLI helpers."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from library import manifest, RENOVATE_CONFIG_PATH
from library.utils import docker, fetch
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
    dockerfile_contents: str

    if dockerfile_path is not None:
        console.print(f"[cyan]Reading Dockerfile: {dockerfile_path}[/cyan]")
        dockerfile_contents = dockerfile_path.read_text(encoding="utf-8")
    elif manifest_path is not None:
        console.print(f"[cyan]Reading Manifest: {manifest_path}[/cyan]")
        data = manifest.read(manifest_path)
        manifest.validate(data)
        git_info = data["git"]
        build_info = data["build"]
        repo = git_info["repo"]
        commit = git_info["commit"]
        path = build_info.get("path")
        dockerfile = build_info.get("dockerfile")
        raw_url = fetch.url(repo, commit, path, dockerfile)
        dockerfile_contents = fetch.contents(raw_url)
        console.print("[cyan]Resolved Dockerfile Contents:[/cyan]")
        console.print(f"\n{dockerfile_contents}\n")
    else:
        raise ValueError("Either manifest_path or dockerfile_path must be provided")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        dockerfile_path = temp_path / "Dockerfile"
        config_source = RENOVATE_CONFIG_PATH
        config_path = temp_path / "renovate.json5"
        console.print("[cyan]Preparing renovate workspace...[/cyan]")
        dockerfile_path.write_text(dockerfile_contents, encoding="utf-8")
        config_path.write_text(
            config_source.read_text(encoding="utf-8"), encoding="utf-8"
        )
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
        output = (result.stdout or "").strip()

    console.print("[cyan]Generating JSON summary...[/cyan]")
    summary = build_summary(output)
    updates = summary.get("updates", [])
    if updates:
        console.print(
            f"[yellow]Renovate found {len(updates)} update candidates.[/yellow]"
        )
    else:
        console.print("[green]Renovate: No updates found.[/green]")
    return summary
