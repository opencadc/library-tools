"""Tests for build command helpers."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import subprocess

from library.cli import build as build_cli


def _tag_values(cmd: list[str]) -> list[str]:
    values: list[str] = []
    for idx, token in enumerate(cmd):
        if token == "--tag" and idx + 1 < len(cmd):
            values.append(cmd[idx + 1])
    return values


def test_run_build_expands_plain_manifest_tags(monkeypatch) -> None:
    """Build should resolve plain manifest tags to fully qualified image refs."""

    class _Build:
        def __init__(self) -> None:
            self.tags = ["latest"]
            self.options = ""
            self.platforms = ["linux/amd64"]
            self.context = "."
            self.file = "Dockerfile"
            self.output = "type=docker"

        def command(self) -> list[str]:
            cmd = ["docker", "buildx", "build", "--file", self.file]
            for tag in self.tags:
                cmd.extend(["--tag", tag])
            for platform in self.platforms:
                cmd.extend(["--platform", platform])
            cmd.extend(["--output", self.output, self.context])
            return cmd

    manifest = SimpleNamespace(
        registry=SimpleNamespace(host="images.canfar.net", project="cadc", image="library"),
        build=_Build(),
    )

    commands: list[list[str]] = []

    def fake_from_yaml(_path: Path):
        return manifest

    def fake_run(cmd: list[str], check: bool = False):
        commands.append(cmd)
        return subprocess.CompletedProcess(args=cmd, returncode=0)

    monkeypatch.setattr(build_cli.schema.Schema, "from_yaml", fake_from_yaml)
    monkeypatch.setattr(build_cli.subprocess, "run", fake_run)

    exit_code = build_cli.run_build(Path(".library.manifest.yaml"), [])

    assert exit_code == 0
    assert commands
    assert _tag_values(commands[0]) == ["images.canfar.net/cadc/library:latest"]
