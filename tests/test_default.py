"""Tests for runtime defaults exposed by tools.defaults."""

from __future__ import annotations

from library.tools import defaults


def test_runtime_default_tools_include_lint_scan_refurbish() -> None:
    """Defaults module should ship runtime default tool catalog."""
    model = defaults.default_config()

    assert model.cli == {
        "lint": "default-linter",
        "scan": "default-scanner",
        "refurbish": "default-refurbisher",
    }
    tool_ids = {tool.id for tool in model.tools}
    assert tool_ids == {"default-linter", "default-scanner", "default-refurbisher"}


def test_runtime_default_hadolint_inputs_shape() -> None:
    """Hadolint runtime default should keep expected input destinations."""
    model = defaults.default_config()
    tool = next(tool for tool in model.tools if tool.id == "default-linter")

    assert tool.outputs == "/outputs/"
    assert tool.inputs["hadolint"].destination == "/inputs/.hadolint.yaml"
    assert tool.inputs["dockerfile"].destination == "/inputs/Dockerfile"
