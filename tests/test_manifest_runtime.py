"""Tests for schema runtime-loading behavior with defaults helpers."""

from __future__ import annotations

from pathlib import Path

import pytest
from yaml import safe_dump, safe_load

from library.schema import Schema
from library.tools import defaults


def _custom_scan_tool(tool_id: str = "custom-scan") -> dict[str, object]:
    return {
        "id": tool_id,
        "parser": "trivy",
        "image": "docker.io/aquasec/trivy:latest",
        "command": ["trivy", "image", "{{image.reference}}"],
        "inputs": {
            "trivy": {
                "source": "default",
                "destination": "/inputs/.trivy.yaml",
            }
        },
        "outputs": "/outputs/",
    }


def _minimal_manifest_payload(
    config: dict[str, object] | None = None,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "version": 1,
        "registry": {
            "host": "images.canfar.net",
            "project": "library",
            "image": "runtime-test",
        },
        "build": {
            "context": ".",
            "file": "Dockerfile",
            "tags": ["latest"],
        },
        "metadata": {
            "discovery": {
                "title": "Runtime Test",
                "description": "Runtime manifest test.",
                "source": "https://github.com/opencadc/canfar-library",
                "url": "https://images.canfar.net/library/runtime-test",
                "documentation": "https://canfar.net/docs/user-guide",
                "version": "1.0.0",
                "revision": "1234567890123456789012345678901234567890",
                "created": "2026-02-20T00:00:00Z",
                "authors": [{"name": "Runtime", "email": "runtime@example.com"}],
                "licenses": "MIT",
                "keywords": ["runtime"],
                "domain": ["astronomy"],
                "kind": ["headless"],
                "tools": ["python"],
            }
        },
    }
    if config is not None:
        payload["config"] = config
    return payload


def _write_manifest(path: Path, payload: dict[str, object]) -> None:
    path.write_text(safe_dump(payload, sort_keys=False), encoding="utf-8")


def test_default_constructors_return_fresh_models() -> None:
    """Default constructors should return independent runtime models."""
    left = defaults.default_config()
    right = defaults.default_config()

    left.tools[0].image = "docker.io/example/other:1"

    assert right.tools[0].image != "docker.io/example/other:1"


def test_manifest_rejects_missing_config() -> None:
    """Runtime commands require fully materialized manifests."""
    with pytest.raises(ValueError):
        Schema.from_dict(_minimal_manifest_payload(config=None))


def test_manifest_rejects_empty_config_block() -> None:
    """Compact config payloads should fail strict runtime loading."""
    with pytest.raises(ValueError):
        Schema.from_dict(_minimal_manifest_payload(config={}))


def test_manifest_rejects_unknown_cli_mapping() -> None:
    """Runtime manifest should enforce command mapping integrity."""
    with pytest.raises(ValueError, match="unknown tool ids"):
        Schema.from_dict(
            _minimal_manifest_payload(
                config={
                    "policy": "default",
                    "conflicts": "warn",
                    "tools": [_custom_scan_tool()],
                    "cli": {"scan": "missing-tool"},
                }
            )
        )


def test_manifest_rejects_duplicate_tool_ids() -> None:
    """Runtime manifest should reject duplicate tool ids."""
    with pytest.raises(ValueError, match="must be unique"):
        Schema.from_dict(
            _minimal_manifest_payload(
                config={
                    "policy": "default",
                    "conflicts": "warn",
                    "tools": [_custom_scan_tool("dupe"), _custom_scan_tool("dupe")],
                    "cli": {"scan": "dupe"},
                }
            )
        )


def test_manifest_validates_command_tokens() -> None:
    """Runtime manifest should validate templated command tokens."""
    with pytest.raises(ValueError, match="undefined input token"):
        Schema.from_dict(
            _minimal_manifest_payload(
                config={
                    "policy": "default",
                    "conflicts": "warn",
                    "tools": [
                        {
                            **_custom_scan_tool("broken"),
                            "command": ["{{inputs.missing}}"],
                        }
                    ],
                    "cli": {"scan": "broken"},
                }
            )
        )


def test_manifest_normalizes_relative_input_source_from_yaml(tmp_path: Path) -> None:
    """Relative tool input source paths should resolve from manifest location."""
    dockerfile = tmp_path / "Dockerfile"
    dockerfile.write_text("FROM alpine:3.20\n", encoding="utf-8")
    trivy_cfg = tmp_path / "custom.trivy.yaml"
    trivy_cfg.write_text("severity: HIGH\n", encoding="utf-8")
    manifest_path = tmp_path / ".library.manifest.yaml"

    payload = _minimal_manifest_payload(
        config={
            "policy": "default",
            "conflicts": "warn",
            "tools": [
                {
                    "id": "default-scanner",
                    "parser": "trivy",
                    "image": "docker.io/aquasec/trivy:latest",
                    "command": ["trivy", "image", "{{image.reference}}"],
                    "inputs": {
                        "trivy": {
                            "source": "./custom.trivy.yaml",
                            "destination": "/config/trivy.yaml",
                        }
                    },
                    "outputs": "/outputs/",
                }
            ],
            "cli": {"scan": "default-scanner"},
        }
    )
    payload["build"] = {
        "context": str(tmp_path),
        "file": "Dockerfile",
        "tags": ["latest"],
    }
    _write_manifest(manifest_path, payload)

    model = Schema.from_yaml(manifest_path)
    source = model.config.tools[0].inputs["trivy"].source

    assert str(Path(str(source)).resolve()) == str(trivy_cfg.resolve())


def test_manifest_preserves_absolute_input_source_from_yaml(tmp_path: Path) -> None:
    """Absolute input sources should not be modified by normalization."""
    dockerfile = tmp_path / "Dockerfile"
    dockerfile.write_text("FROM alpine:3.20\n", encoding="utf-8")
    trivy_cfg = tmp_path / "custom.trivy.yaml"
    trivy_cfg.write_text("severity: HIGH\n", encoding="utf-8")
    manifest_path = tmp_path / ".library.manifest.yaml"

    payload = _minimal_manifest_payload(
        config={
            "policy": "default",
            "conflicts": "warn",
            "tools": [
                {
                    "id": "default-scanner",
                    "parser": "trivy",
                    "image": "docker.io/aquasec/trivy:latest",
                    "command": ["trivy", "image", "{{image.reference}}"],
                    "inputs": {
                        "trivy": {
                            "source": str(trivy_cfg.resolve()),
                            "destination": "/config/trivy.yaml",
                        }
                    },
                    "outputs": "/outputs/",
                }
            ],
            "cli": {"scan": "default-scanner"},
        }
    )
    payload["build"] = {
        "context": str(tmp_path),
        "file": "Dockerfile",
        "tags": ["latest"],
    }
    _write_manifest(manifest_path, payload)

    model = Schema.from_yaml(manifest_path)
    source = model.config.tools[0].inputs["trivy"].source

    assert str(source) == str(trivy_cfg.resolve())


def test_manifest_save_writes_full_config_defaults(tmp_path: Path) -> None:
    """Manifest.save should always write materialized config defaults."""
    model = Schema.from_dict(
        _minimal_manifest_payload(
            config=defaults.default_config().model_dump(mode="python")
        )
    )
    output = tmp_path / ".library.manifest.yaml"

    model.save(output)
    saved = safe_load(output.read_text(encoding="utf-8"))

    assert isinstance(saved, dict)
    config = saved["config"]
    assert config["policy"] == "default"
    assert config["conflicts"] == "warn"
    assert config["cli"] == defaults.default_cli()
    assert len(config["tools"]) == 3
