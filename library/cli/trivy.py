"""Trivy CLI helpers."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from library import TRIVY_CONFIG_PATH
from library.utils import docker
from library.utils.console import console


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
        config_path.write_text(
            TRIVY_CONFIG_PATH.read_text(encoding="utf-8"), encoding="utf-8"
        )

        console.print("[cyan]Running trivy...[/cyan]")

        command = [
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

        result = docker.run(
            "docker.io/aquasec/trivy:latest",
            command,
            volumes={
                "/var/run/docker.sock": {
                    "bind": "/var/run/docker.sock",
                    "mode": "rw",
                },
                str(cache_dir): {"bind": "/trivy-cache", "mode": "rw"},
                str(temp_path): {"bind": "/work", "mode": "rw"},
            },
            working_dir="/work",
            environment={"TRIVY_CACHE_DIR": "/trivy-cache"},
            verbose=verbose,
            emit_output=False,
        )

        output = result.stdout.strip()
        vulnerabilities = 0
        if output:
            try:
                parsed = json.loads(output)
                console.print_json(json.dumps(parsed, indent=2))
                for item in parsed.get("Results", []):
                    vulnerabilities += len(item.get("Vulnerabilities", []))
            except json.JSONDecodeError:
                console.print("[red]Trivy: Failed to parse JSON output.[/red]")
        if vulnerabilities:
            console.print(f"[red]Trivy vulnerabilities found: {vulnerabilities}[/red]")
        else:
            console.print("[green]Trivy: No vulnerabilities found.[/green]")

        return result.exit_code
