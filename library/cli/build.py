"""Build CLI helpers."""

from __future__ import annotations

from pathlib import Path
import shlex
import subprocess

from library import schema
from library.utils.console import console


_OVERLAP_FLAGS = {
    "--file",
    "-f",
    "--tag",
    "-t",
    "--platform",
    "--label",
    "--annotation",
    "--output",
    "-o",
}

_OVERLAP_PREFIXES = (
    "--file=",
    "--tag=",
    "--platform=",
    "--label=",
    "--annotation=",
    "--output=",
)


def _find_overlap(tokens: list[str]) -> str | None:
    for token in tokens:
        if token in _OVERLAP_FLAGS:
            return token
        if token.startswith(_OVERLAP_PREFIXES):
            return token.split("=", 1)[0]
    return None


def _append_options(existing: str, extra: list[str]) -> str:
    if not extra:
        return existing
    extra_str = " ".join(shlex.quote(arg) for arg in extra)
    if not existing:
        return extra_str
    return f"{existing} {extra_str}"


def _resolve_build_tags(manifest: schema.Schema) -> list[str]:
    """Resolve plain manifest tags into fully qualified image references."""
    prefix = (
        f"{manifest.registry.host}/"
        f"{manifest.registry.project}/"
        f"{manifest.registry.image}"
    )
    resolved: list[str] = []
    for tag in manifest.build.tags:
        # Preserve explicit image references for backward compatibility.
        if any(marker in tag for marker in ("/", ":", "@")):
            resolved.append(tag)
            continue
        resolved.append(f"{prefix}:{tag}")
    return resolved


def run_build(manifest_path: Path, extra_args: list[str]) -> int:
    """Run docker buildx build using the manifest defaults.

    Args:
        manifest_path: Path to the manifest file.
        extra_args: Additional buildx options to append.

    Returns:
        Exit code from the buildx command.
    """
    manifest = schema.Schema.from_yaml(manifest_path)
    options_tokens = (
        shlex.split(manifest.build.options) if manifest.build.options else []
    )
    overlap = _find_overlap(options_tokens + extra_args)
    if overlap:
        console.print(f"[red]❌ build options cannot include {overlap}.[/red]")
        return 2

    manifest.build.tags = _resolve_build_tags(manifest)
    manifest.build.options = _append_options(manifest.build.options, extra_args)
    result = subprocess.run(manifest.build.command(), check=False)
    return result.returncode
