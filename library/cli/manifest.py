"""Shared manifest discovery and resolution helpers for CLI commands."""

from __future__ import annotations

from pathlib import Path

from library import default


def discover(cwd: Path | None = None) -> Path | None:
    """Discover a manifest file in the given directory."""
    root = (cwd or Path.cwd()).resolve()
    candidates = [default.MANIFEST_FILENAME, ".library.manifest.yml"]
    for filename in candidates:
        candidate = root / filename
        if candidate.is_file():
            return candidate
    return None


def resolve(path: Path | None, *, required: bool) -> Path | None:
    """Resolve an explicit manifest path or discover one from current directory."""
    if path is not None:
        resolved = path.expanduser().resolve()
        if not resolved.is_file():
            raise ValueError(f"Manifest file not found: {resolved}")
        return resolved

    discovered = discover()
    if discovered is not None:
        return discovered
    if required:
        raise ValueError(
            "No manifest provided and no default manifest found. "
            f"Expected ./{default.MANIFEST_FILENAME}"
        )
    return None
