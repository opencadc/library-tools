"""Tests for canonical schema contract validation."""

from __future__ import annotations

import pytest

from library.schema import Schema


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


def _minimal_schema_payload(
    config: dict[str, object] | None = None,
) -> dict[str, object]:
    return {
        "version": 1,
        "registry": {
            "host": "images.canfar.net",
            "project": "library",
            "image": "schema-test",
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
                "authors": [
                    {"name": "Schema Test", "email": "schema-test@example.com"}
                ],
                "licenses": "MIT",
                "keywords": ["schema", "validation"],
                "domain": ["astronomy"],
                "kind": ["headless"],
                "tools": ["python"],
            }
        },
        "config": config
        or {
            "policy": "default",
            "conflicts": "warn",
            "tools": [_default_scan_tool()],
            "cli": {"scan": "default-scanner"},
        },
    }


def test_config_tools_accept_list_shape() -> None:
    """Schema loads when tools are configured as a tool definition list."""
    data = _minimal_schema_payload()
    model = Schema(**data)

    assert model.config.tools[0].id == "default-scanner"
    assert model.config.cli["scan"] == "default-scanner"


def test_config_defaults_policy_and_conflicts() -> None:
    """Schema defaults policy/conflicts when omitted."""
    data = _minimal_schema_payload()
    del data["config"]["policy"]
    del data["config"]["conflicts"]

    model = Schema(**data)
    assert model.config.policy == "default"
    assert model.config.conflicts == "warn"


def test_config_rejects_removed_tooling_section() -> None:
    """config.tooling should be rejected by schema."""
    data = _minimal_schema_payload()
    data["config"]["tooling"] = {}

    with pytest.raises(ValueError):
        Schema(**data)


def test_discovery_deprecated_defaults_to_false() -> None:
    """Discovery deprecated flag should default to false."""
    data = _minimal_schema_payload()
    model = Schema(**data)

    assert model.metadata.discovery.deprecated is False


def test_discovery_kind_required() -> None:
    """Discovery kind must be provided for classification."""
    data = _minimal_schema_payload()
    del data["metadata"]["discovery"]["kind"]

    with pytest.raises(ValueError):
        Schema(**data)


def test_discovery_kind_rejects_unknown_values() -> None:
    """Discovery kind must be one of the supported values."""
    data = _minimal_schema_payload()
    data["metadata"]["discovery"]["kind"] = ["unknown"]

    with pytest.raises(ValueError):
        Schema(**data)


def test_registry_tags_not_part_of_schema_contract() -> None:
    """Schema should not require legacy registry.tags."""
    payload = _minimal_schema_payload()
    model = Schema(**payload)

    assert model.registry.host == "images.canfar.net"


def test_schema_does_not_validate_tool_command_tokens() -> None:
    """Token validation belongs to runtime manifest implementation, not schema."""
    payload = _minimal_schema_payload()
    payload["config"]["tools"][0]["command"] = ["{{inputs.missing}}"]
    model = Schema(**payload)

    assert model.config.tools[0].command == ["{{inputs.missing}}"]


def test_schema_does_not_validate_cli_mappings() -> None:
    """CLI mapping integrity validation belongs to runtime manifest implementation."""
    payload = _minimal_schema_payload()
    payload["config"]["cli"] = {"scan": "missing-tool"}
    model = Schema(**payload)

    assert model.config.cli["scan"] == "missing-tool"


def test_schema_exposes_no_runtime_io_helpers() -> None:
    """Schema should not provide YAML load/save runtime helpers."""
    assert not hasattr(Schema, "from_yaml")
    assert not hasattr(Schema, "from_dict")
    assert not hasattr(Schema, "save")
