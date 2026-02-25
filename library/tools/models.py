"""Runtime models for generic tool execution."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, ConfigDict, DirectoryPath, model_validator

from library.schema import Tool


class ToolRunContext(BaseModel):
    """Execution context for a single generic tool run."""

    manifest: Path | None = None
    command: str
    image: str
    time: datetime
    tool: Tool | None = None
    output_root: Path | None = None

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    @model_validator(mode="after")
    def validate_resolution_inputs(self) -> "ToolRunContext":
        """Require either a manifest path or an explicit tool definition."""
        if self.manifest is None and self.tool is None:
            raise ValueError(
                "Tool execution requires a manifest path or explicit tool config."
            )
        return self


class ToolRunResult(BaseModel):
    """Result payload returned by the generic tool runner."""

    tool: str
    output: DirectoryPath
    exit_code: int
    stdout: str
    stderr: str

    model_config = ConfigDict(extra="forbid", validate_assignment=True)
