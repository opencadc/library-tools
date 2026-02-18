"""Tests for deterministic run workspace creation."""

from __future__ import annotations

from datetime import datetime, timezone

from library.tools import workspace


def test_workspace_path_shape_and_time_format(tmp_path) -> None:
    """Run workspace path follows ./outputs/{tool-id}/{DATETIME}/."""
    run_time = datetime(2026, 2, 18, 19, 20, 21, tzinfo=timezone.utc)

    assert workspace.format(run_time) == "20260218T192021Z"

    run_dir = workspace.create(
        root=tmp_path,
        tool_id="default-scanner",
        run_time=run_time,
    )

    assert run_dir == tmp_path / "outputs" / "default-scanner" / "20260218T192021Z"
    assert run_dir.is_dir()
