"""Packaged default input registry for generic tools."""

from __future__ import annotations

from pathlib import Path

from library import HADOLINT_CONFIG_PATH, RENOVATE_CONFIG_PATH, TRIVY_CONFIG_PATH
from library import schema
from library.schema import Tool, ToolInputs

DEFAULT_INPUT_REGISTRY: dict[str, Path] = {
    "hadolint": HADOLINT_CONFIG_PATH,
    "trivy": TRIVY_CONFIG_PATH,
    "renovate": RENOVATE_CONFIG_PATH,
}

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


def default_config() -> schema.Config:
    """Return a fresh default runtime config model."""
    return schema.Config(
        policy="default",
        conflicts="warn",
        tools=default_tools(),
        cli=default_cli(),
    )


DEFAULT_CONFIG: schema.Config = default_config()


def _resolve_manifest_dockerfile(path: Path) -> Path:
    """Resolve Dockerfile host path from manifest build context/file."""
    manifest = schema.Schema.from_yaml(path)
    dockerfile = Path(manifest.build.file)
    if not dockerfile.is_absolute():
        dockerfile = path.parent / manifest.build.context / dockerfile
    dockerfile = dockerfile.resolve()
    if not dockerfile.is_file():
        raise ValueError(f"Dockerfile from manifest does not exist: {dockerfile}")
    return dockerfile


def input(tool: Tool, input_key: str, manifest: Path) -> Path:
    """Resolve packaged default input path for a tool input key."""
    if input_key not in tool.inputs:
        raise ValueError(f"Input key not defined for tool '{tool.id}': {input_key}")

    if input_key == "dockerfile":
        return _resolve_manifest_dockerfile(manifest)

    default_path = DEFAULT_INPUT_REGISTRY.get(input_key)
    if default_path is None:
        default_path = DEFAULT_INPUT_REGISTRY.get(tool.parser)
    if default_path is None:
        raise ValueError(
            f"No packaged default input available for parser '{tool.parser}'"
        )
    if not default_path.is_file():
        raise ValueError(f"Packaged default input not found: {default_path}")
    return default_path.resolve()
