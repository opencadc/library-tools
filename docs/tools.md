# Library Tools

This document defines the developer contract for tool configuration in `config`.

## Runtime Status

Runtime scaffolding is now wired into CLI commands:

- `library lint`
- `library scan`
- `library refurbish`

Command dispatch is centralized in `library/cli/dispatch.py`. Each command now
resolves an effective manifest, resolves command-to-tool mapping, runs the
tool container, then routes outputs through the built-in parser registry in
`library/parsers/__init__.py`.

## Phase 2 Hadolint Refactor

Hadolint is now wired through the generic tool runner.

- CLI entrypoint: `library/cli/main.py` (via `library/cli/dispatch.py`)
- Runner call: `library.tools.run(ToolRunContext(...))`
- Parser module: `library/parsers/hadolint.py`
- Parser API:
  - `hadolint.parse(output_dir: Path) -> list[dict[str, object]]`
  - `hadolint.report(violations: list[dict[str, object]]) -> int`

Parser modules now live under `library/parsers` and are imported as:

```python
from library.parsers import hadolint
```

Manifest path behavior for `library lint`:

- Canonical manifest filename: `.library.manifest.yaml`
- Optional override: `library lint --manifest <path>`
- Default behavior: if `--manifest` is omitted, CLI uses
  `./.library.manifest.yaml`.

For hadolint, the manifest `build.context` + `build.file` resolve the Dockerfile path.
That Dockerfile is mounted into the container as `/inputs/Dockerfile`.

Runtime API:

- `ToolRunContext`
  - `manifest: Path`
  - `command: str`
  - `image: str`
  - `time: datetime`
- `ToolRunResult`
  - `tool: str`
  - `output: DirectoryPath`
  - `exit_code: int`
  - `stdout: str`
  - `stderr: str`

## Goals

- Keep the schema simple and explicit.
- Run every tool in Docker.
- Require tools to write one or more JSON outputs into `/outputs/`.
- Support built-in defaults and local user overrides for tool inputs.

## Config Shape

Tool configuration is flattened under `config`:

- `config.policy`
- `config.conflicts`
- `config.tools`
- `config.cli`

## Config Fields

### `config.policy`

Policy profile:

- `default`
- `strict`
- `expert`

### `config.conflicts`

Conflict handling behavior:

- `warn`
- `strict`

### `config.tools`

List of tool definitions. Each tool entry has:

- `id`: unique tool id.
- `parser`: built-in parser name.
- `image`: Docker image used for execution.
- `command`: tokenized argv command.
- `env`: environment variables for the tool container.
- `inputs`: named input mapping (`ToolInputs`).
- `socket`: whether `/var/run/docker.sock` is mounted.
- `outputs`: fixed literal `/outputs/`.

`config.tools` is optional and defaults to `[]`.

### `config.cli`

Dictionary mapping CLI command names to tool ids.

Example:

- `scan: default-scanner`
- `lint: default-linter`

`config.cli` is required.

Validation rules:

- every tool id in `config.tools` must be unique.
- every `config.cli` target must reference an existing tool id.
- catalog selection behavior:
  - runtime commands require a fully materialized config block in the manifest.
  - defaults are materialized when manifests are created/saved.
  - `config.tools` and `config.cli` are used directly as provided.
  - deep merge and tool-by-id patch semantics are not applied.

## Tool Inputs

Each `tools[].inputs.<key>` entry contains:

- `source`: either:
  - `default` for packaged built-in config
  - a local file path
- `destination`: absolute path inside the container where input is mounted

## Runtime Contract

1. Every tool runs in Docker.
2. Container outputs path is fixed: `/outputs/`.
3. Host run workspace is deterministic:
   - `./outputs/{tool-id}/{DATETIME}/`
4. Host run workspace is always mounted into container as `/outputs`.
5. All tool outputs are written to `/outputs/*` inside the container.
6. `inputs` are resolved and mounted at `destination`.

## Variables and Source of Truth

