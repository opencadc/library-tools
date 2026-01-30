"""Tests for docker utilities."""

from __future__ import annotations

import subprocess
import sys

from library.utils import docker


def test_image_exists_true_when_inspect_succeeds(monkeypatch) -> None:
    """Return True when docker image inspect succeeds."""
    captured = {}

    def fake_run(command, check=False, stdout=None, stderr=None):
        captured["command"] = command
        captured["stdout"] = stdout
        captured["stderr"] = stderr
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(docker.subprocess, "run", fake_run)

    assert docker.image_exists("docker.io/library/alpine:3.20") is True
    assert captured["command"] == [
        "docker",
        "image",
        "inspect",
        "docker.io/library/alpine:3.20",
    ]
    assert captured["stdout"] is subprocess.DEVNULL
    assert captured["stderr"] is subprocess.DEVNULL


def test_image_exists_false_when_inspect_fails(monkeypatch) -> None:
    """Return False when docker image inspect fails."""
    def fake_run(command, check=False, stdout=None, stderr=None):
        return subprocess.CompletedProcess(command, 1)

    monkeypatch.setattr(docker.subprocess, "run", fake_run)

    assert docker.image_exists("docker.io/library/alpine:3.20") is False


def test_pull_quiet_suppresses_output(monkeypatch) -> None:
    """Quiet pulls should not emit console output and use pipes."""
    calls = []
    captured = {}

    def fake_print(*args, **kwargs):
        calls.append((args, kwargs))

    def fake_run(command, check=False, stdout=None, stderr=None, text=None):
        captured["command"] = command
        captured["stdout"] = stdout
        captured["stderr"] = stderr
        captured["text"] = text
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(docker.console, "print", fake_print)
    monkeypatch.setattr(docker.subprocess, "run", fake_run)

    docker.pull("docker.io/library/alpine:3.20", quiet=True)

    assert calls == []
    assert captured["stdout"] is subprocess.PIPE
    assert captured["stderr"] is subprocess.PIPE
    assert captured["text"] is True


def test_pull_quiet_emits_stderr_on_failure(monkeypatch) -> None:
    """Quiet pulls should emit stderr on failure."""
    calls = []

    def fake_print(*args, **kwargs):
        calls.append((args, kwargs))

    def fake_run(command, check=False, stdout=None, stderr=None, text=None):
        return subprocess.CompletedProcess(command, 1, "", "boom")

    monkeypatch.setattr(docker.subprocess, "run", fake_run)
    monkeypatch.setattr("builtins.print", fake_print)

    docker.pull("docker.io/library/alpine:3.20", quiet=True)

    assert len(calls) == 1
    assert calls[0][0][0] == "boom"
    assert calls[0][1].get("file") is sys.stderr


def test_run_emit_output_false_suppresses_console(monkeypatch) -> None:
    """emit_output=False should avoid console output."""
    calls = []

    def fake_print(*args, **kwargs):
        calls.append((args, kwargs))

    def fake_run(command, check=False, stdout=None, stderr=None, text=None):
        return subprocess.CompletedProcess(command, 0, "stdout", "stderr")

    monkeypatch.setattr(docker.console, "print", fake_print)
    monkeypatch.setattr(docker.subprocess, "run", fake_run)

    docker.run(["docker", "run", "busybox"], verbose=True, emit_output=False)

    assert calls == []
