"""Tests for the trivy CLI command."""

from __future__ import annotations


import pytest
from yaml import safe_dump

from library.tools import defaults as runtime_defaults
from library.utils import docker
from tests.cli.conftest import cli, skip_if_docker_unavailable


def _ensure_image_available(image: str) -> None:
    """Skip test if Docker image cannot be confirmed locally."""
    skip_if_docker_unavailable()
    if docker.image_exists(image):
        return
    docker.pull(image, quiet=True)
    if not docker.image_exists(image):
        pytest.skip(f"Image unavailable for scan test: {image}")


def test_library_scan_reports_results(cli_runner, tmp_path) -> None:
    """Scan should run in fallback mode when an image is provided."""
    _ensure_image_available("docker.io/library/alpine:3.19")

    with cli_runner.isolated_filesystem():
        result = cli_runner.invoke(
            cli,
            ["scan", "docker.io/library/alpine:3.19"],
        )

    assert result.exit_code in {0, 1}
    assert "Trivy" in result.stdout


def test_library_scan_accepts_manifest_override(
    cli_runner, fixtures_dir, tmp_path
) -> None:
    """Scan should accept --manifest and still run against explicit image argument."""
    _ensure_image_available("docker.io/library/alpine:3.19")
    manifest = tmp_path / ".library.manifest.yaml"
    manifest.write_text(
        safe_dump(
            {
                "version": 1,
                "registry": {
                    "host": "images.canfar.net",
                    "project": "library",
                    "image": "sample-image",
                },
                "build": {
                    "context": str(
                        (fixtures_dir / "Dockerfile.sample").parent.resolve()
                    ),
                    "file": "Dockerfile.sample",
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
                        "tools": ["python"],
                    }
                },
                "config": runtime_defaults.default_config().model_dump(mode="python"),
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    result = cli_runner.invoke(
        cli,
        [
            "scan",
            "docker.io/library/alpine:3.19",
            "--manifest",
            str(manifest),
        ],
    )

    assert result.exit_code in {0, 1}
    assert "Trivy" in result.stdout


def test_library_scan_derives_image_from_manifest(
    cli_runner, fixtures_dir, tmp_path
) -> None:
    """Scan should derive image reference from manifest when IMAGE is omitted."""
    _ensure_image_available("docker.io/library/alpine:3.19")
    manifest = tmp_path / ".library.manifest.yaml"
    manifest.write_text(
        safe_dump(
            {
                "version": 1,
                "registry": {
                    "host": "docker.io",
                    "project": "library",
                    "image": "alpine",
                },
                "build": {
                    "context": str(
                        (fixtures_dir / "Dockerfile.sample").parent.resolve()
                    ),
                    "file": "Dockerfile.sample",
                    "tags": ["3.19"],
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
                        "tools": ["python"],
                    }
                },
                "config": runtime_defaults.default_config().model_dump(mode="python"),
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    result = cli_runner.invoke(
        cli,
        [
            "scan",
            "--manifest",
            str(manifest),
        ],
    )

    assert result.exit_code in {0, 1}
    assert "docker.io/library/alpine:3.19" in result.stdout


def test_library_scan_fails_without_manifest_or_image(cli_runner) -> None:
    """Scan should fail when no manifest is discoverable and no image is provided."""
    with cli_runner.isolated_filesystem():
        result = cli_runner.invoke(cli, ["scan"])

    assert result.exit_code == 2
    assert isinstance(result.exception, SystemExit)
    assert result.exception.code == 2
