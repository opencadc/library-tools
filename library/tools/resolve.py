"""Resolution helpers for command -> tool lookups."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from library.schema import Schema, Tool


def tool_id(command: str, cli: Mapping[str, str]) -> str:
    """Resolve a CLI command name to a configured tool id."""
    tool_id = cli.get(command)
    if tool_id is None:
        raise ValueError(f"Unknown tool command mapping: {command}")
    return tool_id


def tool(tool_id: str, tools: Sequence[Tool]) -> Tool:
    """Resolve tool id to tool definition with duplicate-id defense."""
    matches = [tool for tool in tools if tool.id == tool_id]
    if not matches:
        raise ValueError(f"Unknown tool id: {tool_id}")
    if len(matches) > 1:
        raise ValueError(f"Duplicate tool id found: {tool_id}")
    return matches[0]


def for_command(manifest: Schema, command: str) -> Tool:
    """Resolve command mapping and return the configured Tool."""
    resolved_id = tool_id(command=command, cli=manifest.config.cli)
    return tool(tool_id=resolved_id, tools=manifest.config.tools)
