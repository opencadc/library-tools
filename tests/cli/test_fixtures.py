"""Fixture tests for CLI manifests."""

from __future__ import annotations

from tests.cli.conftest import FIXTURES


def test_fixture_manifests_present() -> None:
    """Ensure manifest fixtures are present."""
    assert (FIXTURES / "manifest.valid.yml").exists()
