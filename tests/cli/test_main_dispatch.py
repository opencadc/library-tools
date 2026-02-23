"""Tests for direct dispatch usage in CLI command handlers."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from library.cli.main import cli
import library.cli.main as cli_main


def test_cli_main_does_not_import_tool_wrapper_modules() -> None:
    """Main CLI module should not hold wrapper module imports."""
    assert "hadolint" not in cli_main.__dict__
    assert "trivy" not in cli_main.__dict__
    assert "refurbish" not in cli_main.__dict__


def test_lint_calls_dispatch_directly(monkeypatch, tmp_path: Path) -> None:
    """Lint command should dispatch directly with lint command key."""
    calls: list[tuple[str, Path, str | None, bool]] = []

    class _Result:
        exit_code = 0

    class _Dispatched:
        result = _Result()
        payload = {}

    def fake_run_tool_command(command, *, manifest, image, verbose):
        calls.append((command, manifest, image, verbose))
        return _Dispatched()

    monkeypatch.setattr(cli_main.dispatch, "run_tool_command", fake_run_tool_command)
    runner = CliRunner()
    manifest_path = tmp_path / ".library.manifest.yaml"
    manifest_path.write_text("version: 1\n", encoding="utf-8")

    result = runner.invoke(cli, ["lint", "--manifest", str(manifest_path), "--verbose"])

    assert result.exit_code == 0
    assert calls == [("lint", manifest_path, None, True)]


def test_scan_calls_dispatch_directly(monkeypatch, tmp_path: Path) -> None:
    """Scan command should dispatch directly with scan command key."""
    calls: list[tuple[str, Path, str | None, bool]] = []

    class _Result:
        exit_code = 1

    class _Dispatched:
        result = _Result()
        payload = {}

    def fake_run_tool_command(command, *, manifest, image, verbose):
        calls.append((command, manifest, image, verbose))
        return _Dispatched()

    monkeypatch.setattr(cli_main.dispatch, "run_tool_command", fake_run_tool_command)
    runner = CliRunner()
    manifest_path = tmp_path / ".library.manifest.yaml"
    manifest_path.write_text("version: 1\n", encoding="utf-8")

    result = runner.invoke(
        cli,
        [
            "scan",
            "docker.io/library/alpine:3.19",
            "--manifest",
            str(manifest_path),
        ],
    )

    assert result.exit_code == 1
    assert calls == [("scan", manifest_path, "docker.io/library/alpine:3.19", False)]


def test_refurbish_calls_dispatch_directly(monkeypatch, tmp_path: Path) -> None:
    """Refurbish command should dispatch directly and emit JSON from payload."""
    calls: list[tuple[str, Path, str | None, bool]] = []

    class _Result:
        exit_code = 0

    class _Dispatched:
        result = _Result()
        payload = {"updates": []}

    def fake_run_tool_command(command, *, manifest, image, verbose):
        calls.append((command, manifest, image, verbose))
        return _Dispatched()

    monkeypatch.setattr(cli_main.dispatch, "run_tool_command", fake_run_tool_command)
    runner = CliRunner()
    manifest_path = tmp_path / ".library.manifest.yaml"
    manifest_path.write_text("version: 1\n", encoding="utf-8")

    result = runner.invoke(
        cli,
        ["refurbish", "--manifest", str(manifest_path), "--json"],
    )

    assert result.exit_code == 0
    assert calls == [("refurbish", manifest_path, None, False)]
    assert '"updates": []' in result.stdout
