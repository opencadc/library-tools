"""Shared console utilities for CLI output."""

from __future__ import annotations

from functools import lru_cache

from rich.console import Console


@lru_cache(maxsize=1)
def get_console() -> Console:
    """Get a Rich console configured from the user configuration.

    Returns:
        Console: Rich console instance.
    """
    terminal = Console(width=120)
    return terminal


# Convenience instance for modules that just need a console
console: Console = get_console()
