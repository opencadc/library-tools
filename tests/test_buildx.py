"""Tests for buildx command generation."""

from __future__ import annotations

from pathlib import Path
import subprocess

import pytest

from library.schema import Manifest
from library.utils import docker as docker_utils
from tests.cli.conftest import skip_if_docker_unavailable


def _make_manifest(*, build: dict[str, object]) -> Manifest:
    data = {
        "registry": {
            "host": "https://images.canfar.net",
            "project": "library",
            "image": "buildx-test",
        },
        "maintainers": [
            {"name": "Build Test", "email": "build-test@example.com"},
        ],
        "git": {
            "repo": "https://github.com/opencadc/canfar-library",
            "commit": "1234567890123456789012345678901234567890",
        },
        "build": build,
        "metadata": {
            "name": "Buildx Test",
            "description": "Buildx test image",
        },
    }
    return Manifest(**data)


def _has_pair(cmd: list[str], flag: str, value: str) -> bool:
    for idx in range(len(cmd) - 1):
        if cmd[idx] == flag and cmd[idx + 1] == value:
            return True
    return False


def test_build_command_includes_core_and_options() -> None:
    manifest = _make_manifest(
        build={
            "context": "/tmp/build-context",
            "file": "Dockerfile",
            "tag": ["canfar-library/buildx-test:options"],
            "platform": ["linux/amd64"],
            "labels": {"org.opencontainers.image.title": "Buildx Test"},
            "annotations": {"canfar.image.runtime": "python"},
            "options": "--target=runtime --push --build-arg GREETING=hello",
        }
    )

    cmd = manifest.build.command()
    assert cmd[:3] == ["docker", "buildx", "build"]
    assert _has_pair(cmd, "--file", "/tmp/build-context/Dockerfile")
    assert _has_pair(cmd, "--tag", "canfar-library/buildx-test:options")
    assert _has_pair(cmd, "--platform", "linux/amd64")
    assert _has_pair(cmd, "--label", "org.opencontainers.image.title=Buildx Test")
    assert _has_pair(cmd, "--annotation", "canfar.image.runtime=python")
    assert _has_pair(cmd, "--output", "type=docker")
    assert "--target=runtime" in cmd
    assert _has_pair(cmd, "--build-arg", "GREETING=hello")
    assert "--push" in cmd
    assert cmd[-1] == "/tmp/build-context"


@pytest.mark.integration
def test_build_container_image_buildx(tmp_path: Path) -> None:
    skip_if_docker_unavailable()
    buildx = subprocess.run(
        ["docker", "buildx", "version"],
        check=False,
        capture_output=True,
        text=True,
    )
    if buildx.returncode != 0:
        pytest.skip(f"Buildx unavailable: {buildx.stderr.strip()}")

    context_dir = tmp_path / "context"
    context_dir.mkdir()
    dockerfile = context_dir / "Dockerfile"
    dockerfile.write_text(
        "FROM alpine:3.20\nARG GREETING=hello\nRUN echo $GREETING > /greeting.txt\n",
        encoding="utf-8",
    )

    tag = "canfar-library/buildx-test:local"
    manifest = _make_manifest(
        build={
            "context": str(context_dir),
            "file": "Dockerfile",
            "tag": [tag],
            "platform": ["linux/amd64"],
            "options": "--build-arg GREETING=hello",
        }
    )

    manifest.build_container_image()
    assert docker_utils.image_exists(tag)
