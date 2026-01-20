"""Tests for the renovate CLI command."""

from __future__ import annotations

import subprocess

from tests.cli.conftest import cli


def test_library_renovate_emits_updates_summary(
    cli_runner, monkeypatch, fixtures_dir
) -> None:
    """Summarize detected updates from renovate output."""
    mock_output = (
        '{"branchesInformation": [{"branchName": "renovate/ghcr.io-prefix-dev-pixi-0.x", '
        '"upgrades": [{"depName": "ghcr.io/prefix-dev/pixi", "newVersion": "0.63.2", '
        '"newDigest": "sha256:abc", "updateType": "minor"},'
        '{"depName": "ghcr.io/astral-sh/uv", "newVersion": "0.9.1", '
        '"newDigest": "sha256:def", "updateType": "digest"}]}]}\n'
    )

    def fake_run(command, verbose=False):
        return subprocess.CompletedProcess(command, 0, mock_output)

    monkeypatch.setattr("library.cli.renovate.docker.run", fake_run)
    monkeypatch.setattr(
        "library.cli.renovate.fetch_dockerfile",
        lambda *_args, **_kwargs: "FROM scratch",
    )
    result = cli_runner.invoke(
        cli, ["renovate", str(fixtures_dir / "manifest.valid.yml")]
    )
    assert result.exit_code == 0
    assert "ghcr.io/prefix-dev/pixi" in result.stdout
    assert "minor" in result.stdout
    assert "ghcr.io/astral-sh/uv" in result.stdout
    assert "digest" in result.stdout
    assert '"updates"' not in result.stdout
    assert "FROM scratch" in result.stdout


def test_library_renovate_uses_json_log_format(
    cli_runner, monkeypatch, tmp_path
) -> None:
    """Ensure renovate uses JSON log output by default."""
    dockerfile_path = tmp_path / "Dockerfile"
    dockerfile_path.write_text("FROM scratch", encoding="utf-8")
    captured: dict[str, object] = {}

    def fake_run(command: list[str], verbose=False):
        captured["command"] = command
        captured["verbose"] = verbose
        return subprocess.CompletedProcess(command, 0, "")

    monkeypatch.setattr("library.cli.renovate.docker.run", fake_run)
    monkeypatch.setattr(
        "library.cli.renovate.subprocess.run", lambda *_args, **_kwargs: None
    )

    result = cli_runner.invoke(cli, ["renovate", "--dockerfile", str(dockerfile_path)])
    assert result.exit_code == 0
    command = captured["command"]
    assert isinstance(command, list)
    assert "LOG_FORMAT=json" in command
    assert captured["verbose"] is False
    assert '"updates"' not in result.stdout


def test_library_renovate_accepts_verbose_flag(
    cli_runner, monkeypatch, tmp_path
) -> None:
    """Enable renovate verbose output via CLI flag."""
    dockerfile_path = tmp_path / "Dockerfile"
    dockerfile_path.write_text("FROM scratch", encoding="utf-8")
    captured: dict[str, object] = {}

    def fake_run(command: list[str], verbose=False):
        captured["command"] = command
        captured["verbose"] = verbose
        return subprocess.CompletedProcess(command, 0, "")

    monkeypatch.setattr("library.cli.renovate.docker.run", fake_run)
    monkeypatch.setattr(
        "library.cli.renovate.subprocess.run", lambda *_args, **_kwargs: None
    )

    result = cli_runner.invoke(
        cli, ["renovate", "--dockerfile", str(dockerfile_path), "--verbose"]
    )
    assert result.exit_code == 0
    command = captured["command"]
    assert isinstance(command, list)
    assert "LOG_LEVEL=debug" in command
    assert captured["verbose"] is True
    assert '"updates"' not in result.stdout
    assert "No updates detected" in result.stdout


def test_library_renovate_accepts_dockerfile(cli_runner, monkeypatch, tmp_path) -> None:
    """Run renovate against a Dockerfile path."""
    dockerfile_path = tmp_path / "Dockerfile"
    dockerfile_path.write_text("FROM scratch", encoding="utf-8")

    def fake_run(command, verbose=False):
        return subprocess.CompletedProcess(command, 0, '{"updates": []}')

    monkeypatch.setattr("library.cli.renovate.docker.run", fake_run)
    result = cli_runner.invoke(cli, ["renovate", "--dockerfile", str(dockerfile_path)])
    assert result.exit_code == 0
    assert '"updates"' not in result.stdout
