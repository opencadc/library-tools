"""Refurbish (renovate backend) output parser and reporter."""

from __future__ import annotations

import json
from pathlib import Path

from library.utils.console import console


def parse(output: Path) -> dict[str, list[dict[str, object]]]:
    """Parse refurbish output artifacts into an updates summary."""
    artifacts = sorted([path for path in output.iterdir() if path.is_file()])
    if not artifacts:
        raise ValueError(f"No refurbish artifacts found under: {output}")

    updates: list[dict[str, object]] = []
    for artifact in artifacts:
        for line in artifact.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or not line.startswith("{"):
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if "branchesInformation" in record:
                for branch in record.get("branchesInformation", []):
                    if isinstance(branch, dict):
                        upgrades = branch.get("upgrades", [])
                        if isinstance(upgrades, list):
                            updates.extend(
                                item for item in upgrades if isinstance(item, dict)
                            )
                continue
            if "updates" in record:
                parsed_updates = record.get("updates", [])
                if isinstance(parsed_updates, list):
                    updates.extend(
                        item for item in parsed_updates if isinstance(item, dict)
                    )
                continue
            if "depName" in record:
                updates.append(record)
    return {"updates": updates}


def report(summary: dict[str, list[dict[str, object]]]) -> int:
    """Emit refurbish summary output and return update count."""
    updates = summary.get("updates", [])
    if updates:
        console.print("[cyan]Detected updates:[/cyan]")
        for update in updates:
            dep_name = update.get("depName") or update.get("packageName")
            new_value = update.get("newValue") or update.get("newVersion")
            if dep_name and new_value:
                console.print(f"- {dep_name}: {new_value}")
    else:
        console.print("[yellow]No updates detected.[/yellow]")
    return len(updates)
