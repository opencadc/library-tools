"""Runtime manifest implementation built on top of canonical schema."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
import re
from typing import Any, Literal, cast

from pydantic import ConfigDict, Field, field_validator, model_validator
from yaml import dump as yaml_dump
from yaml import safe_load

from library import DEFAULT_LIBRARY_MANIFEST_FILENAME, schema

TOOL_TOKEN_PATTERN = re.compile(r"{{\s*([a-zA-Z0-9_.-]+)\s*}}")


def _normalize_relative_input_sources(
    payload: dict[str, Any], *, base: Path | None
) -> dict[str, Any]:
    """Resolve relative tool input sources to absolute paths from manifest directory."""
    if base is None:
        return payload

    tools = payload.get("config", {}).get("tools", [])

    for tool in tools:
        if not isinstance(tool, dict):
            continue
        inputs = tool.get("inputs")
        if not isinstance(inputs, Mapping):
            continue
        for input_data in inputs.values():
            if not isinstance(input_data, dict):
                continue
            source = input_data.get("source")
            if not isinstance(source, str) or source == "default":
                continue
            source_path = Path(source)
            if source_path.is_absolute():
                continue
            input_data["source"] = str((base / source_path).resolve())

    return payload


class ToolInputs(schema.ToolInputs):
    """Runtime tool input implementation with additional destination checks."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    @field_validator("destination")
    @classmethod
    def validate_destination_path(cls, value: str) -> str:
        """Ensure destination is absolute in the tool container."""
        if not value.startswith("/"):
            raise ValueError("Tool input destination must be an absolute container path.")
        return value


