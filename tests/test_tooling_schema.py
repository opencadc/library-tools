"""Tests for the flattened generic tool schema."""

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
    """ToolInputs destination must be an absolute container path."""
    with pytest.raises(ValueError):
        ToolInputs(source="default", destination="config.yaml")


def test_tool_outputs_must_be_fixed() -> None:
    """Tool outputs path is hardcoded to /outputs/."""
    data = _scan_tool()
    data["outputs"] = "/results/"
    with pytest.raises(ValueError):
        Tool(**data)


def test_command_tokens_must_reference_declared_inputs() -> None:
    """inputs token names in command must exist in tool.inputs."""
    data = _scan_tool()
    data["command"] = [
        "--config",
        "{{inputs.missing}}",
        "--output",
        "/outputs/out.json",
    ]
    with pytest.raises(ValueError):
        Tool(**data)


def test_command_rejects_unsupported_tokens() -> None:
    """Only inputs.* and image.reference tokens are supported."""
    data = _scan_tool()
    data["command"] = ["--output", "{{outputs}}scan.json"]
    with pytest.raises(ValueError):
        Tool(**data)


def test_config_cli_must_reference_known_tool_ids() -> None:
    """Config cli mappings must reference defined tool ids."""
    with pytest.raises(ValueError):
        Config(
            policy="default",
            conflicts="warn",
            tools=[Tool(**_scan_tool())],
            cli={"scan": "missing-tool"},
        )


def test_config_rejects_duplicate_tool_ids() -> None:
    """Config tool list must not contain duplicate tool ids."""
    with pytest.raises(ValueError):
        Config(
            policy="default",
            conflicts="warn",
            tools=[Tool(**_scan_tool()), Tool(**_scan_tool())],
            cli={"scan": "scan-tool"},
        )
