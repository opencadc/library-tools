"""JSON Schema for CANFAR Library manifest files."""

from __future__ import annotations

from typing import List, Optional, Literal

from pydantic import AnyUrl, BaseModel, ConfigDict, Field


Platform = Literal[
    "linux/amd64",
    "linux/arm64",
    "linux/arm/v7",
    "linux/arm/v6",
    "linux/arm/v5",
    "windows/amd64",
]


class Maintainer(BaseModel):
    """Build Maintainer Information."""

    name: str = Field(..., title="Name", description="Full name of the maintainer.")
    email: str = Field(
        ...,
        title="Email",
        description="Contact email, required for traceability.",
    )
    github: Optional[str] = Field(
        None,
        title="Maintainer Github",
        description="Optional Github Username.",
    )
    gitlab: Optional[str] = Field(
        None,
        title="Maintainer Gitlab",
        description="Optional Gitlab Username.",
    )

    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class Git(BaseModel):
    """Git repository which contains build source."""

    repo: AnyUrl = Field(
        ...,
        title="Repository",
        description="Git repository which contains the build source.",
    )
    tag: str = Field(
        ...,
        title="Git Tag Reference",
        description="Tag reference to checkout for build.",
        examples=["refs/tags/v1.0.0", "v1.0.0"],
    )
    sha: Optional[str] = Field(
        None,
        title="Commit SHA for the Git Tag Reference",
        description="Optional commit SHA for the Git Tag Reference."
        "If provided, the build will fail if the SHA does not match the tag reference."
        "If not provided, the SHA is looked up from the tag reference.",
    )

    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class Build(BaseModel):
    """Build information."""

    path: str = Field(
        ".",
        title="Path",
        description="Path to the directory containing the Dockerfile; defaults to the root of the repository.",
    )
    dockerfile: str = Field(
        "Dockerfile",
        title="Dockerfile",
        description="Name of the Dockerfile relative to the path.",
        examples=["Dockerfile", "Dockerfile-alternate"],
    )
    context: str = Field(
        ".",
        title="Build Context",
        description="Build context path relative to the Dockerfile.",
        examples=[".", "../"],
    )
    builder: str = Field(
        "buildkit",
        title="Build Backend",
        description="Builder backend used for this entry.",
        examples=["buildkit"],
    )
    platforms: list[Platform] = Field(
        default=["linux/amd64"],
        title="Target Platforms",
        description="Set target platforms for build.",
        examples=[["linux/amd64"], ["linux/amd64", "linux/arm64"]],
    )
    tags: List[str] = Field(
        ...,
        title="Container Image Tags",
        description="Tags produced by this build entry.",
        examples=["latest", "1.0.0"],
    )
    args: Optional[dict[str, str]] = Field(
        None,
        title="Build Args",
        description="Set build-time variables for the build.",
        examples=[{"FOO": "bar"}],
    )
    annotations: Optional[dict[str, str]] = Field(
        None,
        title="Image Annotations",
        description="Add annotation to the container image.",
        examples=[{"canfar.image.type": "base"}],
    )
    labels: Optional[dict[str, str]] = Field(
        None,
        title="Image Labels",
        description="Add metadata to the container image.",
        examples=[
            {
                "org.opencontainers.image.title": "CANFAR Base Image",
                "org.opencontainers.image.description": "Base image for CANFAR Science Platform",
            }
        ],
    )
    target: Optional[str] = Field(
        None,
        title="Build Target",
        description="Set the target build stage to build.",
        examples=["runtime"],
    )

    test: Optional[Run] = Field(
        None,
        title="Image Test Command",
        description="Command to run in the created container to verify the image is working.",
    )

    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class Metadata(BaseModel):
    """
    Metadata for the image.
    """

    identifier: str = Field(..., description="Unique science identifier for the image.")
    project: str = Field(..., description="SRCnet Project name for the image.")


class Run(BaseModel):
    """Test information for the image."""

    cmd: Optional[str] = Field(
        None,
        title="Testing Command",
        description="Command to run in the created container to verify the image is working."
        " The command is run with `docker run --rm -it <image> <cmd>`, where image is populated automatically from the build process."
        " If the command returns a non-zero exit code, the test is considered to have failed.",
        examples=["bash -c 'echo hello world'"],
    )


class Manifest(BaseModel):
    """
    Manifest information.
    """

    name: str = Field(..., description="Name of the image.", examples=["astroml"])
    maintainers: List[Maintainer] = Field(
        ...,
        title="Maintainers",
        description="List of maintainers responsible for the image.",
    )
    git: Git = Field(
        ..., title="Git Info", description="Repository information for the image."
    )
    build: Build = Field(
        ..., title="Build Info", description="Build information for the image."
    )
    metadata: Metadata = Field(
        ..., title="Metadata", description="Metadata for the image."
    )

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        json_schema_extra={
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": "https://raw.githubusercontent.com/opencadc/canfar-library/main/.spec.json",
            "title": "CANFAR Library Manifest",
            "description": "Schema to capture ownership, build source, intent, and identity for library artifacts.",
        },
    )


if __name__ == "__main__":
    # Emit the JSON Schema that downstream tools can consume.
    import json

    print(json.dumps(Manifest.model_json_schema(), indent=2))
