"""Integration tests for the hadolint CLI workflow."""

from __future__ import annotations

from pathlib import Path

import pytest

from library.cli.hadolint import run


@pytest.mark.integration
@pytest.mark.skipif(
    not Path("/var/run/docker.sock").exists(), reason="Docker is required"
)
def test_hadolint_chain_dockerfile(tmp_path: Path) -> None:
    """Run hadolint end-to-end using a local Dockerfile."""
    dockerfile_path = tmp_path / "Dockerfile"
    dockerfile_path.write_text("FROM alpine:3.19\n", encoding="utf-8")
    result = run(None, dockerfile_path, False)
    assert result == 0
