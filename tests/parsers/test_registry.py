"""Tests for parser registry lookup."""

from __future__ import annotations

import pytest

from library import parsers


def test_parser_registry_exposes_builtin_parsers() -> None:
    """Registry should include built-in parser backends."""
    registry = parsers.registry()

    assert {"hadolint", "trivy", "renovate"} <= set(registry)


def test_parser_lookup_returns_parser_adapter() -> None:
    """Lookup should resolve parse/report callables by parser key."""
    adapter = parsers.get("trivy")

    assert callable(adapter.parse)
    assert callable(adapter.report)


def test_parser_lookup_rejects_unknown_parser() -> None:
    """Unknown parser key should raise a clear error."""
    with pytest.raises(ValueError, match="Unknown parser"):
        parsers.get("missing-parser")
