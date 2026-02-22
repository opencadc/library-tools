"""Integration tests for the hadolint CLI workflow."""

from __future__ import annotations

from pathlib import Path

import pytest
from yaml import safe_dump
from typer.testing import CliRunner

from library.cli.main import cli
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
                "version": 1,
                "registry": {
                    "host": "images.canfar.net",
                    "project": "library",
                    "image": "sample-image",
                },
                "build": {
                    "context": str(dockerfile_path.parent),
                    "file": dockerfile_path.name,
                    "tags": ["latest"],
                },
                "metadata": {
                    "discovery": {
                        "title": "Sample Image",
                        "description": "Sample description for testing.",
                        "source": "https://github.com/opencadc/canfar-library",
                        "url": "https://images.canfar.net/library/sample-image",
                        "documentation": "https://canfar.net/docs/user-guide",
                        "version": "1.0.0",
                        "revision": "1234567890123456789012345678901234567890",
                        "created": "2026-02-05T12:00:00Z",
                        "authors": [
                            {
                                "name": "Example Maintainer",
                                "email": "maintainer@example.com",
                            }
                        ],
                        "licenses": "MIT",
                        "keywords": ["sample", "testing"],
                        "domain": ["astronomy"],
                        "kind": ["headless"],
                    }
                },
                "config": {},
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    runner = CliRunner()
    result = runner.invoke(cli, ["lint", "--manifest", str(manifest_path)])
    assert result.exit_code == 0
