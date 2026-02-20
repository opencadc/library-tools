"""Tests for trivy output parsing and reporting."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from library.parsers import trivy


def test_parse_collects_payload_from_output_artifact(tmp_path: Path) -> None:
    """Parse should load trivy JSON payload from output artifacts."""
    payload = {
        "Results": [
            {"Vulnerabilities": [{"VulnerabilityID": "CVE-1"}]},
            {"Vulnerabilities": [{"VulnerabilityID": "CVE-2"}]},
        ]
    }
    (tmp_path / "scan.json").write_text(json.dumps(payload), encoding="utf-8")

    parsed = trivy.parse(tmp_path)

    assert parsed == payload


def test_parse_requires_json_artifacts(tmp_path: Path) -> None:
    """Parse should fail when no JSON artifacts exist."""
    with pytest.raises(ValueError):
        trivy.parse(tmp_path)


def test_report_returns_vulnerability_count() -> None:
    """Report should return vulnerability count."""
    payload = {
        "Results": [
            {"Vulnerabilities": [{"VulnerabilityID": "CVE-1"}]},
            {"Vulnerabilities": [{"VulnerabilityID": "CVE-2"}]},
        ]
    }

    count = trivy.report(payload)

    assert count == 2
