"""Command line entrypoints for the CANFAR Container Library."""

from __future__ import annotations

from pathlib import Path

import json
import typer

from library import DEFAULT_LIBRARY_MANIFEST_FILENAME
from library.cli import dispatch
from library.cli import init as cli_init
from library.utils.console import console


def callback(ctx: typer.Context) -> None:
    """Handle the top-level CLI callback.

    Args:
        ctx: Typer context for the current invocation.
    """
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())
        raise typer.Exit(0)


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
        Path(DEFAULT_LIBRARY_MANIFEST_FILENAME),
        "--manifest",
        "-m",
        help=("Path to library manifest file."),
        exists=True,
        readable=True,
        file_okay=True,
        dir_okay=False,
        resolve_path=True,
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
    dispatched = dispatch.run_tool_command(
        "lint",
        manifest=manifest,
        image=None,
        verbose=verbose,
    )
    exit_code = dispatched.result.exit_code
    if exit_code == 0:
        console.print("[green]✅ Hadolint completed successfully.[/green]")
    else:
        console.print(f"[red]❌ Hadolint failed with exit code {exit_code}.[/red]")
    raise typer.Exit(exit_code)


@cli.command("init", help="Create a manifest interactively.")
def initializer(
    output: Path = typer.Option(
        Path(DEFAULT_LIBRARY_MANIFEST_FILENAME),
        "--output",
        "-o",
        help="Output path for the manifest file.",
        file_okay=True,
        dir_okay=False,
        writable=True,
        resolve_path=True,
    ),
) -> None:
    """Collect and save a fully materialized manifest."""
    cli_init.run_init(output)


@cli.command("scan", help="Check Container Image for CVEs.")
def scanner(
    image: str | None = typer.Argument(
        None,
        help="Docker image to scan. If omitted, derive from manifest defaults.",
    ),
    manifest: Path = typer.Option(
        Path(DEFAULT_LIBRARY_MANIFEST_FILENAME),
        "--manifest",
        "-m",
        help=("Path to library manifest file."),
        file_okay=True,
        dir_okay=False,
        resolve_path=True,
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output."
    ),
) -> None:
    """Run Trivy against a Docker image.

    Args:
        image: Docker image to scan, if provided.
        manifest: Path to optional manifest file.
        verbose: Whether to emit verbose output.
    """
    try:
        dispatched = dispatch.run_scan_command(
            manifest=manifest,
            image=image,
            verbose=verbose,
        )
    except ValueError as exc:
        console.print(f"[red]❌ {exc}[/red]")
        raise typer.Exit(2) from exc
    exit_code = dispatched.result.exit_code
    raise typer.Exit(exit_code)


@cli.command("refurbish", help="Find outdated dependencies.")
def refurbisher(
    manifest: Path = typer.Option(
        Path(DEFAULT_LIBRARY_MANIFEST_FILENAME),
        "--manifest",
        "-m",
        help=("Path to library manifest file."),
        exists=True,
        readable=True,
        file_okay=True,
        dir_okay=False,
        resolve_path=True,
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
    dispatched = dispatch.run_tool_command(
        "refurbish",
        manifest=manifest,
        image=None,
        verbose=verbose,
    )
    if jsonify:
        console.print_json(json.dumps(dispatched.payload))
    raise typer.Exit(dispatched.result.exit_code)


@cli.command("validate", help="Check manifest for compliance.")
def validator(path: Path) -> None:
    """Validate a manifest file against the schema.

    Args:
        path: Path to the manifest to validate.
    """
    dispatch.run_validate(path)


@cli.command(
    "build",
    help="Build a container image with buildx.",
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def builder(
    ctx: typer.Context,
    manifest: Path = typer.Option(
        Path(DEFAULT_LIBRARY_MANIFEST_FILENAME),
        "--manifest",
        "-m",
        help=("Path to library manifest file."),
        exists=True,
        readable=True,
        file_okay=True,
        dir_okay=False,
        resolve_path=True,
    ),
) -> None:
    """Build a container image using the manifest defaults.

    Args:
        ctx: Typer context for extra args.
        manifest: Path to the manifest file.
    """
    exit_code = dispatch.run_build(manifest, list(ctx.args))
    raise typer.Exit(exit_code)


def main() -> None:
    """Run the CLI entrypoint."""
    try:
        cli()
    except Exception as exc:
        console.print(f"[red]❌ Error: {exc}[/red]")


if __name__ == "__main__":
    main()
