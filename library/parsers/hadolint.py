"""Hadolint output parser and reporter."""

from __future__ import annotations

from pathlib import Path
import json

from library.cli import helpers
from library.utils.console import console


def parse(output: Path) -> list[dict[str, object]]:
    """Parse hadolint JSON artifacts from a tool output directory."""
    artifacts = sorted(output.glob("*.json"))
    if not artifacts:
        raise ValueError(f"No hadolint JSON artifacts found under: {output}")

    violations: list[dict[str, object]] = []
    for artifact in artifacts:
        payload = json.loads(artifact.read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            raise ValueError(f"Invalid hadolint payload in artifact: {artifact}")
        for violation in payload:
            if isinstance(violation, dict):
                violations.append(violation)
    return violations


def report(violations: list[dict[str, object]]) -> int:
    """Emit hadolint results and return number of violations."""
    helpers.print_json_output(violations)
    if violations:
        console.print(f"[red]Hadolint violations found: {len(violations)}[/red]")
    else:
        console.print("[green]Hadolint: No violations found.[/green]")
    return len(violations)
