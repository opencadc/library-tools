"""Tests for the trivy CLI command."""

from __future__ import annotations

import subprocess

from tests.cli.conftest import cli


def test_library_scan_invokes_trivy_with_json(cli_runner, monkeypatch) -> None:
    """Invoke scan and assert Trivy args include JSON + severity."""
    captured = {}

    def fake_run(command, verbose=False, emit_output=True, stream_output=False):
        captured["command"] = command
        return subprocess.CompletedProcess(command, 0, "[]", "")

    monkeypatch.setattr("library.cli.trivy.docker.run", fake_run)
    monkeypatch.setattr("library.cli.trivy.docker.pull", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("library.cli.trivy.docker.image_exists", lambda *_args, **_kwargs: True)

    result = cli_runner.invoke(cli, ["scan", "docker.io/library/alpine:3.20"])

    assert result.exit_code == 0
    assert "--format" in captured["command"]
    assert "json" in captured["command"]
    assert "--severity" in captured["command"]
    assert "HIGH,CRITICAL" in captured["command"]
    assert result.stdout.strip() == "[]"


def test_library_scan_pulls_missing_image(cli_runner, monkeypatch) -> None:
    """Pull target image when it is not present locally."""
    pulled = {}

    def fake_pull(image):
        pulled["image"] = image

    monkeypatch.setattr("library.cli.trivy.docker.pull", fake_pull)
    monkeypatch.setattr(
        "library.cli.trivy.docker.image_exists", lambda *_args, **_kwargs: False
    )
    monkeypatch.setattr(
        "library.cli.trivy.docker.run",
        lambda command, verbose=False, emit_output=True, stream_output=False: subprocess.CompletedProcess(
            command, 0, "[]", ""
        ),
    )

    result = cli_runner.invoke(cli, ["scan", "docker.io/library/alpine:3.20"])

    assert result.exit_code == 0
    assert pulled["image"] == "docker.io/library/alpine:3.20"


def test_library_scan_mounts_cache_dir(cli_runner, monkeypatch, tmp_path) -> None:
    """Mount the cache directory and export TRIVY_CACHE_DIR."""
    cache_dir = tmp_path / "trivy-cache"
    captured = {}

    def fake_run(command, verbose=False, emit_output=True, stream_output=False):
        captured["command"] = command
        return subprocess.CompletedProcess(command, 0, "[]", "")

    monkeypatch.setattr("library.cli.trivy.docker.run", fake_run)
    monkeypatch.setattr("library.cli.trivy.docker.pull", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("library.cli.trivy.docker.image_exists", lambda *_args, **_kwargs: True)

    result = cli_runner.invoke(
        cli,
        ["scan", "docker.io/library/alpine:3.20", "--cache-dir", str(cache_dir)],
    )

    assert result.exit_code == 0
    joined = " ".join(captured["command"])
    assert f"{cache_dir}:/trivy-cache" in joined
    assert "TRIVY_CACHE_DIR=/trivy-cache" in joined
