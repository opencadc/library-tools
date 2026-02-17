"""Tests for manifest schema validation."""

from __future__ import annotations

import pytest

from library.schema import Manifest


def _default_scan_tool() -> dict[str, object]:
    return {
        "id": "default-scanner",
        "parser": "trivy",
        "image": "docker.io/aquasec/trivy:latest",
        "command": [
            "trivy",
            "image",
            "--config",
            "{{inputs.trivy}}",
            "--format",
            "json",
            "--output",
            "/outputs/scan.json",
            "{{image.reference}}",
        ],
        "inputs": {
            "trivy": {"source": "default", "destination": "/config/trivy.yaml"},
        },
        "socket": True,
        "outputs": "/outputs/",
    }


def _minimal_manifest() -> dict[str, object]:
    return {
        "version": 1,
        "registry": {
            "host": "images.canfar.net",
            "project": "library",
            "image": "schema-test",
        },
        "maintainers": [
            {"name": "Schema Test", "email": "schema-test@example.com"},
        ],
        "git": {
            "repo": "https://github.com/opencadc/canfar-library",
            "commit": "1234567890123456789012345678901234567890",
        },
        "build": {
            "context": ".",
            "file": "Dockerfile",
            "tags": ["canfar-library/schema-test:latest"],
        },
        "metadata": {
            "discovery": {
                "title": "Schema Test",
                "description": "Schema validation test image",
                "source": "https://github.com/opencadc/canfar-library",
                "url": "https://images.canfar.net/library/schema-test",
                "documentation": "https://canfar.net/docs/user-guide",
                "version": "1.0.0",
                "revision": "1234567890123456789012345678901234567890",
                "created": "2026-02-05T12:00:00Z",
                "authors": "Schema Test",
                "licenses": "MIT",
                "keywords": ["schema", "validation"],
                "domain": ["astronomy"],
                "kind": ["headless"],
                "tools": ["python"],
            }
        },
        "config": {
            "policy": "default",
            "conflicts": "warn",
            "tools": [_default_scan_tool()],
            "cli": {"scan": "default-scanner"},
        },
    }


def test_config_tools_accept_list_shape() -> None:
    """Manifest loads when tools are configured as a tool definition list."""
    data = _minimal_manifest()
    manifest = Manifest(**data)

    assert manifest.config.tools[0].id == "default-scanner"
    assert manifest.config.cli["scan"] == "default-scanner"


def test_config_requires_explicit_policy_and_conflicts() -> None:
    """Schema requires flattened config policy and conflicts fields."""
    data = _minimal_manifest()
    del data["config"]["policy"]
    del data["config"]["conflicts"]

    with pytest.raises(ValueError):
        Manifest(**data)


def test_config_rejects_removed_tooling_section() -> None:
    """config.tooling should be rejected by schema."""
    data = _minimal_manifest()
    data["config"]["tooling"] = {}

    with pytest.raises(ValueError):
        Manifest(**data)


def test_discovery_deprecated_defaults_to_false() -> None:
    """Discovery deprecated flag should default to false."""
    data = _minimal_manifest()
    manifest = Manifest(**data)

    assert manifest.metadata.discovery.deprecated is False


def test_discovery_kind_required() -> None:
    """Discovery kind must be provided for classification."""
    data = _minimal_manifest()
    del data["metadata"]["discovery"]["kind"]

    with pytest.raises(ValueError):
        Manifest(**data)


def test_discovery_kind_rejects_unknown_values() -> None:
    """Discovery kind must be one of the supported values."""
    data = _minimal_manifest()
    data["metadata"]["discovery"]["kind"] = ["unknown"]

    with pytest.raises(ValueError):
        Manifest(**data)


def test_manifest_deprecated_methods_removed() -> None:
    """Deprecated manifest helper methods are removed."""
    assert not hasattr(Manifest, "dockerfile")
    assert not hasattr(Manifest, "build_container_image")
