"""Packaged default input registry for generic tools."""

from __future__ import annotations

from pathlib import Path

from library import HADOLINT_CONFIG_PATH, RENOVATE_CONFIG_PATH, TRIVY_CONFIG_PATH
from library.schema import Tool

DEFAULT_INPUT_REGISTRY: dict[str, Path] = {
    "hadolint": HADOLINT_CONFIG_PATH,
    "trivy": TRIVY_CONFIG_PATH,
    "renovate": RENOVATE_CONFIG_PATH,
}


def input(tool: Tool, input_key: str) -> Path:
    """Resolve packaged default input path for a tool input key."""
    if input_key not in tool.inputs:
        raise ValueError(f"Input key not defined for tool '{tool.id}': {input_key}")

    default_path = DEFAULT_INPUT_REGISTRY.get(tool.parser)
    if default_path is None:
        raise ValueError(
            f"No packaged default input available for parser '{tool.parser}'"
        )
    if not default_path.is_file():
        raise ValueError(f"Packaged default input not found: {default_path}")
    return default_path.resolve()
