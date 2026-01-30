# Library Scan (Trivy) Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add `library scan DOCKERIMAGE` to run Trivy in Docker, output JSON, and fail on HIGH/CRITICAL CVEs with configurable DB cache.

**Architecture:** Add a Trivy CLI helper that ensures the target image exists locally, runs a Trivy container against the local Docker daemon, and streams JSON output to stdout. Wire the helper into the Typer CLI and provide a repo-level Trivy config.

**Tech Stack:** Python (Typer, Rich), Docker CLI, Trivy container.

### Task 1: Add failing tests for the new scan command

**Files:**
- Create: `tests/cli/test_trivy.py`

**Step 1: Write the failing test (CLI invokes Trivy with JSON + severity)**

```python
from __future__ import annotations

import subprocess

from tests.cli.conftest import cli


def test_library_scan_invokes_trivy_with_json(cli_runner, monkeypatch) -> None:
    """Invoke scan and assert Trivy args include JSON + severity."""
    captured = {}

    def fake_run(command, verbose=False, emit_output=True):
        captured["command"] = command
        return subprocess.CompletedProcess(command, 0, "[]", "")

    monkeypatch.setattr("library.cli.trivy.docker.run", fake_run)
    monkeypatch.setattr("library.cli.trivy.docker.pull", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("library.cli.trivy.docker.image_exists", lambda *_args, **_kwargs: True)

    result = cli_runner.invoke(cli, ["scan", "docker.io/library/alpine:3.20"])

    assert result.exit_code == 0
    assert "trivy" in " ".join(captured["command"])
    assert "--format" in captured["command"]
    assert "json" in captured["command"]
    assert "--severity" in captured["command"]
    assert "HIGH,CRITICAL" in captured["command"]
    assert result.stdout.strip() == "[]"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/cli/test_trivy.py::test_library_scan_invokes_trivy_with_json -v`
Expected: FAIL with `ImportError` or `AttributeError` (scan/trivy helpers not implemented).

**Step 3: Write the failing test (pull image when missing)**

```python
def test_library_scan_pulls_missing_image(cli_runner, monkeypatch) -> None:
    """Pull target image when it is not present locally."""
    pulled = {}

    def fake_pull(image):
        pulled["image"] = image

    monkeypatch.setattr("library.cli.trivy.docker.pull", fake_pull)
    monkeypatch.setattr("library.cli.trivy.docker.image_exists", lambda *_args, **_kwargs: False)
    monkeypatch.setattr(
        "library.cli.trivy.docker.run",
        lambda command, verbose=False, emit_output=True: subprocess.CompletedProcess(command, 0, "[]", ""),
    )

    result = cli_runner.invoke(cli, ["scan", "docker.io/library/alpine:3.20"])

    assert result.exit_code == 0
    assert pulled["image"] == "docker.io/library/alpine:3.20"
```

**Step 4: Run test to verify it fails**

Run: `pytest tests/cli/test_trivy.py::test_library_scan_pulls_missing_image -v`
Expected: FAIL with `ImportError` or missing helper.

**Step 5: Write the failing test (cache dir mount + env)**

```python
def test_library_scan_mounts_cache_dir(cli_runner, monkeypatch, tmp_path) -> None:
    """Mount the cache directory and export TRIVY_CACHE_DIR."""
    cache_dir = tmp_path / "trivy-cache"
    captured = {}

    def fake_run(command, verbose=False, emit_output=True):
        captured["command"] = command
        return subprocess.CompletedProcess(command, 0, "[]", "")

    monkeypatch.setattr("library.cli.trivy.docker.run", fake_run)
    monkeypatch.setattr("library.cli.trivy.docker.pull", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("library.cli.trivy.docker.image_exists", lambda *_args, **_kwargs: True)

    result = cli_runner.invoke(
        cli,
        ["scan", "docker.io/library/alpine:3.20", "--cache-dir", str(cache_dir)],
    )

    assert result.exit_code == 0
    joined = " ".join(captured["command"])
    assert f"{cache_dir}:/trivy-cache" in joined
    assert "TRIVY_CACHE_DIR=/trivy-cache" in joined
```

**Step 6: Run test to verify it fails**

Run: `pytest tests/cli/test_trivy.py::test_library_scan_mounts_cache_dir -v`
Expected: FAIL until cache handling exists.

**Step 7: Commit**

```bash
git add tests/cli/test_trivy.py
git commit -m "test(cli): add failing scan command tests"
```

### Task 2: Add Trivy config and Docker helper primitives

**Files:**
- Create: `library/.trivy.yaml`
- Modify: `library/utils/docker.py`
- Modify: `library/__init__.py`

**Step 1: Write minimal Trivy config**

```yaml
format: json
severity:
  - HIGH
  - CRITICAL
scanners:
  - vuln
vuln-type:
  - os
  - library
ignore-unfixed: false
```

**Step 2: Add Docker image existence helper**

```python
def image_exists(image: str) -> bool:
    result = subprocess.run(
        ["docker", "image", "inspect", image],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0
```

**Step 3: Add optional quiet parameters to Docker helpers**

