"""
Pydantic models that describe the structure of Docker Official Image
`library/*` definitions. The intent is to emit JSON Schema from these
models so downstream users can author compatible build configuration
files programmatically.
"""

from __future__ import annotations

from enum import Enum
from typing import List, Optional, Any

from pydantic import AnyUrl, BaseModel, ConfigDict, Field, model_validator


class Architecture(str, Enum):
    """Container Architectures."""

    AMD64 = "amd64"
    ARM32V5 = "arm32v5"
    ARM32V6 = "arm32v6"
    ARM32V7 = "arm32v7"
    ARM64V8 = "arm64v8"
    WINDOWS_AMD64 = "windows-amd64"


class Builder(str, Enum):
    """Docker build backends."""

    BUILDKIT = "buildkit"
    CLASSIC = "classic"
    OCI_IMPORT = "oci-import"


class Maintainer(BaseModel):
    """Build Maintainer Information."""

    name: str = Field(..., description="Full name of the maintainer.")
    email: str = Field(
        ...,
        description="Contact email, required for traceability.",
    )
    github: Optional[str] = Field(
        None,
        description="Github handle without the leading '@'.",
    )
    gitlab: Optional[str] = Field(
        None,
        description="GitLab handle without the leading '@'.",
    )

    model_config = ConfigDict(extra="forbid")


class Git(BaseModel):
    """Git repository which contains build source."""

    repo: AnyUrl = Field(
        ..., description="Git repository which contains the Dockerfile."
    )
    fetch: str = Field(
        "refs/heads/main",
        description="Reference to fetch before resolving commits (e.g., refs/heads/main).",
        examples=["refs/heads/main", "refs/tags/v1.0.0"],
    )
    sha: Optional[str] = Field(
        None,
        description="Commit SHA to checkout for builds.",
    )
    tag: Optional[str] = Field(
        None,
        description="Tag to checkout for builds.",
    )

    @model_validator(mode="before")
    @classmethod
    def _sanitize_checkout(cls, data: Any) -> Any:
        """Check git config.

        Raises:
            ValueError: If neither sha nor tag is provided.
            ValueError: If both sha and tag are provided.

        Returns:
            Any: The sanitized data.
        """
        if data.get("sha") is None and data.get("tag") is None:
            raise ValueError("Either sha or tag must be provided.")
        if data.get("sha") is not None and data.get("tag") is not None:
            raise ValueError("Only one of sha or tag may be provided.")
        return data

    model_config = ConfigDict(extra="forbid")


class Build(BaseModel):
    """Build information."""

    path: str = Field(
        ".",
        description="Path to the directory containing the Dockerfile; defaults to the root of the repository.",
    )
    dockerfile: str = Field(
        "Dockerfile",
        description="Name of the Dockerfile relative to the path.",
        examples=["Dockerfile", "Dockerfile-alternate"],
    )
    context: str = Field(
        ".",
        description="Build context path relative to the Dockerfile.",
        examples=[".", "../"],
    )
    builder: str = Field(
        Builder.BUILDKIT,
        description="Builder backend used for this entry.",
        examples=[Builder.BUILDKIT, Builder.CLASSIC, Builder.OCI_IMPORT],
    )
    platforms: list[Architecture] = Field(
        default=[Architecture.AMD64],
        description="Set target platforms for the build.",
    )
    tags: List[str] = Field(..., description="Tags produced by this build entry.")
    args: Optional[dict[str, str]] = Field(
        None,
        description="Set build-time variables for the build.",
    )
    annotations: Optional[dict[str, str]] = Field(
        None,
        description="Add annotation to the container image.",
    )
    labels: Optional[dict[str, str]] = Field(
        None,
        description="Add metadata to the container image.",
    )
    target: Optional[str] = Field(
        None,
        description="Set the target build stage to build.",
    )

    model_config = ConfigDict(extra="forbid")


class Metadata(BaseModel):
    """
    Metadata for the image.
    """

    identifier: str = Field(..., description="Unique science identifier for the image.")
    project: str = Field(..., description="SRCnet Project name for the image.")


class Manifest(BaseModel):
    """
    Manifest information.
    """

    version: float = Field(0.1, description="CANFAR Library manifest version.")
    maintainers: List[Maintainer] = Field(
        ..., description="List of maintainers responsible for the image."
    )
    git: Git = Field(..., description="Git repository information.")
    build: Build = Field(..., description="Build information for the image.")
    metadata: Metadata = Field(..., description="Metadata for the image.")


if __name__ == "__main__":
    # Emit the JSON Schema that downstream tools can consume.
    import json

    print(json.dumps(Manifest.model_json_schema(), indent=2))
