"""Tests for schema markdown generation."""

from __future__ import annotations

from pathlib import Path

from library.utils.generate import generate_schema_markdown


def test_generate_schema_markdown_writes_file(tmp_path: Path) -> None:
    """Generate markdown output to a target file."""
    output_path = tmp_path / "schema.md"

    generate_schema_markdown(output_path)

    contents = output_path.read_text(encoding="utf-8")
    assert contents.startswith("---")
    assert "hide:" in contents
