"""Docker execution helpers."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from functools import lru_cache
import sys
from typing import Any, cast

import docker as docker_sdk
from docker.errors import APIError, DockerException, ImageNotFound

from library.utils.console import console


@dataclass(slots=True)
class ContainerResult:
    """Container execution result."""

    stdout: str
    stderr: str
    exit_code: int


@lru_cache(maxsize=1)
def get_client() -> docker_sdk.DockerClient:
    """Get a cached Docker client.

    Returns:
        DockerClient: Docker SDK client.
    """
    return docker_sdk.from_env()


def image_exists(image: str) -> bool:
    """Check whether a Docker image exists locally.

    Args:
        image: Docker image to inspect.

    Returns:
        True if the image exists locally.
    """
    try:
        get_client().images.get(image)
        return True
    except ImageNotFound:
        return False
    except DockerException as exc:
        console.print(f"[red]Docker: Failed to inspect {image}: {exc}[/red]")
        return False


def pull(image: str, *, quiet: bool = False) -> None:
    """Pull a Docker image with follow-along logs.

    Args:
        image: Docker image to pull.
        quiet: Whether to suppress output.
    """
    if not quiet:
        console.print(f"[cyan]Docker: Pulling Image {image}[/cyan]")
    try:
        get_client().images.pull(image)
        if not quiet:
            console.print("[cyan]Docker: Pull Complete.[/cyan]")
    except APIError as exc:
        if quiet:
            print(str(exc), end="", file=sys.stderr)
        else:
            console.print(f"[red]Docker: Pull failed: {exc}[/red]")
    except DockerException as exc:
        if quiet:
            print(str(exc), end="", file=sys.stderr)
        else:
            console.print(f"[red]Docker: Pull failed: {exc}[/red]")


def run(
    image: str,
    command: Sequence[str],
    *,
    volumes: Mapping[str, Mapping[str, str]] | None = None,
    environment: Mapping[str, str] | None = None,
    working_dir: str | None = None,
    stdin_open: bool = False,
    verbose: bool,
    emit_output: bool = True,
    stream_output: bool = False,
) -> ContainerResult:
    """Run a Docker container and capture logs.

    Args:
        image: Image to run.
        command: Command to execute inside the container.
        volumes: Volume bindings.
        environment: Environment variables.
        working_dir: Container working directory.
        stdin_open: Whether to keep stdin open.
        verbose: Whether to emit stdout from the process.
        emit_output: Whether to emit process output to console.
        stream_output: Whether to stream output directly to stdout/stderr.

    Returns:
        The container execution result.
    """
    client = get_client()
    if emit_output and not stream_output:
        console.print("[cyan]Docker: Starting Container...[/cyan]")

    volume_config = (
        {key: dict(value) for key, value in volumes.items()} if volumes else None
    )
    environment_config = dict(environment) if environment else None

    container = client.containers.create(
        image=image,
        command=list(command),
        working_dir=working_dir,
        environment=environment_config,
        volumes=volume_config,
        stdin_open=stdin_open,
        tty=False,
    )

    stdout_chunks: list[str] = []
    stderr_chunks: list[str] = []

    try:
        container.start()
        try:
            log_stream = cast(Any, container).logs(
                stream=True, follow=True, stdout=True, stderr=True, demux=True
            )
            for stdout_bytes, stderr_bytes in log_stream:
                if stdout_bytes:
                    stdout_text = stdout_bytes.decode("utf-8", errors="replace")
                    stdout_chunks.append(stdout_text)
                    if stream_output:
                        print(stdout_text, end="")
                if stderr_bytes:
                    stderr_text = stderr_bytes.decode("utf-8", errors="replace")
                    stderr_chunks.append(stderr_text)
                    if stream_output:
                        print(stderr_text, end="", file=sys.stderr)
        except TypeError:
            streamed = False
            if stream_output:
                raw_stream = container.logs(
                    stream=True, follow=True, stdout=True, stderr=True
                )
                for chunk in raw_stream:
                    if not chunk:
                        continue
                    if isinstance(chunk, bytes):
                        text = chunk.decode("utf-8", errors="replace")
                    else:
                        text = str(chunk)
                    print(text, end="")
                streamed = True

            result = container.wait()
            exit_code = int(result.get("StatusCode", 1))
            stdout_data = container.logs(stream=False, stdout=True, stderr=False)
            stderr_data = container.logs(stream=False, stdout=False, stderr=True)
            stdout = (
                stdout_data.decode("utf-8", errors="replace")
                if isinstance(stdout_data, (bytes, bytearray))
                else str(stdout_data)
            )
            stderr = (
                stderr_data.decode("utf-8", errors="replace")
                if isinstance(stderr_data, (bytes, bytearray))
                else str(stderr_data)
            )

            if emit_output and not stream_output:
                if stderr:
                    print(stderr, end="", file=sys.stderr)
                if verbose and stdout:
                    print(stdout, end="")
                console.print(
                    "[cyan]Docker: Container Finished with exit code "
                    f"{exit_code}.[/cyan]"
                )
            elif stream_output and not streamed:
                if stdout:
                    print(stdout, end="")
                if stderr:
                    print(stderr, end="", file=sys.stderr)

            return ContainerResult(stdout=stdout, stderr=stderr, exit_code=exit_code)

        result = container.wait()
        exit_code = int(result.get("StatusCode", 1))
    finally:
        try:
            container.remove(force=True)
        except DockerException:
            pass

    stdout = "".join(stdout_chunks)
    stderr = "".join(stderr_chunks)

    if emit_output and not stream_output:
        if stderr:
            print(stderr, end="", file=sys.stderr)
        if verbose and stdout:
            print(stdout, end="")
        console.print(
            f"[cyan]Docker: Container Finished with exit code {exit_code}.[/cyan]"
        )

    return ContainerResult(stdout=stdout, stderr=stderr, exit_code=exit_code)


def run_container(
    image: str,
    command: Sequence[str],
    *,
    volumes: Mapping[str, Mapping[str, str]] | None = None,
    environment: Mapping[str, str] | None = None,
    working_dir: str | None = None,
    stdin_open: bool = False,
    verbose: bool,
    emit_output: bool = True,
    stream_output: bool = False,
) -> ContainerResult:
    """Backward-compatible wrapper for run.

    Args:
        image: Image to run.
        command: Command to execute inside the container.
        volumes: Volume bindings.
        environment: Environment variables.
        working_dir: Container working directory.
        stdin_open: Whether to keep stdin open.
        verbose: Whether to emit stdout from the process.
        emit_output: Whether to emit process output to console.
        stream_output: Whether to stream output directly to stdout/stderr.

    Returns:
        The container execution result.
    """
    return run(
        image,
        command,
        volumes=volumes,
        environment=environment,
        working_dir=working_dir,
        stdin_open=stdin_open,
        verbose=verbose,
        emit_output=emit_output,
        stream_output=stream_output,
    )
