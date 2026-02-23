"""Generic tool runner for manifest-defined tool execution."""

from __future__ import annotations

from pathlib import Path

from library import schema
from library.schema import Tool, ToolInputs
from library.tools import defaults, render, resolve, workspace
from library.tools.models import ToolRunContext, ToolRunResult
from library.utils import runtime

CONTAINER_OUTPUTS_PATH = "/outputs"
DOCKER_SOCKET_PATH = "/var/run/docker.sock"


def _resolve_input_source(
    *,
    manifest: Path,
    tool: Tool,
    input_key: str,
    input_config: ToolInputs,
) -> Path:
    """Resolve host input file path for a tool input entry."""
    if input_config.source == "default":
        return defaults.input(tool=tool, input_key=input_key, manifest=manifest)

    source_path = Path(str(input_config.source))
    if not source_path.is_absolute():
        source_path = manifest.parent / source_path
    source_path = source_path.resolve()
    if not source_path.is_file():
        raise ValueError(f"Input source file not found: {source_path}")
    return source_path


def _build_volumes(
    *, manifest: Path, tool: Tool, output_dir: Path
) -> dict[str, dict[str, str]]:
    """Build Docker volume bindings for outputs, inputs, and optional socket."""
    volumes: dict[str, dict[str, str]] = {
        str(output_dir): {"bind": CONTAINER_OUTPUTS_PATH, "mode": "rw"}
    }
    for input_key, input_config in tool.inputs.items():
        source = _resolve_input_source(
            manifest=manifest,
            tool=tool,
            input_key=input_key,
            input_config=input_config,
        )
        volumes[str(source)] = {"bind": input_config.destination, "mode": "ro"}

    if tool.socket:
        volumes[DOCKER_SOCKET_PATH] = {"bind": DOCKER_SOCKET_PATH, "mode": "rw"}
    return volumes


def run(context: ToolRunContext) -> ToolRunResult:
    """Run a manifest-configured tool in Docker and return execution result."""
    manifest_path = context.manifest.resolve()
    manifest_model = schema.Schema.from_yaml(manifest_path)
    tool = resolve.for_command(manifest_model, context.command)

    output_dir = workspace.create(
        root=manifest_path.parent,
        tool_id=tool.id,
        run_time=context.time,
    )
    command = render.command(
        tool.command,
        inputs=tool.inputs,
        image_reference=context.image,
    )
    result = runtime.run(
        tool.image,
        command,
        volumes=_build_volumes(
            manifest=manifest_path,
            tool=tool,
            output_dir=output_dir,
        ),
        environment=tool.env,
        verbose=False,
        emit_output=False,
        stream_output=False,
    )

    if not output_dir.is_dir():
        raise ValueError(f"Tool output directory not found: {output_dir}")

    return ToolRunResult(
        tool=tool.id,
        output=output_dir,
        exit_code=result.exit_code,
        stdout=result.stdout,
        stderr=result.stderr,
    )
