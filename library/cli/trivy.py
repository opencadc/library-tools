"""Trivy CLI helpers."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import tempfile

from yaml import safe_dump

from library import default
from library.cli import manifest
from library.parsers import trivy as trivy_parser
from library.tools import ToolRunContext, run as run_tool
from library.utils import docker
from library.utils.console import console

TRIVY_COMMAND = "scan"


def _ensure_image_present(image: str, *, verbose: bool) -> None:
    """Ensure the target image exists locally."""
    if not docker.image_exists(image):
        docker.pull(image, quiet=not verbose)


def _runtime_manifest_payload() -> dict[str, object]:
    """Build a minimal runtime manifest that uses package tool defaults."""
    return {
        "version": 1,
        "registry": {
            "host": "images.canfar.net",
            "project": "library",
            "image": "runtime-scan",
        },
        "build": {"context": ".", "file": "Dockerfile", "tags": ["local"]},
        "metadata": {
            "discovery": {
                "title": "Runtime Scan",
                "description": "Generated manifest for scan execution.",
                "source": "https://github.com/opencadc/canfar-library",
                "url": "https://images.canfar.net/library/runtime-scan",
                "documentation": "https://canfar.net/docs/user-guide",
                "version": "1.0.0",
                "revision": "1234567890123456789012345678901234567890",
                "created": "2026-02-18T00:00:00Z",
                "authors": [
                    {"name": "Library Tooling", "email": "tooling@example.com"}
                ],
                "licenses": "MIT",
                "keywords": ["scan", "runtime"],
                "domain": ["astronomy"],
                "kind": ["headless"],
            }
        },
        "config": {},
    }


def _run_with_manifest(manifest_path: Path, image: str, verbose: bool) -> int:
    """Execute trivy through generic runner for a concrete manifest path."""
    result = run_tool(
        ToolRunContext(
            manifest=manifest_path,
            command=TRIVY_COMMAND,
            image=image,
            time=datetime.now(timezone.utc),
        )
    )
    payload = trivy_parser.parse(Path(result.output))
    trivy_parser.report(payload)
    if verbose and result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="")
    return result.exit_code


def run(image: str, manifest_path: Path | None, verbose: bool) -> int:
    """Run trivy against a Docker image."""
    _ensure_image_present(image, verbose=verbose)
    docker.pull(default.TrivyTool.image, quiet=not verbose)
    console.print("[cyan]Running trivy...[/cyan]")
    resolved_manifest = manifest.resolve(manifest_path, required=False)
    if resolved_manifest is not None:
        return _run_with_manifest(resolved_manifest, image, verbose)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir)
        generated = temp_root / "manifest.generated.yaml"
        generated.write_text(
            safe_dump(_runtime_manifest_payload(), sort_keys=False),
            encoding="utf-8",
        )
        return _run_with_manifest(generated, image, verbose)
