"""Tests for docker utilities."""

from __future__ import annotations

import sys

from docker.errors import APIError, ImageNotFound
import pytest

from library.utils import docker


class FakeImages:
    """Fake Docker images client."""

    def __init__(self) -> None:
        self.get_calls: list[str] = []
        self.pull_calls: list[str] = []
        self.raise_on_get: Exception | None = None
        self.raise_on_pull: Exception | None = None

    def get(self, image: str):
        """Track image inspection requests."""
        self.get_calls.append(image)
        if self.raise_on_get:
            raise self.raise_on_get
        return object()

    def pull(self, image: str):
        """Track image pull requests."""
        self.pull_calls.append(image)
        if self.raise_on_pull:
            raise self.raise_on_pull
        return object()


class FakeContainer:
    """Fake Docker container."""

    def __init__(
        self,
        logs: list[tuple[bytes | None, bytes | None]],
        exit_code: int,
        *,
        demux_unsupported: bool = False,
        raw_logs: list[bytes] | None = None,
        stdout_data: bytes | None = None,
        stderr_data: bytes | None = None,
    ) -> None:
        self._logs = logs
        self._exit_code = exit_code
        self._demux_unsupported = demux_unsupported
        self._raw_logs = raw_logs or []
        self._stdout_data = stdout_data or b""
        self._stderr_data = stderr_data or b""
        self.started = False
        self.removed = False

    def start(self) -> None:
        """Mark the container as started."""
        self.started = True

    def logs(self, **kwargs):
        """Yield log tuples for the container."""
        if kwargs.get("demux") and self._demux_unsupported:
            raise TypeError("demux not supported")
        if kwargs.get("stream") and kwargs.get("follow"):
            if self._demux_unsupported:
                return iter(self._raw_logs)
            return iter(self._logs)
        if kwargs.get("stdout") and not kwargs.get("stderr"):
            return self._stdout_data
        if kwargs.get("stderr") and not kwargs.get("stdout"):
            return self._stderr_data
        return iter(self._logs)

    def wait(self):
        """Return the configured exit code."""
        return {"StatusCode": self._exit_code}

    def remove(self, force=False):
        """Mark the container as removed."""
        self.removed = True


class FakeContainers:
    """Fake Docker containers client."""

    def __init__(self, container: FakeContainer) -> None:
        self.container = container
        self.create_calls: list[dict[str, object]] = []

    def create(self, **kwargs):
        """Track container creation arguments."""
        self.create_calls.append(kwargs)
        return self.container


class FakeClient:
    """Fake Docker client."""

    def __init__(self, images: FakeImages, containers: FakeContainers) -> None:
        self.images = images
        self.containers = containers

    def ping(self) -> bool:
        """Report that the client is reachable."""
        return True


def test_image_exists_true_when_inspect_succeeds(monkeypatch) -> None:
    """Return True when docker image inspect succeeds."""
    images = FakeImages()
    container = FakeContainer([], 0)
    client = FakeClient(images, FakeContainers(container))
    monkeypatch.setattr(docker, "get_client", lambda: client)

    assert docker.image_exists("docker.io/library/alpine:3.20") is True
    assert images.get_calls == ["docker.io/library/alpine:3.20"]


def test_image_exists_false_when_inspect_fails(monkeypatch) -> None:
    """Return False when docker image inspect fails."""
    images = FakeImages()
    images.raise_on_get = ImageNotFound("nope")
    container = FakeContainer([], 0)
    client = FakeClient(images, FakeContainers(container))
    monkeypatch.setattr(docker, "get_client", lambda: client)

    assert docker.image_exists("docker.io/library/alpine:3.20") is False


def test_pull_quiet_suppresses_output(monkeypatch) -> None:
    """Quiet pulls should not emit console output and use pipes."""
    calls = []

    def fake_print(*args, **kwargs):
        """Capture console output."""
        calls.append((args, kwargs))

    images = FakeImages()
    container = FakeContainer([], 0)
    client = FakeClient(images, FakeContainers(container))
    monkeypatch.setattr(docker.console, "print", fake_print)
    monkeypatch.setattr(docker, "get_client", lambda: client)

    docker.pull("docker.io/library/alpine:3.20", quiet=True)

    assert calls == []
    assert images.pull_calls == ["docker.io/library/alpine:3.20"]


