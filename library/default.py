"""Default tool definitions shipped with the library."""

from __future__ import annotations

from library.schema import Tool, ToolInputs

MANIFEST_FILENAME = ".library.manifest.yaml"

HadolintTool = Tool(
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
    inputs={
        "hadolint": ToolInputs(source="default", destination="/inputs/.hadolint.yaml"),
        "dockerfile": ToolInputs(source="default", destination="/inputs/Dockerfile"),
    },
    socket=False,
    outputs="/outputs/",
)

HadolintCli: dict[str, str] = {"lint": HadolintTool.id}

__all__ = ["MANIFEST_FILENAME", "HadolintTool", "HadolintCli"]
