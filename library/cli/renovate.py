"""Renovate CLI helpers."""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

from library import manifest
from library.utils import docker
from library.utils.console import console
from library.utils.git import fetch_dockerfile


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
        console.print(f"[cyan]Reading Dockerfile from {dockerfile_path}...[/cyan]")
        dockerfile_contents = dockerfile_path.read_text(encoding="utf-8")
    elif manifest_path is not None:
        console.print(f"[cyan]Reading manifest from {manifest_path}...[/cyan]")
        data = manifest.read(manifest_path)
        manifest.validate(data)

        git_info = data["git"]
        build_info = data["build"]
        console.print("[cyan]Fetching Dockerfile from git...[/cyan]")
        dockerfile_contents = fetch_dockerfile(
            str(git_info["repo"]),
            git_info.get("fetch", "refs/heads/main"),
            git_info["commit"],
            build_info.get("path", "."),
            build_info.get("dockerfile", "Dockerfile"),
        )
    else:
        raise ValueError("Either manifest_path or dockerfile_path must be provided")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        dockerfile_path = temp_path / "Dockerfile"
        config_source = Path.cwd() / "renovate.json5"
        config_path = temp_path / "renovate.json5"
        console.print("[cyan]Preparing renovate workspace...[/cyan]")
        dockerfile_path.write_text(dockerfile_contents, encoding="utf-8")
        config_path.write_text(
            config_source.read_text(encoding="utf-8"), encoding="utf-8"
        )
        command = [
            "docker",
            "run",
            "--rm",
            "-i",
            "-e",
            "LOG_FORMAT=json",
            "-e",
            "LOG_LEVEL=debug",
            "-v",
            f"{temp_path}:/repo",
            "-w",
            "/repo",
            "renovate/renovate:latest",
            "--platform=local",
            "--require-config=ignored",
            "--dry-run=full",
        ]
        console.print("[cyan]Pulling Docker image renovate/renovate:latest...[/cyan]")
        subprocess.run(["docker", "pull", "renovate/renovate:latest"], check=False)
        console.print("[cyan]Running renovate...[/cyan]")
        output = (docker.run(command, verbose=verbose).stdout or "").strip()

    console.print("[cyan]Generating JSON summary...[/cyan]")
    return build_summary(output)