def test_pull_quiet_emits_stderr_on_failure(monkeypatch) -> None:
    """Quiet pulls should emit stderr on failure."""
    calls = []

    def fake_print(*args, **kwargs):
        """Capture console output."""
        calls.append((args, kwargs))

    images = FakeImages()
    images.raise_on_pull = APIError("boom")
    container = FakeContainer([], 0)
    client = FakeClient(images, FakeContainers(container))
    monkeypatch.setattr(docker, "get_client", lambda: client)
    monkeypatch.setattr("builtins.print", fake_print)

    docker.pull("docker.io/library/alpine:3.20", quiet=True)

    assert len(calls) == 1
    assert "boom" in calls[0][0][0]
    assert calls[0][1].get("file") is sys.stderr


def test_run_emit_output_false_suppresses_console(monkeypatch) -> None:
    """emit_output=False should avoid console output."""
    calls = []

    def fake_print(*args, **kwargs):
        """Capture console output."""
        calls.append((args, kwargs))

    images = FakeImages()
    container = FakeContainer([(b"stdout", b"stderr")], 0)
    client = FakeClient(images, FakeContainers(container))
    monkeypatch.setattr(docker.console, "print", fake_print)
    monkeypatch.setattr(docker, "get_client", lambda: client)

    docker.run(
        "busybox",
        ["echo", "ok"],
        verbose=True,
        emit_output=False,
    )

    assert calls == []


def test_run_stream_output_passthrough(monkeypatch) -> None:
    """stream_output=True should stream directly without console output."""
    calls = []
    printed = []

    def fake_print(*args, **kwargs):
        """Capture console output."""
        calls.append((args, kwargs))

    def fake_print_out(*args, **kwargs):
        """Capture printed output."""
        printed.append((args, kwargs))

    images = FakeImages()
    container = FakeContainer([(b"stdout", b""), (b"", b"stderr")], 0)
    client = FakeClient(images, FakeContainers(container))
    monkeypatch.setattr(docker.console, "print", fake_print)
    monkeypatch.setattr("builtins.print", fake_print_out)
    monkeypatch.setattr(docker, "get_client", lambda: client)

    result = docker.run(
        "busybox",
        ["echo", "ok"],
        verbose=False,
        stream_output=True,
    )

    assert calls == []
    assert any("stdout" in call[0][0] for call in printed)
    assert any("stderr" in call[0][0] for call in printed)
    assert result.stdout == "stdout"
    assert result.stderr == "stderr"


def test_run_demux_fallback_collects_logs(monkeypatch) -> None:
    """Fallback log collection should capture stdout and stderr."""
    images = FakeImages()
    container = FakeContainer(
        [],
        0,
        demux_unsupported=True,
        stdout_data=b"stdout\n",
        stderr_data=b"stderr\n",
    )
    client = FakeClient(images, FakeContainers(container))
    monkeypatch.setattr(docker, "get_client", lambda: client)

    result = docker.run(
        "busybox",
        ["echo", "ok"],
        verbose=False,
        emit_output=False,
    )

    assert result.stdout == "stdout\n"
    assert result.stderr == "stderr\n"


def _skip_if_docker_unavailable() -> None:
    """Skip tests when Docker is unavailable."""
    try:
        docker.get_client().ping()
    except Exception as exc:
        pytest.skip(f"Docker unavailable: {exc}")


def test_run_alpine_stdout_stderr_exit_zero() -> None:
    """Ensure stdout/stderr capture with success exit code."""
    _skip_if_docker_unavailable()
    docker.pull("docker.io/library/alpine:3.20", quiet=True)
    result = docker.run(
        "docker.io/library/alpine:3.20",
        ["sh", "-c", 'env; echo "error command" >&2; exit 0'],
        verbose=False,
        emit_output=False,
    )

    assert result.exit_code == 0
    assert "PATH=" in result.stdout
    assert "error command" in result.stderr


def test_run_alpine_exit_code_nonzero() -> None:
    """Ensure stderr capture with non-zero exit code."""
    _skip_if_docker_unavailable()
    docker.pull("docker.io/library/alpine:3.20", quiet=True)
    result = docker.run(
        "docker.io/library/alpine:3.20",
        ["sh", "-c", 'echo "error command" >&2; exit 3'],
        verbose=False,
        emit_output=False,
    )

    assert result.exit_code == 3
    assert "error command" in result.stderr
