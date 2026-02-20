"""Trivy output parser and reporter."""

from __future__ import annotations

import json
from pathlib import Path

from library.cli import helpers
from library.utils.console import console


def parse(output: Path) -> dict[str, object]:
    """Parse trivy JSON artifacts from a tool output directory."""
    artifacts = sorted(output.glob("*.json"))
    if not artifacts:
        raise ValueError(f"No trivy JSON artifacts found under: {output}")

    payload = json.loads(artifacts[0].read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Invalid trivy payload in artifact: {artifacts[0]}")
    return payload


def report(payload: dict[str, object]) -> int:
    """Emit trivy results and return vulnerability count."""
    helpers.print_json_output(payload)
    vulnerabilities = 0
    for item in payload.get("Results", []):
        if isinstance(item, dict):
            vulnerabilities += len(item.get("Vulnerabilities", []))
    if vulnerabilities:
        console.print(f"[red]Trivy vulnerabilities found: {vulnerabilities}[/red]")
    else:
        console.print("[green]Trivy: No vulnerabilities found.[/green]")
    return vulnerabilities
