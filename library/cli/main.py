"""Command line entrypoints for the CANFAR Container Library."""

from __future__ import annotations

from pathlib import Path

import json

import typer

from library import schema
from library.cli import build, hadolint, refurbish, trivy
from library.utils.console import console
from library import DEFAULT_LIBRARY_MANIFEST_FILENAME


def callback(ctx: typer.Context) -> None:
    """Handle the top-level CLI callback.

    Args:
        ctx: Typer context for the current invocation.
    """
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())
        raise typer.Exit(0)


def _format_update_line(update: dict[str, object]) -> str | None:
    """Format a single refurbish update line.

    Args:
        update: Update record from renovate.

    Returns:
        Formatted update line or None.
    """
    dep_name = update.get("depName") or update.get("packageName")
    new_value = update.get("newValue") or update.get("newVersion")
    new_digest = update.get("newDigest")
    update_type = update.get("updateType") or "update"
    if not dep_name or not new_value:
        return None
    digest_suffix = f"@{new_digest}" if new_digest else ""
    return f"- {dep_name}: {new_value}{digest_suffix} ({update_type})"


def _emit_refurbish_summary(
    summary: dict[str, list[dict[str, object]]], *, json_output: bool
) -> None:
    """Emit refurbish summary output.

    Args:
        summary: Renovate summary data.
        json_output: Whether to emit JSON output.
    """
    updates = summary.get("updates", [])
    if updates:
        console.print("[cyan]Detected updates:[/cyan]")
        for update in updates:
            line = _format_update_line(update)
            if line:
                console.print(line)
    else:
        console.print("[yellow]No updates detected.[/yellow]")
    if json_output:
        console.print_json(json.dumps(summary))


cli: typer.Typer = typer.Typer(
    name="library",
    help="CANFAR Container Library",
    no_args_is_help=False,  # Disable automatic help to handle manually
    add_completion=True,
    pretty_exceptions_show_locals=True,
    pretty_exceptions_enable=True,
    pretty_exceptions_short=True,
    epilog="For more information, visit https://opencadc.github.io/library-tools/",
    rich_markup_mode="rich",
    rich_help_panel="CANFAR Container Library CLI",
    callback=callback,
    invoke_without_command=True,  # Allow callback to be called without subcommand
)


@cli.command("lint", help="Check Dockerfile for best practices.")
def linter(
    manifest: Path = typer.Option(
        Path.cwd() / DEFAULT_LIBRARY_MANIFEST_FILENAME,
        "--manifest",
        "-m",
        help=("Path to library manifest file."),
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output."
    ),
) -> None:
    """Run hadolint against Dockerfile resolved from a manifest.

    Args:
        manifest: Path to the manifest file.
        verbose: Whether to emit verbose output.
    """
    exit_code = hadolint.run(manifest, verbose)
    if exit_code == 0:
        console.print("[green]✅ Hadolint completed successfully.[/green]")
    else:
        console.print(f"[red]❌ Hadolint failed with exit code {exit_code}.[/red]")
    raise typer.Exit(exit_code)


@cli.command("scan", help="Check Container Image for CVEs.")
def scanner(
    image: str = typer.Argument(..., help="Docker image to scan."),
    manifest: Path = typer.Option(
        Path.cwd() / DEFAULT_LIBRARY_MANIFEST_FILENAME,
        "--manifest",
        "-m",
        help=("Path to library manifest file."),
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output."
    ),
) -> None:
    """Run Trivy against a Docker image.

    Args:
        image: Docker image to scan.
        manifest: Path to optional manifest file.
        verbose: Whether to emit verbose output.
    """
    exit_code = trivy.run(image, manifest, verbose)
    raise typer.Exit(exit_code)


@cli.command("refurbish", help="Find outdated dependencies.")
def refurbisher(
    manifest: Path = typer.Option(
        Path.cwd() / DEFAULT_LIBRARY_MANIFEST_FILENAME,
        "--manifest",
        "-m",
        help=("Path to library manifest file."),
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output."
    ),
    jsonify: bool = typer.Option(
        False, "--json", help="Emit raw JSON updates summary."
    ),
) -> None:
    """Run refurbish against a manifest.

    Args:
        manifest: Path to the manifest.
        verbose: Whether to emit verbose output.
        json_output: Whether to emit JSON output.
    """
    summary = refurbish.run(manifest, verbose)
    _emit_refurbish_summary(summary, json_output=jsonify)


@cli.command("validate", help="Check manifest for compliance.")
def validator(path: Path) -> None:
    """Validate a manifest file against the schema.

    Args:
        path: Path to the manifest to validate.
    """
    schema.Manifest.from_yaml(path)
    console.print("[green]✅ Manifest is valid.[/green]")


@cli.command(
    "build",
    help="Build a container image with buildx.",
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def builder(ctx: typer.Context, path: Path) -> None:
    """Build a container image using the manifest defaults.

    Args:
        ctx: Typer context for extra args.
        path: Path to the manifest file.
    """
    exit_code = build.run_build(path, list(ctx.args))
    raise typer.Exit(exit_code)


def main() -> None:
    """Run the CLI entrypoint."""
    try:
        cli()
    except Exception as exc:
        console.print(f"[red]❌ Error: {exc}[/red]")


if __name__ == "__main__":
    main()
