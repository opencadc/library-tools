"""Tests for CLI helper utilities."""

from __future__ import annotations

from pathlib import Path

from library.cli import helpers
from library.schema import Manifest


def test_helpers_read_dockerfile(tmp_path: Path) -> None:
    """Read Dockerfile contents from disk."""
    dockerfile_path = tmp_path / "Dockerfile"
    dockerfile_path.write_text("FROM alpine:3.19\n", encoding="utf-8")

    contents = helpers.read_dockerfile(dockerfile_path)

    assert contents == "FROM alpine:3.19\n"


def test_helpers_resolve_dockerfile_contents(tmp_path: Path) -> None:
    """Resolve Dockerfile contents for local paths."""
    dockerfile_path = tmp_path / "Dockerfile"
    dockerfile_path.write_text("FROM alpine:3.19\n", encoding="utf-8")

    contents = helpers.resolve_dockerfile_contents(None, dockerfile_path)

    assert contents == "FROM alpine:3.19\n"


def test_helpers_prepare_workspace(tmp_path: Path) -> None:
    """Write workspace files for Dockerfile and config."""
    config_source = tmp_path / "tool.yaml"
    config_source.write_text("rules: {}\n", encoding="utf-8")

    helpers.prepare_workspace(
        temp_path=tmp_path,
        dockerfile_contents="FROM alpine:3.19\n",
        config_source=config_source,
        config_name=".tool.yaml",
        label="tool",
    )

    assert (tmp_path / "Dockerfile").read_text(encoding="utf-8") == "FROM alpine:3.19\n"
    assert (tmp_path / ".tool.yaml").read_text(encoding="utf-8") == "rules: {}\n"


def test_helpers_load_manifest(fixtures_dir: Path) -> None:
    """Load a manifest from YAML fixtures."""
    manifest_path = fixtures_dir / "manifest.valid.yml"

    manifest_model = helpers.load_manifest(manifest_path)

    assert isinstance(manifest_model, Manifest)
    assert manifest_model.metadata.discovery.authors


def test_helpers_parse_json_output() -> None:
    """Parse JSON output into a Python object."""
    payload = helpers.parse_json_output('{"ok": true}')

    assert payload == {"ok": True}
