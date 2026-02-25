"""Tests for canonical schema contract validation."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest
from yaml import safe_load

from library.schema import Discovery, Schema


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


def test_discovery_created_defaults_to_utc_now_when_omitted() -> None:
    """Discovery created should be generated with a timezone-aware UTC timestamp."""
    data = _minimal_schema_payload()
    del data["metadata"]["discovery"]["created"]

    model = Schema(**data)
    created = model.metadata.discovery.created

    assert isinstance(created, datetime)
    assert created.tzinfo is not None
    assert created.utcoffset() == timezone.utc.utcoffset(created)


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


def test_schema_validates_tool_command_tokens() -> None:
    """Schema rejects command templates that reference missing inputs."""
    payload = _minimal_schema_payload()
    payload["config"]["tools"][0]["command"] = ["{{inputs.missing}}"]
    with pytest.raises(ValueError, match="undefined input token"):
        Schema(**payload)


def test_schema_validates_cli_mappings() -> None:
    """Schema rejects CLI mappings that target unknown tool ids."""
    payload = _minimal_schema_payload()
    payload["config"]["cli"] = {"scan": "missing-tool"}
    with pytest.raises(ValueError, match="unknown tool ids"):
        Schema(**payload)


def test_schema_rejects_duplicate_tool_ids() -> None:
    """Schema rejects duplicate tool ids in config.tools."""
    payload = _minimal_schema_payload()
    payload["config"]["tools"] = [_default_scan_tool(), _default_scan_tool()]
    payload["config"]["cli"] = {"scan": "default-scanner"}

    with pytest.raises(ValueError, match="must be unique"):
        Schema(**payload)


def test_schema_from_dict_normalizes_relative_input_source(tmp_path: Path) -> None:
    """Schema.from_dict resolves relative input source paths when base_dir is provided."""
    local_input = tmp_path / "custom.trivy.yaml"
    local_input.write_text("severity: HIGH\n", encoding="utf-8")

    payload = _minimal_schema_payload(
        config={
            "tools": [
                {
                    **_default_scan_tool(),
                    "inputs": {
                        "trivy": {
                            "source": "./custom.trivy.yaml",
                            "destination": "/inputs/.trivy.yaml",
                        }
                    },
                }
            ],
            "cli": {"scan": "default-scanner"},
        }
    )
    model = Schema.from_dict(payload, base_dir=tmp_path)

    source = model.config.tools[0].inputs["trivy"].source
    assert str(Path(str(source)).resolve()) == str(local_input.resolve())


def test_schema_from_yaml_normalizes_relative_input_source(tmp_path: Path) -> None:
    """Schema.from_yaml resolves relative tool input paths from manifest directory."""
    local_input = tmp_path / "custom.trivy.yaml"
    local_input.write_text("severity: HIGH\n", encoding="utf-8")
    manifest_path = tmp_path / "manifest.yaml"

    manifest_path.write_text(
        """
version: 1
registry:
  host: images.canfar.net
  project: library
  image: schema-test
build:
  context: .
  file: Dockerfile
  tags:
    - canfar-library/schema-test:latest
metadata:
  discovery:
    title: Schema Test
    description: Schema validation test image
    source: https://github.com/opencadc/canfar-library
    url: https://images.canfar.net/library/schema-test
    documentation: https://canfar.net/docs/user-guide
    version: "1.0.0"
    revision: "1234567890123456789012345678901234567890"
    created: "2026-02-05T12:00:00Z"
    authors:
      - name: Schema Test
        email: schema-test@example.com
    licenses: MIT
    keywords:
      - schema
      - validation
    domain:
      - astronomy
    kind:
      - headless
    tools:
      - python
config:
  tools:
    - id: default-scanner
      parser: trivy
      image: docker.io/aquasec/trivy:latest
      command:
        - trivy
        - image
        - --config
        - "{{inputs.trivy}}"
        - --format
        - json
        - --output
        - /outputs/scan.json
        - "{{image.reference}}"
      inputs:
        trivy:
          source: ./custom.trivy.yaml
          destination: /inputs/.trivy.yaml
      socket: true
      outputs: /outputs/
  cli:
    scan: default-scanner
""".strip()
        + "\n",
        encoding="utf-8",
    )
    model = Schema.from_yaml(manifest_path)

    source = model.config.tools[0].inputs["trivy"].source
    assert str(Path(str(source)).resolve()) == str(local_input.resolve())


def test_schema_save_writes_materialized_yaml(tmp_path: Path) -> None:
    """Schema.save writes a deterministic YAML payload."""
    model = Schema(**_minimal_schema_payload())
    output = tmp_path / "saved.manifest.yaml"

    model.save(output)
    saved = safe_load(output.read_text(encoding="utf-8"))

    assert isinstance(saved, dict)
    assert saved["version"] == 1
    assert saved["config"]["policy"] == "default"


def test_richforms_exclude_metadata_is_present_on_schema_fields() -> None:
    """Schema fields should expose richforms exclusion metadata for init prompts."""
    created_field = Discovery.model_fields["created"]
    revision_field = Discovery.model_fields["revision"]
    config_field = Schema.model_fields["config"]

    assert created_field.json_schema_extra == {"richforms": {"exclude": True}}
    assert revision_field.json_schema_extra == {"richforms": {"exclude": True}}
    assert config_field.json_schema_extra == {"richforms": {"exclude": True}}


def test_model_json_schema_includes_richforms_exclude_metadata() -> None:
    """Generated JSON Schema should include richforms metadata extensions."""
    schema_json = Schema.model_json_schema()
    discovery_fields = schema_json["$defs"]["Discovery"]["properties"]
    config_field = schema_json["properties"]["config"]
    config_def = schema_json["$defs"]["Config"]

    assert discovery_fields["created"]["richforms"]["exclude"] is True
    assert discovery_fields["revision"]["richforms"]["exclude"] is True
    if "richforms" in config_field:
        assert config_field["richforms"]["exclude"] is True
    else:
        assert config_def["richforms"]["exclude"] is True
