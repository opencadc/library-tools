"""Runtime models for generic tool execution."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, ConfigDict, DirectoryPath


class ToolRunContext(BaseModel):
    """Execution context for a single generic tool run."""

    manifest: Path
    command: str
    image: str
    time: datetime

    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class ToolRunResult(BaseModel):
    """Result payload returned by the generic tool runner."""

    tool: str
    output: DirectoryPath
    exit_code: int
    stdout: str
    stderr: str

    model_config = ConfigDict(extra="forbid", validate_assignment=True)
