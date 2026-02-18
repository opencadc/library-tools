"""Hadolint CLI helpers."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import tempfile
from typing import Any

from yaml import safe_dump, safe_load

from library import default
from library.parsers import hadolint as hadolint_parser
from library.tools import ToolRunContext, run as run_tool
from library.utils import docker
from library.utils.console import console

HADOLINT_IMAGE = "docker.io/hadolint/hadolint:latest"
HADOLINT_COMMAND = "lint"


def _discover_manifest() -> Path:
    """Discover the default manifest from the current working directory."""
    cwd = Path.cwd()
    candidates = [default.MANIFEST_FILENAME, ".library.manifest.yml"]
    for filename in candidates:
        candidate = cwd / filename
        if candidate.is_file():
            return candidate.resolve()
    raise ValueError(
        "No manifest provided and no default manifest found. "
        "Expected ./.library.manifest.yaml"
    )


def _resolve_manifest_path(manifest_path: Path | None) -> Path:
    """Resolve explicit or discovered manifest path."""
    if manifest_path is None:
        return _discover_manifest()
    resolved = manifest_path.expanduser().resolve()
    if not resolved.is_file():
        raise ValueError(f"Manifest file not found: {resolved}")
    return resolved


def _load_manifest_data(manifest_path: Path) -> dict[str, Any]:
    """Load manifest YAML as a dictionary."""
    with manifest_path.open("r", encoding="utf-8") as handle:
        payload = safe_load(handle)
    if payload is None:
        payload = {}
    if not isinstance(payload, dict):
        raise ValueError("Manifest must be a dictionary.")
    return payload


def _resolve_dockerfile(manifest_path: Path) -> Path:
    """Resolve Dockerfile path from manifest build section."""
    data = _load_manifest_data(manifest_path)
    build = data.get("build")
    if not isinstance(build, dict):
        raise ValueError("Manifest build section is required for hadolint.")

    context = build.get("context", ".")
    file_name = build.get("file", "Dockerfile")
    if not isinstance(context, str) or not isinstance(file_name, str):
        raise ValueError("Manifest build.context and build.file must be strings.")

    dockerfile = Path(file_name)
    if not dockerfile.is_absolute():
        dockerfile = manifest_path.parent / context / dockerfile
    dockerfile = dockerfile.resolve()
    if not dockerfile.is_file():
        raise ValueError(f"Dockerfile from manifest does not exist: {dockerfile}")
    return dockerfile


def _runtime_manifest(dockerfile: Path) -> dict[str, object]:
    """Build runtime manifest using shipped hadolint defaults."""
    tool = default.HadolintTool.model_copy(deep=True)
    tool.inputs["dockerfile"].source = str(dockerfile)
    return {
        "version": 1,
        "registry": {
            "host": "images.canfar.net",
            "project": "library",
            "image": "hadolint-local",
        },
        "maintainers": [
            {"name": "Library Tooling", "email": "tooling@example.com"},
        ],
        "git": {
            "repo": "https://github.com/opencadc/canfar-library",
            "commit": "1234567890123456789012345678901234567890",
        },
        "build": {"context": ".", "file": "Dockerfile", "tags": ["local"]},
        "metadata": {
            "discovery": {
                "title": "Hadolint Local",
                "description": "Generated manifest for hadolint local execution.",
                "source": "https://github.com/opencadc/canfar-library",
                "url": "https://images.canfar.net/library/hadolint-local",
                "documentation": "https://canfar.net/docs/user-guide",
                "version": "1.0.0",
                "revision": "1234567890123456789012345678901234567890",
                "created": "2026-02-18T00:00:00Z",
                "authors": "Library Tooling",
                "licenses": "MIT",
                "domain": ["astronomy"],
                "kind": ["headless"],
            }
        },
        "config": {
            "policy": "default",
            "conflicts": "warn",
            "tools": [tool.model_dump(mode="json")],
            "cli": dict(default.HadolintCli),
        },
    }


def _ensure_artifact(output_dir: Path, stdout: str) -> None:
    """Ensure hadolint JSON artifact exists under output directory."""
    if any(output_dir.glob("*.json")):
        return
    if not stdout.strip():
        raise ValueError("Hadolint produced no JSON stdout or output artifacts.")
    artifact_path = output_dir / "hadolint.json"
    artifact_path.write_text(stdout.strip(), encoding="utf-8")


def _execute_runtime_manifest(payload: dict[str, object], *, verbose: bool) -> int:
    """Execute hadolint runtime manifest through the generic tool runner."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir)
        manifest_path = temp_root / "manifest.generated.yaml"
        manifest_path.write_text(
            safe_dump(payload, sort_keys=False),
            encoding="utf-8",
        )

        result = run_tool(
            ToolRunContext(
                manifest=manifest_path,
                command=HADOLINT_COMMAND,
                image="unused-for-hadolint",
                time=datetime.now(timezone.utc),
            )
        )
        _ensure_artifact(Path(result.output), result.stdout)
        violations = hadolint_parser.parse(Path(result.output))
        hadolint_parser.report(violations)
        if verbose and result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="")
        return result.exit_code


def run(manifest_path: Path | None, verbose: bool) -> int:
    """Run hadolint against Dockerfile resolved from a manifest."""
    resolved_manifest = _resolve_manifest_path(manifest_path)
    dockerfile = _resolve_dockerfile(resolved_manifest)

    docker.pull(HADOLINT_IMAGE, quiet=not verbose)
    console.print("[cyan]Running hadolint...[/cyan]")

    return _execute_runtime_manifest(_runtime_manifest(dockerfile), verbose=verbose)
