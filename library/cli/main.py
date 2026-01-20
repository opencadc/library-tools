"""Command line entrypoints for the CANFAR Container Library."""

from __future__ import annotations

from pathlib import Path

import typer
from pydantic import ValidationError

from library import manifest
from library.cli import hadolint
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
    epilog="For more information, visit https://opencadc.github.io/canfar-library/",
    rich_markup_mode="rich",
    rich_help_panel="CANFAR Container Library CLI",
    callback=callback,
    invoke_without_command=True,  # Allow callback to be called without subcommand
)


@cli.command("validate", help="Validate a library manifest.")
def validate_command(path: Path) -> None:
    """Validate a manifest file against the schema.

    Args:
        path: Path to the manifest to validate.
    """
    data = manifest.read(path)
    manifest.validate(data)
    console.print("[green]✅ Manifest is valid.[/green]")


@cli.command("hadolint", help="Lint a Dockerfile from a manifest.")
def hadolint_command(path: Path) -> None:
    """Run hadolint against a manifest Dockerfile.

    Args:
        path: Path to the manifest to lint.
    """
    exit_code = hadolint.run_hadolint(path)
    raise typer.Exit(exit_code)


def main() -> None:
    """Run the CLI entrypoint."""
    try:
        cli()
    except ValidationError as exc:
        console.print(f"[red]❌ Error: {exc}[/red]")


if __name__ == "__main__":
    main()
