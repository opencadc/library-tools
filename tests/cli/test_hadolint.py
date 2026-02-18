"""Tests for the lint CLI command."""

from __future__ import annotations

from pathlib import Path

from yaml import safe_dump

from tests.cli.conftest import cli, skip_if_docker_unavailable


def _write_manifest(path: Path, dockerfile: Path) -> None:
    payload = {
        "build": {
            "context": str(dockerfile.parent),
            "file": dockerfile.name,
        }
    }
    path.write_text(safe_dump(payload, sort_keys=False), encoding="utf-8")


def test_library_hadolint_discovers_default_manifest(cli_runner, fixtures_dir) -> None:
    """Lint should discover .library.manifest.yaml from cwd by default."""
    skip_if_docker_unavailable()
    dockerfile_path = (fixtures_dir / "Dockerfile.hadolint.good").resolve()

    with cli_runner.isolated_filesystem():
        manifest_path = Path(".library.manifest.yaml")
        _write_manifest(manifest_path, dockerfile_path)
        result = cli_runner.invoke(cli, ["lint"])

    assert result.exit_code == 0
    assert "Hadolint: No violations found" in result.stdout
    assert "Hadolint completed successfully" in result.stdout


def test_library_hadolint_reports_violations(cli_runner, fixtures_dir, tmp_path) -> None:
    """Lint should report violations from manifest-resolved Dockerfile."""
    skip_if_docker_unavailable()
    dockerfile_path = (fixtures_dir / "Dockerfile.hadolint.bad").resolve()
    manifest_path = tmp_path / ".library.manifest.yaml"
    _write_manifest(manifest_path, dockerfile_path)

    result = cli_runner.invoke(cli, ["lint", "--manifest", str(manifest_path)])

    assert result.exit_code == 1
    assert "Hadolint violations found" in result.stdout
    assert "Hadolint failed with exit code" in result.stdout


def test_library_hadolint_accepts_verbose_flag(cli_runner, fixtures_dir, tmp_path) -> None:
    """Enable verbose output when linting."""
    skip_if_docker_unavailable()
    dockerfile_path = (fixtures_dir / "Dockerfile.hadolint.good").resolve()
    manifest_path = tmp_path / ".library.manifest.yaml"
    _write_manifest(manifest_path, dockerfile_path)

    result = cli_runner.invoke(
        cli, ["lint", "--manifest", str(manifest_path), "--verbose"]
    )

    assert result.exit_code == 0
    assert "Running hadolint" in result.stdout
