"""Packaged default input registry for generic tools."""

from __future__ import annotations

from pathlib import Path

from library import HADOLINT_CONFIG_PATH, RENOVATE_CONFIG_PATH, TRIVY_CONFIG_PATH
from library import manifest as runtime_manifest
from library.schema import Tool

DEFAULT_INPUT_REGISTRY: dict[str, Path] = {
    "hadolint": HADOLINT_CONFIG_PATH,
    "trivy": TRIVY_CONFIG_PATH,
    "renovate": RENOVATE_CONFIG_PATH,
}


def _resolve_manifest_dockerfile(path: Path) -> Path:
    """Resolve Dockerfile host path from manifest build context/file."""
    manifest = runtime_manifest.Manifest.from_yaml(path)
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
