"""Tests for shipped default tool definitions."""

from __future__ import annotations

from library import default


def test_hadolint_default_tool_shape() -> None:
    """Hadolint default tool should match runtime contract inputs/outputs."""
    tool = default.HadolintTool

    assert tool.id == "default-linter"
    assert tool.outputs == "/outputs/"
    assert tool.inputs["hadolint"].destination == "/inputs/.hadolint.yaml"
    assert tool.inputs["dockerfile"].destination == "/inputs/Dockerfile"
    assert default.HadolintCli == {"lint": "default-linter"}
