"""Docker execution helpers."""

from __future__ import annotations

from collections.abc import Sequence
import subprocess

from library.utils.console import console


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
    console.print("[cyan]Starting Docker container...[/cyan]")
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
        f"[cyan]Docker container finished with exit code {process.returncode}.[/cyan]"
    )
    return process
