"""Default/override tool catalog resolution."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from library import default
from library.schema import Config, Tool


@dataclass(slots=True)
class ResolvedCatalog:
    """Effective tools/cli catalog for command execution."""

    tools: list[Tool]
    cli: dict[str, str]
    source: Literal["default", "manifest"]


def _default_tools() -> list[Tool]:
    """Return deep-copied package default tool definitions."""
    return [tool.model_copy(deep=True) for tool in default.DefaultTools]


def resolve(config: Config) -> ResolvedCatalog:
    """Resolve effective tools catalog from defaults and manifest overrides."""
    has_tools = bool(config.tools)
    has_cli = bool(config.cli)

    if has_tools and has_cli:
        return ResolvedCatalog(
            tools=[tool.model_copy(deep=True) for tool in config.tools],
            cli=dict(config.cli),
            source="manifest",
        )
    if has_tools != has_cli:
        raise ValueError(
            "Manifest override requires both config.tools and config.cli."
        )
    return ResolvedCatalog(
        tools=_default_tools(),
        cli=dict(default.DefaultCli),
        source="default",
    )
