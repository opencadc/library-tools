"""JSON Schema for CANFAR Library Tools manifest files."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re
import shlex
from typing import Any, Literal, cast

from yaml import safe_load
from pydantic import (
    AnyUrl,
    BaseModel,
    ConfigDict,
    Field,
    FilePath,
    field_validator,
    model_validator,
)

ALLOWED_REGISTRY_HOSTS = {"images.canfar.net"}
DISCOVERY_KINDS = ("notebook", "headless", "carta", "firefly", "contributed")
TOOL_TOKEN_PATTERN = re.compile(r"{{\s*([a-zA-Z0-9_.-]+)\s*}}")


class Maintainer(BaseModel):
    """Details about the maintainer of the image."""

    name: str = Field(..., title="Name", description="Name of the maintainer.")
    email: str = Field(..., title="Email", description="Contact email.")
    github: str | None = Field(
        None, title="GitHub Username", description="GitHub Username."
    )
    gitlab: str | None = Field(
        None, title="GitLab Username", description="GitLab Username."
    )

    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class Registry(BaseModel):
    """Details about the container registry."""

    host: str = Field(
        "images.canfar.net",
        title="Hostname",
        description="Container registry hostname.",
        examples=["images.canfar.net"],
    )
    project: str = Field(
        ...,
        title="Project",
        description="Container registry project.",
        examples=["skaha"],
    )
    image: str = Field(
        ...,
        title="Image Name",
        description="Container image name.",
        examples=["python", "base"],
    )

    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class Git(BaseModel):
    """Repository information for the image build source."""

    repo: AnyUrl = Field(
        ...,
        title="Repository",
        description="Git repository.",
        examples=["https://github.com/opencadc/canfar-library"],
    )
    fetch: str = Field(
        "refs/heads/main",
        title="Git Fetch Reference",
        description="Git fetch reference.",
        examples=["refs/heads/main", "refs/heads/develop"],
    )
    commit: str = Field(
        ...,
        title="SHA Commit Hash",
        description="SHA commit hash to build.",
        examples=["1234567890123456789012345678901234567890"],
    )

    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class Build(BaseModel):
    """Configuration for building the container image."""

    context: str = Field(
        ".",
        title="Build Context",
        description="Path to the build context directory.",
        examples=[".", "images/python"],
    )
    file: str = Field(
        "Dockerfile",
        title="Dockerfile",
        description="Name of the Dockerfile in the build context.",
        examples=["Dockerfile", "Dockerfile.runtime"],
    )
    platforms: list[str] = Field(
        default=["linux/amd64"],
        title="Platforms",
        description="Target platforms for the build.",
        examples=[["linux/amd64"], ["linux/amd64", "linux/arm64"]],
    )
    tags: list[str] = Field(
        ...,
        title="Tags",
        description="Image tags to apply.",
        examples=[["latest"], ["1.0.0", "latest"]],
        min_length=1,
    )
    output: str = Field(
        "type=docker",
        title="Output",
        description="Output destination (type=docker by default).",
        examples=["type=docker", "type=registry", "type=local,dest=./out"],
    )
    options: str = Field(
        "",
        title="Options",
        description="Additional buildx options appended to the build command.",
        examples=["--target=runtime --push"],
    )

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    def command(self) -> list[str]:
        """Build the docker buildx command for this build."""
        cmd = ["docker", "buildx", "build"]
        dockerfile_path = Path(self.file)
        if not dockerfile_path.is_absolute():
            dockerfile_path = Path(self.context) / dockerfile_path
        cmd.extend(["--file", str(dockerfile_path)])
        for tag in self.tags:
            cmd.extend(["--tag", tag])
        for platform in self.platforms:
            cmd.extend(["--platform", platform])
        cmd.extend(["--output", self.output])
        if self.options:
            cmd.extend(shlex.split(self.options))
        cmd.append(self.context)
        return cmd


class Discovery(BaseModel):
    """Discovery metadata mapped to OCI labels/annotations."""

    title: str = Field(..., description="Human-readable title of the image.")
    description: str = Field(
        ...,
        description="Human-readable description of the software packaged in the image.",
    )
    source: AnyUrl = Field(
        ..., description="URL to get source code for building the image"
    )
    url: AnyUrl = Field(..., description="URL to find more information on the image.")
    documentation: AnyUrl = Field(
        ..., description="URL to get documentation on the image"
    )
    version: str = Field(..., description="Version of the packaged software.")
    revision: str = Field(
        ...,
        description="Source control revision identifier for the packaged software. For example a git commit SHA.",
    )
    created: datetime = Field(
        ..., description="Datetime on which the image was built. Conforming to RFC 3339"
    )
    authors: str = Field(
        ...,
        description="Details of the people or organization responsible for the image",
    )
    licenses: str = Field(
        ...,
        description="License(s) under which contained software is distributed as an SPDX License Expression.",
    )
    keywords: list[str] = Field(
        default_factory=list,
        description="Keywords used to support software discovery and search.",
        examples=["astronomy", "analysis", "python"],
    )
    domain: list[str] = Field(
        ...,
        min_length=1,
        description="Scientific domains supported by this image.",
        examples=[["astronomy"], ["astronomy", "scientific-computing"]],
    )
    kind: list[Literal["notebook", "headless", "carta", "firefly", "contributed"]] = (
        Field(
            ...,
            min_length=1,
            description="Discovery kinds that classify this image.",
            examples=[["headless"], ["notebook", "headless"]],
        )
    )
    tools: list[str] = Field(
        default_factory=list,
        description="Common tools included in the image.",
        examples=["python", "jupyterlab", "astropy"],
    )
    deprecated: bool = Field(
        False,
        description="Whether this image is deprecated and should no longer be used.",
    )

    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class Metadata(BaseModel):
    """Metadata for the image."""

    discovery: Discovery = Field(
        ..., title="Discovery", description="Canonical discovery metadata."
    )

    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class ToolInputs(BaseModel):
    """Named tool inputs resolved by CLI into deterministic mounts."""

    source: Literal["default"] | FilePath = Field(
        "default",
        title="Source",
        description=(
            "Input source for the tool. 'default' maps to built-in config shipped "
            "with the library; otherwise provide a local file path."
        ),
        examples=["default", "./ci/.trivy.yaml"],
    )
    destination: str = Field(
        "/config.yaml",
        title="Destination",
        description="Absolute path in the tool container where the input is mounted.",
        examples=["/config.yaml", "/workspace/config/trivy.yaml"],
    )

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    @field_validator("destination")
    @classmethod
    def validate_destination_path(cls, value: str) -> str:
        """Ensure destination is an absolute path in the container."""
        if not value.startswith("/"):
            raise ValueError(
                "Tool input destination must be an absolute container path."
            )
        return value


class Tool(BaseModel):
    """Definition of a Library Tool."""

    id: str = Field(
        ...,
        title="ID",
        description="Unique tool identifier.",
        pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]*$",
        examples=["default-scanner", "srcnet-scanner"],
    )
    parser: Literal["hadolint", "trivy", "renovate", "curate", "provenance", "push"] = (
        Field(
            ...,
            title="Parser",
            description="Built-in parser used to consume the tool JSON outputs.",
            examples=["trivy", "hadolint"],
        )
    )
    image: str = Field(
        ...,
        title="Image",
        description="Container image to run the tool in.",
        examples=["docker.io/aquasec/trivy:latest"],
    )
    command: list[str] = Field(
        ...,
        min_length=1,
        title="Command",
        description=(
            "Tokenized command argv executed in the tool container. "
            "Supported tokens: {{inputs.<key>}} and {{image.reference}}."
        ),
        examples=[
            [
                "trivy",
                "image",
                "--config",
                "{{inputs.trivy}}",
                "--format",
                "json",
                "--output",
                "/outputs/report.json",
                "{{image.reference}}",
            ]
        ],
    )
    env: dict[str, str] = Field(
        default_factory=dict,
        title="Environment",
        description="Environment variables passed to the tool container.",
    )
    inputs: dict[str, ToolInputs] = Field(
        default_factory=dict,
        title="Inputs",
        description="Tool inputs mounted into the tool container.",
    )
    socket: bool = Field(
        False,
        title="Docker Socket",
        description="Whether /var/run/docker.sock is mounted into the tool container.",
    )
    outputs: Literal["/outputs/"] = Field(
        "/outputs/",
        title="Outputs",
        description=("Fixed container directory where tools must write outputs."),
        examples=["/outputs/"],
    )

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


class Config(BaseModel):
    """Configuration for Library Tools execution and CLI wiring."""

    policy: Literal["default", "strict", "expert"] = Field(
        "default",
        description="Policy profile for tooling behavior.",
    )
    conflicts: Literal["warn", "strict"] = Field(
        "warn",
        description="Conflict handling mode for tooling behavior.",
    )
    tools: list[Tool] = Field(
        ...,
        description="Tool definitions available to CLI steps.",
    )
    cli: dict[str, str] = Field(
        ...,
        description="CLI step name to tool id mapping.",
        examples=[{"scan": "default-scanner", "lint": "default-linter"}],
    )

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    @model_validator(mode="after")
    def validate_cli_mappings(self) -> "Config":
        """Validate tool id uniqueness and CLI mapping targets."""
        tool_ids = [tool.id for tool in self.tools]
        unique_ids = set(tool_ids)
        if len(unique_ids) != len(tool_ids):
            raise ValueError("Tool ids must be unique in config.tools.")
        unknown_targets = {
            command: tool_id
            for command, tool_id in self.cli.items()
            if tool_id not in unique_ids
        }
        if unknown_targets:
            missing = ", ".join(
                f"{command}->{tool_id}"
                for command, tool_id in sorted(unknown_targets.items())
            )
            raise ValueError(f"CLI mappings reference unknown tool ids: {missing}")
        return self


class Manifest(BaseModel):
    """CANFAR Library Tools Schema."""

    version: Literal[1] = Field(..., description="Library manifest schema version.")
    registry: Registry = Field(..., title="Registry", description="Image registry.")
    maintainers: list[Maintainer] = Field(
        ...,
        title="Maintainers",
        description="Image maintainers.",
    )
    git: Git = Field(..., title="Git Info", description="Image repository.")
    build: Build = Field(..., title="Build Info", description="Image build info.")
    metadata: Metadata = Field(..., title="Metadata", description="Image metadata.")
    config: Config = Field(..., title="Config", description="Tool configuration.")

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        populate_by_name=True,
        json_schema_extra={
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": "https://raw.githubusercontent.com/opencadc/canfar-library/main/.spec.json",
            "title": "CANFAR Library Tools Schema",
            "description": "Schema to capture build intent, discovery metadata, and tool configuration.",
        },
    )

    @classmethod
    def from_yaml(cls, path: Path | str) -> "Manifest":
        """Load a manifest from a YAML file.

        Args:
            path: Path to the manifest YAML file.

        Returns:
            Manifest model instance.
        """
        if isinstance(path, str):
            path = Path(path)
        with path.open("r", encoding="utf-8") as datafile:
            data = safe_load(datafile)
        if data is None:
            data = {}
        if not isinstance(data, dict):
            raise ValueError("Manifest must be a dictionary.")
        return cls(**cast(dict[str, Any], data))

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Manifest":
        """Load a manifest from a dictionary.

        Args:
            data: Manifest data as a dictionary.

        Returns:
            Manifest model instance.
        """
        return cls(**data)


if __name__ == "__main__":
    # Emit the JSON Schema that downstream tools can consume.
    import json

    print(json.dumps(Manifest.model_json_schema(), indent=2))
