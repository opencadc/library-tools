"""Command line entrypoints for the CANFAR Container Library."""

from __future__ import annotations

from pathlib import Path

import json

import typer
from pydantic import ValidationError

from library import manifest
from library.cli import hadolint, renovate, trivy
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


@cli.command("lint", help="Check for best practices.")
def hadolint_command(
    path: Path | None = typer.Argument(None, help="Path to a manifest file."),
    dockerfile: Path | None = typer.Option(
        None, "--dockerfile", help="Path to a Dockerfile."
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output."
    ),
) -> None:
    """Run hadolint against a manifest or Dockerfile.

    Args:
        path: Path to the manifest to lint.
        dockerfile: Path to a Dockerfile.
        verbose: Whether to emit verbose output.
    """
    exit_code = hadolint.run(path, dockerfile, verbose)
    if exit_code == 0:
        console.print("[green]✅ Hadolint completed successfully.[/green]")
    else:
        console.print(f"[red]❌ Hadolint failed with exit code {exit_code}.[/red]")
    raise typer.Exit(exit_code)


@cli.command("scan", help="Check Container Image for CVEs.")
def scan_command(
    image: str = typer.Argument(..., help="Docker image to scan."),
    cache_dir: Path = typer.Option(
        Path("~/.cache/trivy"), "--cache-dir", help="Trivy DB cache directory."
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output."
    ),
) -> None:
    """Run Trivy against a Docker image.

    Args:
        image: Docker image to scan.
        cache_dir: Trivy DB cache directory.
        verbose: Whether to emit verbose output.
    """
    exit_code = trivy.run(image, cache_dir, verbose)
    raise typer.Exit(exit_code)


@cli.command("renovate", help="Find outdated dependencies.")
def renovate_command(
    path: Path | None = typer.Argument(None, help="Path to a manifest file."),
    dockerfile: Path | None = typer.Option(
        None, "--dockerfile", help="Path to a Dockerfile."
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output."
    ),
    json_output: bool = typer.Option(
        False, "--json", help="Emit raw JSON updates summary."
    ),
) -> None:
    """Run renovate against a manifest or Dockerfile.

    Args:
        path: Path to the manifest to scan.
        dockerfile: Path to a Dockerfile.
        verbose: Whether to emit verbose output.
        json_output: Whether to emit JSON output.
    """
    summary = renovate.run_renovate(path, dockerfile, verbose)
    updates = summary.get("updates", [])
    if updates:
        console.print("[cyan]Detected updates:[/cyan]")
        for update in updates:
            dep_name = update.get("depName") or update.get("packageName")
            new_value = update.get("newValue") or update.get("newVersion")
            new_digest = update.get("newDigest")
            update_type = update.get("updateType") or "update"
            if dep_name and new_value:
                digest_suffix = f"@{new_digest}" if new_digest else ""
                console.print(
                    f"- {dep_name}: {new_value}{digest_suffix} ({update_type})"
                )
    else:
        console.print("[yellow]No updates detected.[/yellow]")
    if json_output:
        console.print_json(json.dumps(summary))


@cli.command("validate", help="Check manifest for compliance.")
def validate_command(path: Path) -> None:
    """Validate a manifest file against the schema.

    Args:
        path: Path to the manifest to validate.
    """
    data = manifest.read(path)
    manifest.validate(data)
    console.print("[green]✅ Manifest is valid.[/green]")


def main() -> None:
    """Run the CLI entrypoint."""
    try:
        cli()
    except ValidationError as exc:
        console.print(f"[red]❌ Error: {exc}[/red]")


if __name__ == "__main__":
    main()
