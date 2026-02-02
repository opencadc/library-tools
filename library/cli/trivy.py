"""Trivy CLI helpers."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from library import TRIVY_CONFIG_PATH
from library.cli import helpers
from library.utils import docker
from library.utils.console import console


def _ensure_image_present(image: str, *, verbose: bool) -> None:
    """Ensure the target image exists locally.

    Args:
        image: Docker image to scan.
        verbose: Whether to emit verbose output.
    """
    if not docker.image_exists(image):
        docker.pull(image, quiet=not verbose)


def _prepare_cache_dir(cache_dir: Path) -> Path:
    """Prepare the Trivy cache directory.

    Args:
        cache_dir: Trivy DB cache directory.

    Returns:
        Resolved cache directory path.
    """
    resolved = cache_dir.expanduser().resolve()
    resolved.mkdir(parents=True, exist_ok=True)
    return resolved


def _write_trivy_config(temp_path: Path) -> None:
    """Write Trivy configuration into the workspace.

    Args:
        temp_path: Workspace directory.
    """
    config_path = temp_path / ".trivy.yaml"
    config_path.write_text(
        TRIVY_CONFIG_PATH.read_text(encoding="utf-8"), encoding="utf-8"
    )


def _run_trivy_container(
    *,
    temp_path: Path,
    cache_dir: Path,
    image: str,
    verbose: bool,
) -> tuple[str, int]:
    """Run Trivy in a container.

    Args:
        temp_path: Workspace directory.
        cache_dir: Cache directory path.
        image: Docker image to scan.
        verbose: Whether to emit verbose output.

    Returns:
        Tuple of Trivy output and exit code.
    """
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
    return result.stdout.strip(), result.exit_code


def _emit_trivy_results(output: str) -> int:
    """Emit Trivy JSON output and return vulnerability count.

    Args:
        output: Trivy JSON output string.

    Returns:
        Number of vulnerabilities detected.
    """
    vulnerabilities = 0
    if output:
        try:
            parsed = helpers.parse_json_output(output)
            helpers.print_json_output(parsed)
            if isinstance(parsed, dict):
                for item in parsed.get("Results", []):
                    if isinstance(item, dict):
                        vulnerabilities += len(item.get("Vulnerabilities", []))
        except json.JSONDecodeError:
            console.print("[red]Trivy: Failed to parse JSON output.[/red]")
    return vulnerabilities


def _report_trivy_results(vulnerabilities: int) -> None:
    """Report Trivy findings.

    Args:
        vulnerabilities: Number of vulnerabilities detected.
    """
    if vulnerabilities:
        console.print(f"[red]Trivy vulnerabilities found: {vulnerabilities}[/red]")
    else:
        console.print("[green]Trivy: No vulnerabilities found.[/green]")


def run(image: str, cache_dir: Path, verbose: bool) -> int:
    """Run Trivy against a Docker image.

    Args:
        image: Docker image to scan.
        cache_dir: Trivy DB cache directory.
        verbose: Whether to emit verbose output.

    Returns:
        Trivy exit code.
    """
    _ensure_image_present(image, verbose=verbose)
    docker.pull("docker.io/aquasec/trivy:latest", quiet=not verbose)
    cache_dir = _prepare_cache_dir(cache_dir)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        _write_trivy_config(temp_path)
        output, exit_code = _run_trivy_container(
            temp_path=temp_path,
            cache_dir=cache_dir,
            image=image,
            verbose=verbose,
        )
        vulnerabilities = _emit_trivy_results(output)
        _report_trivy_results(vulnerabilities)
        return exit_code
