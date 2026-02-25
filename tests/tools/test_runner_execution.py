"""Integration-style tests for generic tool execution scaffolding."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
from yaml import safe_dump

from library import schema
from library.tools.models import ToolRunContext
from library.tools.runner import run
from library.utils import runtime as docker_runtime


def _ensure_docker_and_image(image: str) -> None:
    """Skip when Docker or test image is unavailable."""
    try:
        docker_runtime.get_client().ping()
    except Exception as exc:
        pytest.skip(f"Docker unavailable: {exc}")

    if docker_runtime.image_exists(image):
        return

    docker_runtime.pull(image, quiet=True)
    if not docker_runtime.image_exists(image):
        pytest.skip(f"Image unavailable for integration test: {image}")


def _base_manifest(tool: dict[str, object], cli: dict[str, str]) -> dict[str, object]:
    """Build minimal manifest payload with provided tool config."""
    return {
        "version": 1,
        "registry": {
            "host": "images.canfar.net",
            "project": "library",
            "image": "sample-image",
        },
        "build": {"context": ".", "file": "Dockerfile", "tags": ["latest"]},
        "metadata": {
            "discovery": {
                "title": "Sample Image",
                "description": "Sample description.",
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
        "config": {
            "policy": "default",
            "conflicts": "warn",
            "tools": [tool],
            "cli": cli,
        },
    }


def _write_manifest(path: Path, payload: dict[str, object]) -> None:
    """Persist manifest YAML payload."""
    path.write_text(safe_dump(payload, sort_keys=False), encoding="utf-8")


@pytest.mark.integration
def test_runner_executes_tool_with_default_input(tmp_path: Path) -> None:
    """Runner executes a tool and writes JSON artifact under host outputs dir."""
    image = "docker.io/library/alpine:3.19"
    _ensure_docker_and_image(image)

    tool = {
        "id": "default-scanner",
        "parser": "trivy",
        "image": image,
        "command": [
            "sh",
            "-c",
            'cat {{inputs.trivy}} >/dev/null && printf \'{"ok":true,"image":"%s"}\' \'{{image.reference}}\' > /outputs/example.json',
        ],
        "inputs": {
            "trivy": {"source": "default", "destination": "/config/trivy.yaml"},
        },
        "socket": False,
        "outputs": "/outputs/",
    }
    manifest_path = tmp_path / "manifest.yaml"
    _write_manifest(
        manifest_path,
        _base_manifest(tool=tool, cli={"scan": "default-scanner"}),
    )

    result = run(
        ToolRunContext(
            manifest=manifest_path,
            command="scan",
            image="images.canfar.net/library/example:latest",
            time=datetime(2026, 2, 18, 20, 0, 0, tzinfo=timezone.utc),
        )
    )

    assert result.tool == "default-scanner"
    assert result.exit_code == 0
    assert (
        result.output
        == tmp_path / ".library-tool-outputs" / "default-scanner" / "20260218T200000Z"
    )
    artifact = result.output / "example.json"
    assert artifact.exists()
    assert json.loads(artifact.read_text(encoding="utf-8")) == {
        "ok": True,
        "image": "images.canfar.net/library/example:latest",
    }


@pytest.mark.integration
def test_runner_executes_tool_with_local_input_override(tmp_path: Path) -> None:
    """Runner resolves local input source files from manifest context."""
    image = "docker.io/library/alpine:3.19"
    _ensure_docker_and_image(image)

    local_input = tmp_path / "custom.trivy.yaml"
    local_input.write_text("marker: LOCAL_OVERRIDE\n", encoding="utf-8")

    tool = {
        "id": "default-scanner",
        "parser": "trivy",
        "image": image,
        "command": [
            "sh",
            "-c",
            "grep -q LOCAL_OVERRIDE {{inputs.trivy}} && printf '{\"ok\":true}' > /outputs/example.json",
        ],
        "inputs": {
            "trivy": {
                "source": "./custom.trivy.yaml",
                "destination": "/config/trivy.yaml",
            },
        },
        "socket": False,
        "outputs": "/outputs/",
    }
    manifest_path = tmp_path / "manifest.yaml"
    _write_manifest(
        manifest_path,
        _base_manifest(tool=tool, cli={"scan": "default-scanner"}),
    )

    result = run(
        ToolRunContext(
            manifest=manifest_path,
            command="scan",
            image="images.canfar.net/library/example:latest",
            time=datetime(2026, 2, 18, 20, 5, 0, tzinfo=timezone.utc),
        )
    )

    assert result.exit_code == 0
    assert (
        result.output
        == tmp_path / ".library-tool-outputs" / "default-scanner" / "20260218T200500Z"
    )
    assert (result.output / "example.json").exists()


@pytest.mark.integration
def test_runner_executes_with_explicit_tool_config(tmp_path: Path) -> None:
    """Runner should execute when tool configuration is provided explicitly."""
    image = "docker.io/library/alpine:3.19"
    _ensure_docker_and_image(image)

    manifest_path = tmp_path / "manifest.yaml"
    _write_manifest(
        manifest_path,
        {
            "version": 1,
            "registry": {
                "host": "images.canfar.net",
                "project": "library",
                "image": "sample-image",
            },
            "build": {"context": ".", "file": "Dockerfile", "tags": ["latest"]},
            "metadata": {
                "discovery": {
                    "title": "Sample Image",
                    "description": "Sample description.",
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
            "config": {
                "tools": [
                    {
                        "id": "default-scanner",
                        "parser": "trivy",
                        "image": image,
                        "command": [
                            "sh",
                            "-c",
                            "cat {{inputs.trivy}} >/dev/null && printf '{\"Results\":[]}' > /outputs/scan.json",
                        ],
                        "inputs": {
                            "trivy": {
                                "source": "default",
                                "destination": "/config/trivy.yaml",
                            }
                        },
                        "outputs": "/outputs/",
                    }
                ],
                "cli": {"scan": "default-scanner"},
            },
        },
    )

    result = run(
        ToolRunContext(
            manifest=manifest_path,
            command="scan",
            image="images.canfar.net/library/example:latest",
            time=datetime(2026, 2, 18, 20, 10, 0, tzinfo=timezone.utc),
        )
    )

    assert result.exit_code == 0
    assert (result.output / "scan.json").exists()


@pytest.mark.integration
def test_runner_executes_without_manifest_with_default_input(tmp_path: Path) -> None:
    """Runner executes with explicit tool config and no manifest path."""
    image = "docker.io/library/alpine:3.19"
    _ensure_docker_and_image(image)

    tool = schema.Tool(
        id="default-scanner",
        parser="trivy",
        image=image,
        command=[
            "sh",
            "-c",
            "cat {{inputs.trivy}} >/dev/null && printf '{\"ok\":true}' > /outputs/example.json",
        ],
        inputs={
            "trivy": schema.ToolInputs(
                source="default", destination="/config/trivy.yaml"
            )
        },
        socket=False,
        outputs="/outputs/",
    )

    result = run(
        ToolRunContext(
            manifest=None,
            command="scan",
            image="docker.io/library/alpine:3.19",
            time=datetime(2026, 2, 18, 20, 15, 0, tzinfo=timezone.utc),
            tool=tool,
            output_root=tmp_path,
        )
    )

    assert result.exit_code == 0
    assert (
        result.output
        == tmp_path / ".library-tool-outputs" / "default-scanner" / "20260218T201500Z"
    )
    assert (result.output / "example.json").exists()


def test_runner_rejects_relative_input_without_manifest(tmp_path: Path) -> None:
    """Runner should fail fast when relative input source has no manifest context."""
    relative_input = tmp_path / "custom.trivy.yaml"
    relative_input.write_text("key: value\n", encoding="utf-8")

    tool = schema.Tool(
        id="default-scanner",
        parser="trivy",
        image="docker.io/library/alpine:3.19",
        command=["trivy", "image", "{{image.reference}}"],
        inputs={
            "trivy": schema.ToolInputs(
                source=relative_input,
                destination="/config/trivy.yaml",
            )
        },
        socket=False,
        outputs="/outputs/",
    )

    # Force a relative source after model validation to exercise runtime guardrail.
    object.__setattr__(tool.inputs["trivy"], "source", "custom.trivy.yaml")

    with pytest.raises(ValueError, match="requires a manifest"):
        run(
            ToolRunContext(
                manifest=None,
                command="scan",
                image="docker.io/library/alpine:3.19",
                time=datetime(2026, 2, 18, 20, 20, 0, tzinfo=timezone.utc),
                tool=tool,
                output_root=tmp_path,
            )
        )
