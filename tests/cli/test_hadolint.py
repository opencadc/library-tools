"""Tests for the hadolint CLI command."""

from __future__ import annotations

import subprocess

from tests.cli.conftest import cli


def test_library_hadolint_invokes_docker(cli_runner, monkeypatch, fixtures_dir) -> None:
    """Invoke hadolint using a manifest path."""
    captured = {}

    def fake_run(command, verbose=False):
        captured["command"] = command
        captured["verbose"] = verbose
        return subprocess.CompletedProcess(command, 0, "")

    monkeypatch.setattr("library.cli.hadolint.docker.run", fake_run)
    monkeypatch.setattr(
        "library.cli.hadolint.fetch_dockerfile",
        lambda *_args, **_kwargs: "FROM scratch",
    )
    result = cli_runner.invoke(
        cli, ["hadolint", str(fixtures_dir / "manifest.valid.yml")]
    )
    assert result.exit_code == 0
    assert captured["verbose"] is False
    assert "--verbose" not in captured["command"]
    assert "FROM scratch" in result.stdout


def test_library_hadolint_accepts_dockerfile(cli_runner, monkeypatch, tmp_path) -> None:
    """Invoke hadolint using a Dockerfile path."""
    dockerfile_path = tmp_path / "Dockerfile"
    dockerfile_path.write_text("FROM scratch", encoding="utf-8")

    def fake_run(command, verbose=False):
        return subprocess.CompletedProcess(command, 0, "")

    monkeypatch.setattr("library.cli.hadolint.docker.run", fake_run)
    result = cli_runner.invoke(cli, ["hadolint", "--dockerfile", str(dockerfile_path)])
    assert result.exit_code == 0


def test_library_hadolint_accepts_verbose_flag(
    cli_runner, monkeypatch, tmp_path
) -> None:
    """Enable hadolint verbose output via CLI flag."""
    dockerfile_path = tmp_path / "Dockerfile"
    dockerfile_path.write_text("FROM scratch", encoding="utf-8")
    captured = {}

    def fake_run(command, verbose=False):
        captured["command"] = command
        captured["verbose"] = verbose
        return subprocess.CompletedProcess(command, 0, "")

    monkeypatch.setattr("library.cli.hadolint.docker.run", fake_run)
    result = cli_runner.invoke(
        cli, ["hadolint", "--dockerfile", str(dockerfile_path), "--verbose"]
    )
    assert result.exit_code == 0
    assert captured["verbose"] is True
    assert "--verbose" in captured["command"]
