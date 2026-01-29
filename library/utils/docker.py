"""Docker execution helpers."""

from __future__ import annotations

from collections.abc import Sequence
import subprocess

from library.utils.console import console


def pull(image: str) -> None:
    """Pull a Docker image with follow-along logs.

    Args:
        image: Docker image to pull.
    """
    console.print(f"[cyan]Docker: Pulling Image {image}[/cyan]")
    subprocess.run(["docker", "pull", image], check=False)
    console.print("[cyan]Docker: Pull Complete.[/cyan]")


def run(
    command: Sequence[str],
    *,
    verbose: bool,
) -> subprocess.CompletedProcess[str]:
    """Run a Docker command with follow-along logs.

    Args:
        command: Full Docker command to execute.
        verbose: Whether to emit stdout from the process.

    Returns:
        The completed process.
    """
    console.print("[cyan]Docker: Starting Container...[/cyan]")
    process = subprocess.run(
        list(command),
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if process.stderr:
        console.print(process.stderr, end="")
    if verbose and process.stdout:
        console.print(process.stdout, end="")
    console.print(
        f"[cyan]Docker: Container Finished with exit code {process.returncode}.[/cyan]"
    )
    return process
