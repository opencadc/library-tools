"""Trivy CLI helpers."""

from __future__ import annotations

import tempfile
from pathlib import Path
import sys

from library import TRIVY_CONFIG_PATH
from library.utils import docker


def run(image: str, cache_dir: Path, verbose: bool) -> int:
    """Run Trivy against a Docker image.

    Args:
        image: Docker image to scan.
        cache_dir: Trivy DB cache directory.
        verbose: Whether to emit verbose output.

    Returns:
        Trivy exit code.
    """
    if not docker.image_exists(image):
        docker.pull(image, quiet=not verbose)

    docker.pull("docker.io/aquasec/trivy:latest", quiet=not verbose)

    cache_dir = cache_dir.expanduser().resolve()
    cache_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config_path = temp_path / ".trivy.yaml"
        config_path.write_text(TRIVY_CONFIG_PATH.read_text(encoding="utf-8"), encoding="utf-8")

        command = [
            "docker",
            "run",
            "--rm",
            "-v",
            "/var/run/docker.sock:/var/run/docker.sock",
            "-v",
            f"{cache_dir}:/trivy-cache",
            "-e",
            "TRIVY_CACHE_DIR=/trivy-cache",
            "-v",
            f"{temp_path}:/work",
            "-w",
            "/work",
            "docker.io/aquasec/trivy:latest",
            "image",
            "--config",
            "/work/.trivy.yaml",
            "--format",
            "json",
            "--severity",
            "HIGH,CRITICAL",
            "--exit-code",
            "1",
            "--quiet",
            "--no-progress",
            image,
        ]

        process = docker.run(command, verbose=verbose, emit_output=False)

        if process.stderr:
            print(process.stderr, end="", file=sys.stderr)
        if process.stdout:
            print(process.stdout, end="")

        return process.returncode
