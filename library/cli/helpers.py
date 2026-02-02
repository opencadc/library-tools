"""CLI helper utilities."""

from __future__ import annotations

from pathlib import Path

from library import schema
from library.utils.console import console


def read_dockerfile(dockerfile_path: Path) -> str:
    """Read Dockerfile contents from disk.

    Args:
        dockerfile_path: Path to a local Dockerfile.

    Returns:
        Dockerfile contents as text.
    """
    console.print(f"[cyan]Reading Dockerfile: {dockerfile_path}[/cyan]")
    return dockerfile_path.read_text(encoding="utf-8")


def load_manifest(manifest_path: Path) -> schema.Manifest:
    """Load and validate a manifest file.

    Args:
        manifest_path: Path to the manifest file.

    Returns:
        Manifest model instance.
    """
    console.print(f"[cyan]Reading Manifest: {manifest_path}[/cyan]")
    return schema.Manifest.from_yaml(manifest_path)


def resolve_dockerfile_contents(
    manifest_path: Path | None, dockerfile_path: Path | None
) -> str:
    """Resolve Dockerfile contents from a manifest or local path.

    Args:
        manifest_path: Path to the manifest file.
        dockerfile_path: Path to a local Dockerfile.

    Returns:
        Dockerfile contents as text.

    Raises:
        ValueError: If neither a manifest nor Dockerfile path is provided.
    """
    if dockerfile_path is not None:
        return read_dockerfile(dockerfile_path)
    if manifest_path is None:
        raise ValueError("Either manifest_path or dockerfile_path must be provided")

    manifest_model = load_manifest(manifest_path)
    dockerfile_contents = manifest_model.dockerfile()
    console.print("[cyan]Resolved Dockerfile Contents:[/cyan]")
    console.print(f"\n{dockerfile_contents}\n")
    return dockerfile_contents
