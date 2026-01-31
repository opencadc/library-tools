"""Integration tests for the hadolint CLI workflow."""

from __future__ import annotations

from pathlib import Path

import pytest

from library.cli.hadolint import run
from tests.cli.conftest import skip_if_docker_unavailable


@pytest.mark.integration
def test_hadolint_chain_dockerfile(fixtures_dir: Path) -> None:
    """Run hadolint end-to-end using a local Dockerfile."""
    skip_if_docker_unavailable()
    dockerfile_path = fixtures_dir / "Dockerfile.hadolint.good"
    result = run(None, dockerfile_path, False)
    assert result == 0
