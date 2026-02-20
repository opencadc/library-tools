"""Tests for refurbish output parsing and reporting."""

from __future__ import annotations

from pathlib import Path

import pytest

from library.parsers import refurbish


def test_parse_builds_update_summary_from_json_lines(tmp_path: Path) -> None:
    """Parse should aggregate updates from json line artifacts."""
    (tmp_path / "run.log").write_text(
        "\n".join(
            [
                '{"depName": "ghcr.io/astral-sh/uv", "newVersion": "0.9.1"}',
                '{"updates": [{"depName": "python", "newVersion": "3.13.2"}]}',
            ]
        ),
        encoding="utf-8",
    )

    summary = refurbish.parse(tmp_path)

    dep_names = {item.get("depName") for item in summary.get("updates", [])}
    assert {"ghcr.io/astral-sh/uv", "python"} <= dep_names


def test_parse_requires_output_artifacts(tmp_path: Path) -> None:
    """Parse should fail when output directory has no artifacts."""
    with pytest.raises(ValueError):
        refurbish.parse(tmp_path)


def test_report_returns_update_count() -> None:
    """Report should return number of updates."""
    summary = {
        "updates": [
            {"depName": "ghcr.io/astral-sh/uv", "newVersion": "0.9.1"},
            {"depName": "python", "newVersion": "3.13.2"},
        ]
    }

    count = refurbish.report(summary)

    assert count == 2
