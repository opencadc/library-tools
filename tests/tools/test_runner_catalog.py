"""Tests for default-vs-manifest tool catalog resolution."""

from __future__ import annotations

import pytest

from library.schema import Config, Tool
from library.tools import catalog


def _scan_tool(tool_id: str = "custom-scan") -> Tool:
    return Tool(
        id=tool_id,
        parser="trivy",
        image="docker.io/aquasec/trivy:latest",
        command=["trivy", "image", "{{image.reference}}"],
        outputs="/outputs/",
    )


def test_catalog_resolve_uses_package_defaults_when_empty_override() -> None:
    """Empty config tools/cli should resolve to package defaults."""
    resolved = catalog.resolve(Config())

    assert resolved.source == "default"
    assert "scan" in resolved.cli
    assert "lint" in resolved.cli
    assert "refurbish" in resolved.cli
    assert len(resolved.tools) >= 3


def test_catalog_resolve_uses_manifest_override_when_complete() -> None:
    """When tools and cli are both provided, manifest replaces defaults."""
    custom_tool = _scan_tool()
    resolved = catalog.resolve(
        Config(
            policy="default",
            conflicts="warn",
            tools=[custom_tool],
            cli={"scan": custom_tool.id},
        )
    )

    assert resolved.source == "manifest"
    assert resolved.tools == [custom_tool]
    assert resolved.cli == {"scan": custom_tool.id}


def test_catalog_resolve_rejects_partial_override_tools_only() -> None:
    """Partial override with tools-only should fail fast."""
    with pytest.raises(
        ValueError, match="requires both config.tools and config.cli"
    ):
        catalog.resolve(
            Config(
                policy="default",
                conflicts="warn",
                tools=[_scan_tool()],
            )
        )


def test_catalog_resolve_rejects_partial_override_cli_only() -> None:
    """Partial override with cli-only should fail fast."""
    with pytest.raises(
        ValueError, match="requires both config.tools and config.cli"
    ):
        catalog.resolve(
            Config(
                policy="default",
                conflicts="warn",
                cli={"scan": "custom-scan"},
            )
        )
