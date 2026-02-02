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


def _emit_container_start(*, emit_output: bool, stream_output: bool) -> None:
    """Emit container startup logs.

    Args:
        emit_output: Whether to emit process output to console.
        stream_output: Whether to stream output directly to stdout/stderr.
    """
    if emit_output and not stream_output:
        console.print("[cyan]Docker: Starting Container...[/cyan]")


def _emit_container_finish(
    *,
    emit_output: bool,
    stream_output: bool,
    verbose: bool,
    stdout: str,
    stderr: str,
    exit_code: int,
    streamed: bool,
) -> None:
    """Emit container completion logs.

    Args:
        emit_output: Whether to emit process output to console.
        stream_output: Whether to stream output directly to stdout/stderr.
        verbose: Whether to emit stdout from the process.
        stdout: Captured stdout content.
        stderr: Captured stderr content.
        exit_code: Exit code from the container.
        streamed: Whether output was already streamed.
    """
    if emit_output and not stream_output:
        if stderr:
            print(stderr, end="", file=sys.stderr)
        if verbose and stdout:
            print(stdout, end="")
        console.print(
            f"[cyan]Docker: Container Finished with exit code {exit_code}.[/cyan]"
        )
        return
    if stream_output and not streamed:
        if stdout:
            print(stdout, end="")
        if stderr:
            print(stderr, end="", file=sys.stderr)


def _build_volume_config(
    volumes: Mapping[str, Mapping[str, str]] | None,
) -> dict[str, dict[str, str]] | None:
    """Build Docker volume configuration.

    Args:
        volumes: Volume bindings.

    Returns:
        Normalized volume configuration or None.
    """
    if not volumes:
        return None
    return {key: dict(value) for key, value in volumes.items()}


def _build_environment_config(
    environment: Mapping[str, str] | None,
) -> dict[str, str] | None:
    """Build Docker environment configuration.

    Args:
        environment: Environment variables.

    Returns:
        Normalized environment configuration or None.
    """
    if not environment:
        return None
    return dict(environment)


def _create_container(
    client: docker_sdk.DockerClient,
    *,
    image: str,
    command: Sequence[str],
    working_dir: str | None,
    environment: Mapping[str, str] | None,
    volumes: Mapping[str, Mapping[str, str]] | None,
    stdin_open: bool,
) -> Any:
    """Create a Docker container.

    Args:
        client: Docker client instance.
        image: Image to run.
        command: Command to execute inside the container.
        working_dir: Container working directory.
        environment: Environment variables.
        volumes: Volume bindings.
        stdin_open: Whether to keep stdin open.

    Returns:
        The created container object.
    """
    volume_config = _build_volume_config(volumes)
    environment_config = _build_environment_config(environment)
    return client.containers.create(
        image=image,
        command=list(command),
        working_dir=working_dir,
        environment=environment_config,
        volumes=volume_config,
        stdin_open=stdin_open,
        tty=False,
    )


def _wait_for_container(container: Any) -> int:
    """Wait for container completion.

    Args:
        container: Container instance.

    Returns:
        Exit code from the container.
    """
    result = container.wait()
    return int(result.get("StatusCode", 1))


def _decode_log_payload(payload: bytes | bytearray | str) -> str:
    """Decode a log payload into text.

    Args:
        payload: Log payload returned by Docker.

    Returns:
        Decoded log text.
    """
    if isinstance(payload, (bytes, bytearray)):
        return payload.decode("utf-8", errors="replace")
    return str(payload)


def _collect_logs_demux(container: Any, *, stream_output: bool) -> tuple[str, str]:
    """Collect logs using Docker demux support.

    Args:
        container: Container instance.
        stream_output: Whether to stream output directly to stdout/stderr.

    Returns:
        Captured stdout and stderr strings.
    """
    stdout_chunks: list[str] = []
    stderr_chunks: list[str] = []
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
    return "".join(stdout_chunks), "".join(stderr_chunks)


def _stream_raw_logs(container: Any) -> None:
    """Stream raw container logs to stdout.

    Args:
        container: Container instance.
    """
    raw_stream = container.logs(stream=True, follow=True, stdout=True, stderr=True)
    for chunk in raw_stream:
        if not chunk:
            continue
        print(_decode_log_payload(chunk), end="")


def _collect_logs_fallback(
    container: Any, *, stream_output: bool
) -> tuple[str, str, int, bool]:
    """Collect logs without demux support.

    Args:
        container: Container instance.
        stream_output: Whether to stream output directly to stdout/stderr.

    Returns:
        Captured stdout, stderr, exit code, and whether logs were streamed.
    """
    streamed = False
    if stream_output:
        _stream_raw_logs(container)
        streamed = True
    exit_code = _wait_for_container(container)
    stdout_data = container.logs(stream=False, stdout=True, stderr=False)
    stderr_data = container.logs(stream=False, stdout=False, stderr=True)
    stdout = _decode_log_payload(stdout_data)
    stderr = _decode_log_payload(stderr_data)
    return stdout, stderr, exit_code, streamed


def _remove_container(container: Any) -> None:
    """Remove a Docker container safely.

    Args:
        container: Container instance.
    """
    try:
        container.remove(force=True)
    except DockerException:
        pass


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
    _emit_container_start(emit_output=emit_output, stream_output=stream_output)
    container = _create_container(
        client,
        image=image,
        command=command,
        working_dir=working_dir,
        environment=environment,
        volumes=volumes,
        stdin_open=stdin_open,
    )
    stdout = ""
    stderr = ""
    exit_code = 1
    streamed = False

    try:
        container.start()
        try:
            stdout, stderr = _collect_logs_demux(container, stream_output=stream_output)
            exit_code = _wait_for_container(container)
            streamed = stream_output
        except TypeError:
            stdout, stderr, exit_code, streamed = _collect_logs_fallback(
                container, stream_output=stream_output
            )
    finally:
        _remove_container(container)

    _emit_container_finish(
        emit_output=emit_output,
        stream_output=stream_output,
        verbose=verbose,
        stdout=stdout,
        stderr=stderr,
        exit_code=exit_code,
        streamed=streamed,
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
