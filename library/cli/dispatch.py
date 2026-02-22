"""Shared CLI dispatch for tool-backed and adapter-backed commands."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import json
import tempfile

from library import manifest as runtime_manifest
from library import schema
from library.cli import build, manifest as cli_manifest
from library.parsers import get as get_parser
from library.tools import ToolRunContext, ToolRunResult, run as run_tool
from library.tools import resolve as tool_resolve
from library.utils import docker
from library.utils.console import console


@dataclass(slots=True)
class ToolDispatchResult:
    """Result payload for a shared tool-backed CLI command dispatch."""

    command: str
    tool_id: str
    parser: str
    payload: object
    result: ToolRunResult


def _ensure_artifacts(parser: str, output_dir: Path, stdout: str) -> None:
    """Ensure expected artifacts exist for parsers that can emit stdout only."""
    if parser == "hadolint":
        if any(output_dir.glob("*.json")):
            return
        if not stdout.strip():
            raise ValueError("Hadolint produced no JSON stdout or output artifacts.")
        artifact_path = output_dir / "hadolint.json"
        artifact_path.write_text(stdout.strip(), encoding="utf-8")
        return
    if parser == "renovate":
        if any(output_dir.iterdir()):
            return
        if not stdout.strip():
            raise ValueError("Refurbish produced no output artifacts.")
        artifact_path = output_dir / "refurbish.log"
        artifact_path.write_text(stdout.strip(), encoding="utf-8")


def _prepare_manifest(command: str, manifest_path: Path | None) -> tuple[Path, tempfile.TemporaryDirectory[str] | None]:
    """Resolve command manifest path, generating defaults for scan when absent."""
    required = command in {"lint", "refurbish"}
    resolved = cli_manifest.resolve(manifest_path, required=required)
    if resolved is not None:
        return resolved, None
    if command != "scan":
        raise ValueError(f"No runtime manifest strategy defined for command: {command}")

    temp_dir = tempfile.TemporaryDirectory()
    generated = Path(temp_dir.name) / "manifest.generated.yaml"
    generated.write_text(runtime_manifest.default_manifest_yaml(), encoding="utf-8")
    return generated, temp_dir


def _default_image_reference(command: str) -> str:
    """Return a non-semantic image reference placeholder for non-image commands."""
    return f"unused-for-{command}"


def run_tool_command(
    command: str,
    *,
    manifest_path: Path | None,
    image_reference: str | None,
    verbose: bool,
) -> ToolDispatchResult:
    """Run a tool-backed command through shared manifest-driven dispatch."""
    resolved_manifest_path, temp_dir = _prepare_manifest(command, manifest_path)
    try:
        effective = runtime_manifest.effective_manifest(resolved_manifest_path)
        tool = tool_resolve.for_command(effective, command)
        docker.pull(tool.image, quiet=not verbose)
        console.print(f"[cyan]Running {tool.parser}...[/cyan]")

        result = run_tool(
            ToolRunContext(
                manifest=resolved_manifest_path,
                command=command,
                image=image_reference or _default_image_reference(command),
                time=datetime.now(timezone.utc),
            )
        )
        _ensure_artifacts(tool.parser, Path(result.output), result.stdout)

        parser = get_parser(tool.parser)
        payload = parser.parse(Path(result.output))
        parser.report(payload)
        if verbose and result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="")
        return ToolDispatchResult(
            command=command,
            tool_id=tool.id,
            parser=tool.parser,
            payload=payload,
            result=result,
        )
    finally:
        if temp_dir is not None:
            temp_dir.cleanup()


def run_validate(path: Path) -> None:
    """Run validate command through shared dispatcher adapter."""
    runtime_manifest.effective_manifest(path)
    console.print("[green]✅ Manifest is valid.[/green]")


def run_build(path: Path, extra_args: list[str]) -> int:
    """Run build command through shared dispatcher adapter."""
    return build.run_build(path, extra_args)


def emit_refurbish_payload(payload: object, *, json_output: bool) -> None:
    """Emit optional JSON for refurbish command output payload."""
    if json_output:
        console.print_json(json.dumps(payload))