class Tool(schema.Tool):
    """Runtime tool implementation with command token validation."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    @model_validator(mode="after")
    def validate_command_tokens(self) -> "Tool":
        """Validate supported templated tokens used in command args."""
        for part in self.command:
            matches = TOOL_TOKEN_PATTERN.findall(part)
            if ("{{" in part or "}}" in part) and not matches:
                raise ValueError("Malformed template token in tool command.")
            for token_name in matches:
                if token_name == "image.reference":
                    continue
                if token_name.startswith("inputs."):
                    input_name = token_name.split(".", maxsplit=1)[1]
                    if input_name not in self.inputs:
                        raise ValueError(
                            f"Command references undefined input token: {token_name}"
                        )
                    continue
                raise ValueError(f"Unsupported command token: {token_name}")
        return self


class Config(schema.Config):
    """Runtime tool configuration with catalog integrity checks."""

    tools: list[Tool]
    cli: dict[str, str]

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    @model_validator(mode="after")
    def validate_catalog(self) -> "Config":
        """Validate tool id uniqueness and CLI mapping targets."""
        tool_ids = [tool.id for tool in self.tools]
        unique_tool_ids = set(tool_ids)
        if len(unique_tool_ids) != len(tool_ids):
            raise ValueError("Tool ids must be unique in config.tools.")

        unknown_targets = {
            command: tool_id
            for command, tool_id in self.cli.items()
            if tool_id not in unique_tool_ids
        }
        if unknown_targets:
            missing = ", ".join(
                f"{command}->{tool_id}" for command, tool_id in sorted(unknown_targets.items())
            )
            raise ValueError(f"CLI mappings reference unknown tool ids: {missing}")
        return self


DEFAULT_HADOLINT_TOOL: Tool = Tool(
    id="default-linter",
    parser="hadolint",
    image="docker.io/hadolint/hadolint:latest",
    command=[
        "hadolint",
        "--config",
        "{{inputs.hadolint}}",
        "--format",
        "json",
        "{{inputs.dockerfile}}",
    ],
    env={"HADOLINT_CONFIG": "/inputs/.hadolint.yaml"},
    inputs={
        "hadolint": ToolInputs(source="default", destination="/inputs/.hadolint.yaml"),
        "dockerfile": ToolInputs(source="default", destination="/inputs/Dockerfile"),
    },
    socket=False,
    outputs="/outputs/",
)

DEFAULT_TRIVY_TOOL: Tool = Tool(
    id="default-scanner",
    parser="trivy",
    image="docker.io/aquasec/trivy:latest",
    command=[
        "image",
        "--config",
        "{{inputs.trivy}}",
        "--format",
        "json",
        "--output",
        "/outputs/scan.json",
        "--severity",
        "HIGH,CRITICAL",
        "--exit-code",
        "1",
        "--quiet",
        "--no-progress",
        "{{image.reference}}",
    ],
    env={"TRIVY_CACHE_DIR": "/tmp/trivy-cache"},
    inputs={
        "trivy": ToolInputs(source="default", destination="/inputs/.trivy.yaml"),
    },
    socket=True,
    outputs="/outputs/",
)

DEFAULT_REFURBISH_TOOL: Tool = Tool(
    id="default-refurbisher",
    parser="renovate",
    image="docker.io/renovate/renovate:latest",
    command=[
        "sh",
        "-lc",
        "cd /repo && renovate --platform=local --require-config=ignored --dry-run=full 2>&1 | tee /outputs/refurbish.log",
    ],
    env={"LOG_FORMAT": "json", "LOG_LEVEL": "debug"},
    inputs={
        "renovate": ToolInputs(source="default", destination="/repo/renovate.json5"),
        "dockerfile": ToolInputs(source="default", destination="/repo/Dockerfile"),
    },
    socket=False,
    outputs="/outputs/",
)

DEFAULT_CLI: dict[str, str] = {
    "lint": DEFAULT_HADOLINT_TOOL.id,
    "scan": DEFAULT_TRIVY_TOOL.id,
    "refurbish": DEFAULT_REFURBISH_TOOL.id,
}


def default_tools() -> list[Tool]:
    """Return fresh default runtime tools."""
    return [
        DEFAULT_HADOLINT_TOOL.model_copy(deep=True),
        DEFAULT_TRIVY_TOOL.model_copy(deep=True),
        DEFAULT_REFURBISH_TOOL.model_copy(deep=True),
    ]


def default_cli() -> dict[str, str]:
    """Return default CLI command-to-tool mappings."""
    return dict(DEFAULT_CLI)


def default_config() -> Config:
    """Return a fresh default runtime config model."""
    return Config(
        policy="default",
        conflicts="warn",
        tools=default_tools(),
        cli=default_cli(),
    )


DEFAULT_CONFIG: Config = default_config()


class Manifest(schema.Schema):
    """Runtime manifest implementation of the canonical schema."""

    config: Config

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    @classmethod
    def _from_payload(
        cls,
        payload: dict[str, Any],
        *,
        base_dir: Path | None = None,
    ) -> "Manifest":
        """Build runtime manifest from mapping payload with optional path normalization."""
        normalized = _normalize_relative_input_sources(payload, base=base_dir)
        return cls.model_validate(normalized)

    @classmethod
    def from_yaml(cls, path: Path | str) -> "Manifest":
        """Load a manifest from a YAML file."""
        manifest_path = Path(path).expanduser().resolve()
        with manifest_path.open("r", encoding="utf-8") as datafile:
            data = safe_load(datafile)
        if data is None:
            data = {}
        if not isinstance(data, dict):
            raise ValueError("Manifest must be a dictionary.")
        return cls._from_payload(cast(dict[str, Any], data), base_dir=manifest_path.parent)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Manifest":
        """Load a manifest from a dictionary."""
        if not isinstance(data, dict):
            raise ValueError("Manifest must be a dictionary.")
        return cls._from_payload(data)

    def save(self, path: Path = Path.cwd() / DEFAULT_LIBRARY_MANIFEST_FILENAME) -> None:
        """Save the runtime manifest to a YAML file with fully materialized defaults."""
        payload = self.model_dump(mode="json", exclude_defaults=False)
        with path.open("w", encoding="utf-8") as datafile:
            yaml_dump(payload, datafile, sort_keys=False)


__all__ = [
    "MANIFEST_FILENAME",
    "ToolInputs",
    "Tool",
    "Config",
    "Manifest",
    "DEFAULT_HADOLINT_TOOL",
    "DEFAULT_TRIVY_TOOL",
    "DEFAULT_REFURBISH_TOOL",
    "DEFAULT_CLI",
    "DEFAULT_CONFIG",
    "default_tools",
    "default_cli",
    "default_config",
]
