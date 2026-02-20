"""Packaged default input registry for generic tools."""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

from yaml import safe_load

from library import HADOLINT_CONFIG_PATH, RENOVATE_CONFIG_PATH, TRIVY_CONFIG_PATH
from library.schema import Tool

DEFAULT_INPUT_REGISTRY: dict[str, Path] = {
    "hadolint": HADOLINT_CONFIG_PATH,
    "trivy": TRIVY_CONFIG_PATH,
    "renovate": RENOVATE_CONFIG_PATH,
}


def _load_manifest_payload(path: Path) -> dict[str, Any]:
    """Load manifest YAML into a dictionary payload."""
    with path.open("r", encoding="utf-8") as handle:
        payload = safe_load(handle)
    if payload is None:
        payload = {}
    if not isinstance(payload, dict):
        raise ValueError("Manifest must be a dictionary.")
    return cast(dict[str, Any], payload)


def _resolve_manifest_dockerfile(path: Path) -> Path:
    """Resolve Dockerfile host path from manifest build context/file."""
    payload = _load_manifest_payload(path)
    build = payload.get("build")
    if not isinstance(build, dict):
        raise ValueError("Manifest build section is required.")

    context = build.get("context", ".")
    file_name = build.get("file", "Dockerfile")
    if not isinstance(context, str) or not isinstance(file_name, str):
        raise ValueError("Manifest build.context and build.file must be strings.")
    dockerfile = Path(file_name)
    if not dockerfile.is_absolute():
        dockerfile = path.parent / context / dockerfile
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