| Variable | Example | Source |
| --- | --- | --- |
| `tool.id` | `default-scanner` | `config.tools[]` |
| `tool.image` | `docker.io/aquasec/trivy:latest` | `config.tools[]` |
| `tool.command` | `["trivy", "image", ...]` | `config.tools[]` |
| `tool.inputs.<key>.source` | `default` or `./ci/trivy.yaml` | `config.tools[]` |
| `tool.inputs.<key>.destination` | `/config/trivy.yaml` | `config.tools[]` |
| `tool.socket` | `true` | `config.tools[]` |
| `tool.outputs` | `/outputs/` | `config.tools[]` (fixed literal) |
| `image.reference` | `docker.io/library/alpine:3.19` | `ToolRunContext.image` |
| `DATETIME` | `20260217T213015Z` | `ToolRunContext.time` (UTC formatted) |

## Supported Command Tokens

Phase 1 runtime rendering supports only:

- `{{inputs.<key>}}`
- `{{image.reference}}`

Examples:

- `{{inputs.trivy}}` -> value from `inputs.trivy.destination`
- `{{image.reference}}` -> runtime image reference value

## Complete Lifecycle

1. Caller creates `ToolRunContext` and provides:
   - `manifest`: manifest path
   - `command`: logical command key (for example `scan`)
   - `image`: runtime image reference token value
   - `time`: run timestamp
2. Runtime manifest lifecycle loads `manifest.Manifest` from YAML/dict:
   - `manifest.Manifest` inherits `schema.Schema`.
   - runtime defaults and validators are implemented in `library/manifest.py`.
   - `library/schema.py` remains the canonical interoperability contract.
   - compact manifests can be materialized once via `python -m library.manifest_migrate <path>`.
3. `library.tools.runner.run(context)` resolves:
   - `cli[command]` -> `tool.id`
   - `tool.id` -> `tools[]` entry
4. Runner computes run directory:
   - `./outputs/{tool-id}/{DATETIME}/`
5. Runner creates that run directory.
6. Runner resolves each input source:
   - `default` -> packaged config in the library
   - file path -> local override (resolved from manifest directory when relative)
7. Runner mounts each resolved input to its `destination` (read-only).
8. Runner mounts host run directory to container `/outputs` (read-write).
9. Runner mounts Docker socket if `socket=true`.
10. Runner renders command tokens and runs the tool container.
11. Tool writes one or more JSON files into `/outputs/`.
12. JSON artifacts are available on host under `./outputs/{tool-id}/{DATETIME}/`.
13. Runner returns `ToolRunResult` with tool id, output directory, exit code, stdout, and stderr.

## Runnable Example

```python
from datetime import datetime, timezone
from pathlib import Path

from library.tools import ToolRunContext
from library.tools.runner import run

result = run(
    ToolRunContext(
        manifest=Path("manifest.yaml"),
        command="scan",
        image="images.canfar.net/library/my-image:latest",
        time=datetime.now(timezone.utc),
    )
)

print(result.tool, result.exit_code, result.output)
```

## Minimal Example

```yaml
config:
  policy: default
  conflicts: warn
  tools:
    - id: default-scanner
      parser: trivy
      image: docker.io/aquasec/trivy:latest
      command:
        - trivy
        - image
        - --config
        - "{{inputs.trivy}}"
        - --format
        - json
        - --output
        - /outputs/scan.json
        - "{{image.reference}}"
      inputs:
        trivy:
          source: default
          destination: /config/trivy.yaml
      socket: true
      outputs: /outputs/
  cli:
    scan: default-scanner
```

## Advanced Example

```yaml
config:
  policy: strict
  conflicts: strict
  tools:
    - id: srcnet-scanner
      parser: trivy
      image: docker.io/aquasec/trivy:latest
      env:
        TRIVY_CACHE_DIR: /tmp/trivy-cache
      command:
        - trivy
        - image
        - --config
        - "{{inputs.trivy}}"
        - --format
        - json
        - --output
        - /outputs/scan.json
        - "{{image.reference}}"
      inputs:
        trivy:
          source: ./ci/trivy-srcnet.yaml
          destination: /config/trivy.yaml
        policy:
          source: ./ci/policy.yaml
          destination: /config/policy.yaml
      socket: true
      outputs: /outputs/
  cli:
    scan: srcnet-scanner
```