```python
def pull(image: str, *, quiet: bool = False) -> None:
    if not quiet:
        console.print(f"[cyan]Docker: Pulling Image {image}[/cyan]")
    result = subprocess.run(
        ["docker", "pull", image],
        check=False,
        stdout=subprocess.PIPE if quiet else None,
        stderr=subprocess.PIPE if quiet else None,
        text=True,
    )
    if not quiet:
        console.print("[cyan]Docker: Pull Complete.[/cyan]")
    if quiet and result.returncode != 0 and result.stderr:
        console.print(result.stderr, stderr=True)
```

```python
def run(command: Sequence[str], *, verbose: bool, emit_output: bool = True) -> subprocess.CompletedProcess[str]:
    console.print("[cyan]Docker: Starting Container...[/cyan]")
    process = subprocess.run(
        list(command),
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if emit_output:
        if process.stderr:
            console.print(process.stderr, end="")
        if verbose and process.stdout:
            console.print(process.stdout, end="")
        console.print(
            f"[cyan]Docker: Container Finished with exit code {process.returncode}.[/cyan]"
        )
    return process
```

**Step 4: Add Trivy config constant**

```python
TRIVY_CONFIG_PATH = Path(__file__).resolve().parent / ".trivy.yaml"
```

**Step 5: Run targeted tests**

Run: `pytest tests/cli/test_trivy.py::test_library_scan_invokes_trivy_with_json -v`
Expected: FAIL (trivy helper not implemented yet).

**Step 6: Commit**

```bash
git add library/.trivy.yaml library/utils/docker.py library/__init__.py
git commit -m "chore: add trivy config and docker helpers"
```

### Task 3: Implement Trivy scan helper

**Files:**
- Create: `library/cli/trivy.py`

**Step 1: Write minimal implementation**

```python
from __future__ import annotations

import tempfile
from pathlib import Path

from library import TRIVY_CONFIG_PATH
from library.utils import docker
from library.utils.console import console


def run(image: str, cache_dir: Path, verbose: bool) -> int:
    if not docker.image_exists(image):
        docker.pull(image, quiet=not verbose)

    docker.pull("docker.io/aquasec/trivy:latest", quiet=not verbose)

    cache_dir = cache_dir.expanduser().resolve()
    cache_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config_path = temp_path / ".trivy.yaml"
        config_path.write_text(TRIVY_CONFIG_PATH.read_text(encoding="utf-8"), encoding="utf-8")

        command = [
            "docker",
            "run",
            "--rm",
            "-v",
            "/var/run/docker.sock:/var/run/docker.sock",
            "-v",
            f"{cache_dir}:/trivy-cache",
            "-e",
            "TRIVY_CACHE_DIR=/trivy-cache",
            "-v",
            f"{temp_path}:/work",
            "-w",
            "/work",
            "docker.io/aquasec/trivy:latest",
            "image",
            "--config",
            "/work/.trivy.yaml",
            "--format",
            "json",
            "--severity",
            "HIGH,CRITICAL",
            "--exit-code",
            "1",
            "--quiet",
            "--no-progress",
            image,
        ]

        process = docker.run(command, verbose=verbose, emit_output=False)

        if process.stderr:
            console.print(process.stderr, end="", stderr=True)
        if process.stdout:
            console.print(process.stdout, end="")

        return process.returncode
```

**Step 2: Run targeted tests**

Run: `pytest tests/cli/test_trivy.py::test_library_scan_invokes_trivy_with_json -v`
Expected: PASS

Run: `pytest tests/cli/test_trivy.py::test_library_scan_pulls_missing_image -v`
Expected: PASS

Run: `pytest tests/cli/test_trivy.py::test_library_scan_mounts_cache_dir -v`
Expected: PASS

**Step 3: Commit**

```bash
git add library/cli/trivy.py
git commit -m "feat(cli): add trivy scan helper"
```

### Task 4: Wire CLI command

**Files:**
- Modify: `library/cli/__init__.py`
- Modify: `library/cli/main.py`

**Step 1: Export trivy module**

```python
from library.cli import hadolint, renovate, trivy

__all__ = ["hadolint", "renovate", "trivy"]
```

**Step 2: Add `scan` command**

```python
@cli.command("scan", help="Scan a Docker image for CVEs.")
def scan_command(
    image: str = typer.Argument(..., help="Docker image to scan."),
    cache_dir: Path = typer.Option(
        Path("~/.cache/trivy"), "--cache-dir", help="Trivy DB cache directory."
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output."),
) -> None:
    exit_code = trivy.run(image, cache_dir, verbose)
    raise typer.Exit(exit_code)
```

**Step 3: Run targeted tests**

Run: `pytest tests/cli/test_trivy.py::test_library_scan_invokes_trivy_with_json -v`
Expected: PASS

**Step 4: Commit**

```bash
git add library/cli/__init__.py library/cli/main.py
git commit -m "feat(cli): add scan command"
```

### Task 5: Full verification

**Files:**
- None

**Step 1: Run full test suite**

Run: `pytest`
Expected: PASS

**Step 2: Commit (if any changes)**

```bash
git status
```
