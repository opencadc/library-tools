"""Hadolint CLI helpers."""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from library import manifest
from library.utils.git import fetch_dockerfile


def run_docker(command: list[str]) -> int:
    """Run a Docker command.

    Args:
        command: Full Docker command to execute.

    Returns:
        The subprocess return code.
    """
    return subprocess.run(command, check=False).returncode


def run_hadolint(manifest_path: Path) -> int:
    """Run hadolint against the manifest Dockerfile.

    Args:
        manifest_path: Path to the manifest file.

    Returns:
        The hadolint exit code.
    """
    data = manifest.read(manifest_path)
    manifest.validate(data)

    git_info = data["git"]
    build_info = data["build"]
    dockerfile_contents = fetch_dockerfile(
        str(git_info["repo"]),
        git_info.get("fetch", "refs/heads/main"),
        git_info["commit"],
        build_info.get("path", "."),
        build_info.get("dockerfile", "Dockerfile"),
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        dockerfile_path = temp_path / "Dockerfile"
        config_path = Path.cwd() / ".hadolint.yaml"
        dockerfile_path.write_text(dockerfile_contents, encoding="utf-8")
        command = [
            "docker",
            "run",
            "--rm",
            "-i",
            "-v",
            f"{temp_path}:/work",
            "-v",
            f"{config_path}:/work/.hadolint.yaml:ro",
            "-w",
            "/work",
            "hadolint/hadolint",
            "hadolint",
            "--config",
            "/work/.hadolint.yaml",
            "/work/Dockerfile",
        ]
        return run_docker(command)
