"""Docker execution helpers."""

from __future__ import annotations

from collections.abc import Sequence
import subprocess
import sys

from library.utils.console import console


def image_exists(image: str) -> bool:
    """Check whether a Docker image exists locally.

    Args:
        image: Docker image to inspect.

    Returns:
        True if the image exists locally.
    """
    result = subprocess.run(
        ["docker", "image", "inspect", image],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


def pull(image: str, *, quiet: bool = False) -> None:
    """Pull a Docker image with follow-along logs.

    Args:
        image: Docker image to pull.
        quiet: Whether to suppress output.
    """
    if not quiet:
        console.print(f"[cyan]Docker: Pulling Image {image}[/cyan]")
    result = subprocess.run(
        ["docker", "pull", image],
        check=False,
        stdout=subprocess.PIPE if quiet else None,
        stderr=subprocess.PIPE if quiet else None,
        text=True,
    )
    if not quiet:
        console.print("[cyan]Docker: Pull Complete.[/cyan]")
    if quiet and result.returncode != 0 and result.stderr:
        print(result.stderr, end="", file=sys.stderr)


def run(
    command: Sequence[str],
    *,
    verbose: bool,
    emit_output: bool = True,
    stream_output: bool = False,
) -> subprocess.CompletedProcess[str]:
    """Run a Docker command with follow-along logs.

    Args:
        command: Full Docker command to execute.
        verbose: Whether to emit stdout from the process.
        emit_output: Whether to emit process output to console.
        stream_output: Whether to stream output directly to stdout/stderr.

    Returns:
        The completed process.
    """
    if stream_output:
        return subprocess.run(
            list(command),
            check=False,
            text=True,
        )

    if emit_output:
        console.print("[cyan]Docker: Starting Container...[/cyan]")
    process = subprocess.run(
        list(command),
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if emit_output:
        if process.stderr:
            console.print(process.stderr, end="")
        if verbose and process.stdout:
            console.print(process.stdout, end="")
        console.print(
            "[cyan]Docker: Container Finished with exit code "
            f"{process.returncode}.[/cyan]"
        )
    return process
