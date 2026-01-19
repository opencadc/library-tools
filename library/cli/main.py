"""Command Line Interface for CANFAR Container Library."""

from __future__ import annotations

import typer

from library.utils.console import console


def callback(ctx: typer.Context) -> None:
    """Main callback that handles no subcommand case."""
    if ctx.invoked_subcommand is None:
        # No subcommand was invoked, show help and exit cleanly
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


def main() -> None:
    """Main entry point."""
    try:
        cli()
    except Exception as exc:
        console.print(f"[red]Error: {exc}[/red]")
        raise typer.Exit(1) from exc


if __name__ == "__main__":
    main()
