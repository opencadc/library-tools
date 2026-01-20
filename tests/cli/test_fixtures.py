from __future__ import annotations

from tests.cli.conftest import FIXTURES


def test_fixture_manifests_present() -> None:
    assert (FIXTURES / "manifest.valid.yml").exists()
