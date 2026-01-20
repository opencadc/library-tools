"""Manifest loading and validation helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from library.schema import Manifest


def read(path: Path) -> dict[str, Any]:
    """Read a manifest file.

    Args:
        path: Path to the manifest YAML file.

    Returns:
        Parsed manifest data.

    Raises:
        ValueError: If the manifest content is not a mapping.
    """
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError("Manifest must be a mapping")
    return data


def validate(data: dict[str, Any]) -> None:
    """Validate a manifest against the schema.

    Args:
        data: Manifest data to validate.

    Raises:
        ValidationError: If the manifest is invalid.
    """
    Manifest.model_validate(data)
