"""Tests for hadolint output parsing and reporting."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from library.parsers import hadolint


def test_parse_collects_violations_from_json_artifacts(tmp_path: Path) -> None:
    """Parse should merge list payloads from output JSON files."""
    (tmp_path / "a.json").write_text(
        json.dumps([{"code": "DL3000"}, {"code": "DL3001"}]),
        encoding="utf-8",
    )
    (tmp_path / "b.json").write_text(
        json.dumps([{"code": "DL3002"}]),
        encoding="utf-8",
    )

    parsed = hadolint.parse(tmp_path)

    assert [item["code"] for item in parsed] == ["DL3000", "DL3001", "DL3002"]


def test_parse_requires_json_artifacts(tmp_path: Path) -> None:
    """Parse should fail when no JSON artifacts exist."""
    with pytest.raises(ValueError):
        hadolint.parse(tmp_path)


def test_report_returns_violation_count() -> None:
    """Report should return number of hadolint violations."""
    violations = [{"code": "DL3000"}, {"code": "DL3001"}]

    count = hadolint.report(violations)

    assert count == 2
