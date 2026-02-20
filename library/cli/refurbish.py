"""Refurbish CLI helpers (renovate backend)."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from library import default
from library.cli import manifest
from library.parsers import refurbish as refurbish_parser
from library.tools import ToolRunContext, run as run_tool
from library.utils import docker
from library.utils.console import console

REFURBISH_COMMAND = "refurbish"


def _ensure_artifact(output_dir: Path, stdout: str) -> None:
    """Ensure refurbish output artifact exists under output directory."""
    if any(output_dir.iterdir()):
        return
    if not stdout.strip():
        raise ValueError("Refurbish produced no output artifacts.")
    artifact_path = output_dir / "refurbish.log"
    artifact_path.write_text(stdout.strip(), encoding="utf-8")


def run(manifest_path: Path | None, verbose: bool) -> dict[str, list[dict[str, object]]]:
    """Run refurbish against Dockerfile resolved from a manifest."""
    resolved_manifest = manifest.resolve(manifest_path, required=True)
    assert resolved_manifest is not None

    docker.pull(default.RefurbishTool.image, quiet=not verbose)
    console.print("[cyan]Running refurbish...[/cyan]")

    result = run_tool(
        ToolRunContext(
            manifest=resolved_manifest,
            command=REFURBISH_COMMAND,
            image="unused-for-refurbish",
            time=datetime.now(timezone.utc),
        )
    )
    _ensure_artifact(Path(result.output), result.stdout)
    summary = refurbish_parser.parse(Path(result.output))
    refurbish_parser.report(summary)
    if verbose and result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="")
    return summary
