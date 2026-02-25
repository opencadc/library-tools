"""Helpers for deterministic tool run workspace paths."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

RUN_TIME_FORMAT = "%Y%m%dT%H%M%SZ"
OUTPUT_ROOT_DIRNAME = ".library-tool-outputs"


def format(run_time: datetime) -> str:
    """Format run time using UTC basic format."""
    if run_time.tzinfo is None:
        utc_time = run_time.replace(tzinfo=timezone.utc)
    else:
        utc_time = run_time.astimezone(timezone.utc)
    return utc_time.strftime(RUN_TIME_FORMAT)


def create(root: Path, tool_id: str, run_time: datetime) -> Path:
    """Create and return deterministic host run directory."""
    run_dir = root.resolve() / OUTPUT_ROOT_DIRNAME / tool_id / format(run_time)
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir
