"""Hadolint CLI helpers."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from library import HADOLINT_CONFIG_PATH
from library.cli import helpers
from library.utils import docker
from library.utils.console import console


def _prepare_workspace(temp_path: Path, dockerfile_contents: str) -> None:
    """Prepare the hadolint workspace.

    Args:
        temp_path: Workspace directory.
        dockerfile_contents: Dockerfile contents to write.
    """
    dockerfile_path = temp_path / "Dockerfile"
    config_source = HADOLINT_CONFIG_PATH
    config_path = temp_path / ".hadolint.yaml"

    console.print("[cyan]Preparing hadolint workspace...[/cyan]")
    dockerfile_path.write_text(dockerfile_contents, encoding="utf-8")
    config_path.write_text(config_source.read_text(encoding="utf-8"), encoding="utf-8")


def _run_hadolint_container(temp_path: Path, verbose: bool) -> tuple[str, int]:
    """Run hadolint in a container.

    Args:
        temp_path: Workspace directory.
        verbose: Whether to emit verbose output.

    Returns:
        Tuple of hadolint output and exit code.
    """
    docker.pull("docker.io/hadolint/hadolint:latest")
    command = [
        "hadolint",
        "--config",
        "/work/.hadolint.yaml",
        "--format",
        "json",
    ]
    if verbose:
        command.append("--verbose")
    command.append("/work/Dockerfile")
    console.print("[cyan]Running hadolint...[/cyan]")
    result = docker.run(
        "hadolint/hadolint:latest",
        command,
        volumes={str(temp_path): {"bind": "/work", "mode": "rw"}},
        working_dir="/work",
        stdin_open=True,
        verbose=verbose,
    )
    return result.stdout.strip(), result.exit_code


def _emit_hadolint_json(output: str) -> int:
    """Emit hadolint JSON output.

    Args:
        output: Hadolint JSON output string.

    Returns:
        Count of violations.
    """
    violations = 0
    if output:
        parsed = json.loads(output)
        console.print_json(json.dumps(parsed, indent=2))
        if isinstance(parsed, list):
            violations = len(parsed)
    return violations


def _report_hadolint_violations(violations: int) -> None:
    """Report hadolint violations.

    Args:
        violations: Number of violations detected.
    """
    if violations:
        console.print(f"[red]Hadolint violations found: {violations}[/red]")
    else:
        console.print("[green]Hadolint: No violations found.[/green]")


def run(
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
    dockerfile_contents = helpers.resolve_dockerfile_contents(
        manifest_path, dockerfile_path
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        _prepare_workspace(temp_path, dockerfile_contents)
        output, exit_code = _run_hadolint_container(temp_path, verbose)
        violations = _emit_hadolint_json(output)
        _report_hadolint_violations(violations)
        return exit_code
