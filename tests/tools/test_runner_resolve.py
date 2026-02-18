"""Tests for command/tool resolution helpers."""

from __future__ import annotations

import pytest

from library.schema import Tool
from library.tools import resolve


def _tool(tool_id: str) -> Tool:
    return Tool(
        id=tool_id,
        parser="trivy",
        image="docker.io/aquasec/trivy:latest",
        command=["trivy", "image", "{{image.reference}}"],
        outputs="/outputs/",
    )


def test_resolve_tool_id_success() -> None:
    """Resolve command mapping to a configured tool id."""
    tool_id = resolve.tool_id(command="scan", cli={"scan": "default-scanner"})

    assert tool_id == "default-scanner"


def test_resolve_tool_id_unknown_command_fails() -> None:
    """Unknown command mapping raises a clear error."""
    with pytest.raises(ValueError):
        resolve.tool_id(command="scan", cli={"lint": "default-linter"})


def test_resolve_tool_unknown_id_fails() -> None:
    """Unknown tool id raises an error."""
    with pytest.raises(ValueError):
        resolve.tool(tool_id="missing", tools=[_tool("default-scanner")])


def test_resolve_tool_duplicate_ids_fail() -> None:
    """Duplicate tool ids are rejected defensively."""
    with pytest.raises(ValueError):
        resolve.tool(
            tool_id="default-scanner",
            tools=[_tool("default-scanner"), _tool("default-scanner")],
        )
