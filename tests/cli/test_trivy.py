"""Tests for the trivy CLI command."""

from __future__ import annotations

from tests.cli.conftest import cli, skip_if_docker_unavailable


def test_library_scan_reports_results(cli_runner, tmp_path) -> None:
    """Scan an image and report results using JSON output."""
    skip_if_docker_unavailable()
    cache_dir = tmp_path / "trivy-cache"

    result = cli_runner.invoke(
        cli,
        ["scan", "docker.io/library/alpine:3.19", "--cache-dir", str(cache_dir)],
    )

    assert result.exit_code in {0, 1}
    assert cache_dir.exists()
    assert "Trivy" in result.stdout
    if "Trivy vulnerabilities found" in result.stdout:
        assert result.exit_code == 1
    if "Trivy: No vulnerabilities found." in result.stdout:
        assert result.exit_code == 0
