"""Canonical JSON schema contract for CANFAR Library manifest files."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import shlex
from typing import Literal

from pydantic import AnyUrl, BaseModel, ConfigDict, Field, FilePath


class Author(BaseModel):
    """Details about an author of the image."""

    name: str = Field(
        ...,
        title="Name",
        description="Name of the author.",
        examples=["John Doe"],
    )
    email: str = Field(
        ...,
        title="Email",
        description="Contact email address for the author.",
        examples=["john.doe@example.com"],
    )
    role: str = Field(
        "maintainer",
        title="Role",
        description="Role of the author.",
        examples=["maintainer", "contributor", "researcher", "developer"],
    )
    github: str | None = Field(
        None,
        title="GitHub Username",
        description="GitHub Username.",
        examples=["johndoe"],
    )
    gitlab: str | None = Field(
        None,
        title="GitLab Username",
        description="GitLab Username.",
        examples=["johndoe"],
    )
    orcid: str | None = Field(
        None,
        title="ORCID",
        description="Open Researcher and Contributor ID.",
        examples=["0000-0002-1825-0097"],
    )
    affiliation: str | None = Field(
        None,
        title="Affiliation",
        description="Affiliation of the author.",
        examples=["Oxford University"],
    )

    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class Registry(BaseModel):
    """Details about the container registry."""

    host: str = Field(
        ...,
        title="Hostname",
        description="Container registry hostname.",
        examples=["images.canfar.net", "docker.io"],
    )
    project: str = Field(
        ...,
        title="Project",
        description="Container registry project/namespace.",
        examples=["skaha", "chimefrb"],
    )
    image: str = Field(
        ...,
        title="Image Name",
        description="Container image name.",
        examples=["python", "baseband-analysis"],
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
        dockerfile = Path(self.file)
        if not dockerfile.is_absolute():
            dockerfile = Path(self.context) / dockerfile
        cmd.extend(["--file", str(dockerfile)])
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

    title: str = Field(
        ...,
        title="Title",
        description="Human-readable title of the image.",
        examples=["Baseband Analysis"],
    )
    description: str = Field(
        ...,
        title="Description",
        description="Human-readable description of the software packaged in the image.",
        examples=["Baseband analysis tools for radio astronomy."],
        min_length=1,
        max_length=255,
    )
    source: AnyUrl = Field(
        ...,
        title="Source",
        description="URL to get source code for building the image.",
        examples=["https://github.com/example/repo"],
    )
    url: AnyUrl | None = Field(
        None,
        title="URL",
        description="URL to find more information on the image.",
        examples=["https://example.com/baseband-analysis"],
    )
    documentation: AnyUrl | None = Field(
        None,
        title="Documentation",
        description="URL to get documentation on the image.",
        examples=["https://example.com/baseband-analysis/docs"],
    )
    version: str = Field(
        ...,
        title="Version",
        description="Version of the packaged software.",
        examples=["v1.2.3"],
    )
    revision: str = Field(
        "unknown",
        title="Source Control Revision Checksum",
        description="Automatically computed from git when building from source.",
        examples=["1234567890123456789012345678901234567890"],
    )
    created: datetime = Field(
        ...,
        title="Created Timestamp",
        description="Datetime when metadata was processed.",
        examples=["2026-02-05T12:00:00Z"],
    )
    authors: list[Author] = Field(
        ...,
        title="Authors",
        description="Details of the people or organization responsible for the image",
        examples=[{"name": "John Doe", "email": "john.doe@example.com"}],
    )
    licenses: str = Field(
        ...,
        title="Licenses",
        description="License(s) for software, as an SPDX License Expression.",
        examples=["AGPL-3.0", "AGPL-3.0-only", "MIT OR Apache-2.0"],
    )
    keywords: list[str] = Field(
        ...,
        description="Keywords used to support software discovery and search.",
        examples=["polarization", "radio-astronomy", "calibration"],
    )
    domain: list[str] = Field(
        ["astronomy"],
        min_length=1,
        description="Scientific domains supported by this image.",
        examples=[["astronomy"], ["astronomy", "scientific-computing"]],
    )
    kind: list[
        Literal["notebook", "headless", "carta", "firefly", "contributed", "desktop"]
    ] = Field(
        ...,
        min_length=1,
        description="Classification of the software in the image.",
        examples=[["headless"], ["notebook", "headless"]],
    )
    tools: list[str] = Field(
        ...,
        description="Scientific Software packages included in the image.",
        examples=["python", "jupyterlab", "astropy", "pyuvdata", "wsclean"],
    )
    deprecated: bool = Field(
        False,
        title="Deprecated",
        description="Whether this image is deprecated and should no longer be used.",
        examples=[False, True],
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
        examples=["default", "./.trivy.yaml"],
    )
    destination: str = Field(
        "/config.yaml",
        title="Destination",
        description="Absolute path in the tool container where the input is mounted.",
        examples=["/config.yaml", "/workspace/config/trivy.yaml"],
    )

    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class Tool(BaseModel):
    """Definition of a Library Tool."""

    id: str = Field(
        ...,
        title="Tool ID",
        description="Unique tool identifier.",
        pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]*$",
        examples=["default-scanner", "srcnet-scanner"],
    )
    parser: Literal["hadolint", "trivy", "renovate", "curate", "provenance", "push"] = (
        Field(
            ...,
            title="Parser",
            description="Built-in parser used to consume the tool outputs.",
            examples=["trivy", "hadolint"],
        )
    )
    image: str = Field(
        ...,
        title="Tool Image",
        description="Container image used to run the tool.",
        examples=["docker.io/aquasec/trivy:latest"],
    )
    command: list[str] = Field(
        ...,
        min_length=1,
        title="Command",
        description=(
            "Tokenized command executed in the tool container."
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
        {},
        title="Tool Environment",
        description="Environment variables passed to the tool container.",
        examples=[{"TRIVY_DEBUG": "true"}],
    )
    inputs: dict[str, ToolInputs] = Field(
        ...,
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
        title="Tool Outputs Path",
        description=("Fixed container directory where tools must write outputs."),
        examples=["/outputs/"],
    )

    model_config = ConfigDict(extra="forbid", validate_assignment=True)


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


class Schema(BaseModel):
    """Canonical Library manifest schema contract."""

    version: Literal[1] = Field(1, description="Library manifest schema version.")
    registry: Registry = Field(..., title="Registry", description="Image registry.")
    build: Build = Field(..., title="Build Info", description="Image build info.")
    metadata: Metadata = Field(..., title="Metadata", description="Image metadata.")
    config: Config = Field(..., title="Config", description="Tool configuration.")

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        populate_by_name=True,
        json_schema_serialization_defaults_required=True,
        json_schema_extra={
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": "https://raw.githubusercontent.com/opencadc/library-tools/main/.spec.json",
            "title": "CANFAR Library Tools Schema",
            "description": ("Canonical schema for Library Tools manifest files."),
        },
    )


if __name__ == "__main__":
    import json

    print(json.dumps(Schema.model_json_schema(), indent=2))
