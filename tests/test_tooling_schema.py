"""Tests for canonical flattened generic tool schema."""

from __future__ import annotations

from pathlib import Path

import pytest

from library.schema import Config, Tool, ToolInputs


def _scan_tool() -> dict[str, object]:
    return {
        "id": "scan-tool",
        "parser": "trivy",
        "image": "docker.io/aquasec/trivy:latest",
        "command": [
            "trivy",
            "image",
            "--config",
            "{{inputs.trivy}}",
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


def test_tool_shape_is_valid() -> None:
    """A minimal tool definition validates with fixed outputs contract."""
    tool = Tool(**_scan_tool())

    assert tool.outputs == "/outputs/"
    assert tool.socket is True


def test_tool_inputs_source_allows_default_or_existing_file(tmp_path: Path) -> None:
    """ToolInputs source supports default or a valid local file path."""
    local_file = tmp_path / "custom.yaml"
    local_file.write_text("severity: HIGH\n", encoding="utf-8")

    default_input = ToolInputs(source="default", destination="/config/a.yaml")
    file_input = ToolInputs(source=local_file, destination="/config/b.yaml")

    assert default_input.source == "default"
    assert Path(file_input.source).name == "custom.yaml"


def test_tool_inputs_destination_must_be_absolute() -> None:
    """Destination path format checks are runtime-manifest concerns."""
    item = ToolInputs(source="default", destination="config.yaml")

    assert item.destination == "config.yaml"


def test_tool_outputs_must_be_fixed() -> None:
    """Tool outputs path is hardcoded to /outputs/."""
    data = _scan_tool()
    data["outputs"] = "/results/"
    with pytest.raises(ValueError):
        Tool(**data)


def test_command_tokens_are_not_validated_in_schema() -> None:
    """Command token semantics are validated in runtime manifest implementation."""
    data = _scan_tool()
    data["command"] = [
        "--config",
        "{{inputs.missing}}",
        "--output",
        "/outputs/out.json",
    ]
    tool = Tool(**data)

    assert tool.command[1] == "{{inputs.missing}}"


def test_unsupported_tokens_are_not_validated_in_schema() -> None:
    """Unsupported token names are validated in runtime manifest implementation."""
    data = _scan_tool()
    data["command"] = ["--output", "{{outputs}}scan.json"]
    tool = Tool(**data)

    assert tool.command[1] == "{{outputs}}scan.json"


def test_config_allows_cli_with_unknown_tool_ids() -> None:
    """CLI mapping integrity checks run in runtime manifest implementation."""
    config = Config(
        policy="default",
        conflicts="warn",
        tools=[Tool(**_scan_tool())],
        cli={"scan": "missing-tool"},
    )

    assert config.cli["scan"] == "missing-tool"


def test_config_allows_duplicate_tool_ids() -> None:
    """Duplicate tool id checks run in runtime manifest implementation."""
    config = Config(
        policy="default",
        conflicts="warn",
        tools=[Tool(**_scan_tool()), Tool(**_scan_tool())],
        cli={"scan": "scan-tool"},
    )

    assert len(config.tools) == 2


def test_config_requires_tools_and_cli_in_schema_contract() -> None:
    """Canonical schema requires full config block for interoperability."""
    with pytest.raises(ValueError):
        Config()


def test_config_rejects_cli_without_tools_in_schema_contract() -> None:
    """Partial config defaults are implemented only in runtime manifest model."""
    with pytest.raises(ValueError):
        Config(cli={"scan": "custom-scan"})
