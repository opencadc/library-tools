"""Interactive manifest initialization for the CLI."""

from __future__ import annotations

from pathlib import Path
import subprocess

from pydantic import BaseModel, ConfigDict
from richforms import FormConfig, fill
import typer

from library import schema
from library.tools import defaults as runtime_defaults
from library.utils.console import console


class InitForm(BaseModel):
    """Prompt-focused manifest fields collected by `library init`."""

    registry: schema.Registry
    build: schema.Build
    metadata: schema.Metadata

    model_config = ConfigDict(extra="forbid", validate_assignment=True)


def _current_revision() -> str:
    """Return git HEAD revision, or 'unknown' if unavailable."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return "unknown"
    if result.returncode != 0:
        return "unknown"
    revision = result.stdout.strip()
    return revision or "unknown"


def _confirm_overwrite(path: Path) -> bool:
    """Prompt user for overwrite confirmation."""
    return typer.confirm(
        f"Manifest already exists at {path}. Overwrite?",
        default=False,
    )


def run_init(output: Path) -> None:
    """Run interactive manifest initialization and save the result."""
    output_path = output.expanduser().resolve()

    if output_path.exists():
        if not output_path.is_file():
            raise ValueError(f"Output path exists and is not a file: {output_path}")
        if not _confirm_overwrite(output_path):
            console.print(f"[yellow]ℹ️ Manifest left unchanged: {output_path}[/yellow]")
            return

    try:
        form = fill(
        InitForm,
        config=FormConfig(),
    )
    except KeyboardInterrupt as exc:
        console.print("[yellow]⚠️ Init canceled.[/yellow]")
        raise typer.Exit(code=130) from exc

    model = schema.Schema(
        version=1,
        registry=form.registry,
        build=form.build,
        metadata=form.metadata,
        config=runtime_defaults.default_config(),
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    model.save(output_path)
    console.print(f"[green]✅ Wrote manifest: {output_path}[/green]")


__all__ = [
    "InitForm",
    "run_init",
]
