"""Hadolint CLI helpers."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from library import manifest
from library.utils import docker
from library.utils.console import console
from library.utils.git import fetch_dockerfile


def pull_image(image: str) -> None:
    """Pull a Docker image with follow-along logs.

    Args:
        image: Docker image to pull.
    """
    console.print(f"[cyan]Pulling Docker image {image}...[/cyan]")
    subprocess.run(["docker", "pull", image], check=False)


def run_hadolint(
    manifest_path: Path | None,
    dockerfile_path: Path | None,
    verbose: bool,
) -> int:
    """Run hadolint against a manifest or a local Dockerfile.

    Args:
        manifest_path: Path to the manifest file.
        dockerfile_path: Path to a local Dockerfile.
        verbose: Whether to emit verbose output.

    Returns:
        The hadolint exit code.

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
        fetch = git_info.get("fetch")
        commit = git_info["commit"]
        path = build_info.get("path")
        dockerfile = build_info.get("dockerfile")

        console.print(f"[cyan]Fetching Dockerfile: {repo}[/cyan]")
        dockerfile_contents = fetch_dockerfile(
            repo,
            fetch,
            commit,
            path,
            dockerfile,
        )
        console.print("[cyan]Resolved Dockerfile Contents:[/cyan]")
        console.print(f"\n{dockerfile_contents}\n")
    else:
        raise ValueError("Either manifest_path or dockerfile_path must be provided")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        dockerfile_path = temp_path / "Dockerfile"
        config_source = Path.cwd() / ".hadolint.yaml"
        config_path = temp_path / ".hadolint.yaml"
        console.print("[cyan]Preparing hadolint workspace...[/cyan]")
        dockerfile_path.write_text(dockerfile_contents, encoding="utf-8")
        config_path.write_text(
            config_source.read_text(encoding="utf-8"), encoding="utf-8"
        )
        pull_image("hadolint/hadolint:latest")
        command = [
            "docker",
            "run",
            "--rm",
            "-i",
            "-v",
            f"{temp_path}:/work",
            "-w",
            "/work",
            "hadolint/hadolint:latest",
            "hadolint",
            "--config",
            "/work/.hadolint.yaml",
        ]
        if verbose:
            command.append("--verbose")
        command.append("/work/Dockerfile")
        console.print("[cyan]Running hadolint...[/cyan]")
        return docker.run(command, verbose=verbose).returncode
