"""Integration tests for the hadolint CLI workflow."""

from __future__ import annotations

from pathlib import Path

import pytest
from yaml import safe_dump

from library.cli.hadolint import run
from tests.cli.conftest import skip_if_docker_unavailable


@pytest.mark.integration
def test_hadolint_chain_manifest(fixtures_dir: Path, tmp_path: Path) -> None:
    """Run hadolint end-to-end using a manifest-resolved Dockerfile."""
    skip_if_docker_unavailable()
    dockerfile_path = (fixtures_dir / "Dockerfile.hadolint.good").resolve()
    manifest_path = tmp_path / ".library.manifest.yaml"
    manifest_path.write_text(
        safe_dump(
            {
                "build": {
                    "context": str(dockerfile_path.parent),
                    "file": dockerfile_path.name,
                }
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    result = run(manifest_path, False)
    assert result == 0
