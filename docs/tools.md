# Library Tools

This document defines the developer contract for tool configuration in `config`.

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

### `config.cli`

Dictionary mapping CLI command names to tool ids.

Example:

- `scan: default-scanner`
- `lint: default-linter`

Validation rules:

- every tool id in `config.tools` must be unique.
- every `config.cli` target must reference an existing tool id.

## ToolInputs

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
| `image.reference` | `docker.io/library/alpine:3.19` | CLI runtime |
| `DATETIME` | `20260217T213015Z` | CLI runtime clock |

## Supported Command Tokens

The schema validates these tokens in `tool.command`:

- `{{inputs.<key>}}`
- `{{image.reference}}`

Examples:

- `{{inputs.trivy}}` -> value from `inputs.trivy.destination`
- `{{image.reference}}` -> runtime image reference value

## Complete Lifecycle

1. CLI command (for example `scan`) is resolved through `config.cli` to a tool id.
2. CLI loads the matching tool from `config.tools`.
3. CLI computes run directory:
   - `./outputs/{tool-id}/{DATETIME}/`
4. CLI creates that run directory.
5. CLI resolves each input source:
   - `default` -> packaged config in the library
   - file path -> local override
6. CLI mounts each resolved input to its `destination` (read-only).
7. CLI mounts host run directory to container `/outputs` (read-write).
8. CLI mounts Docker socket if `socket=true`.
9. CLI renders command tokens and runs the tool container.
10. Tool writes one or more JSON files into `/outputs/`.
11. JSON artifacts are available on host under `./outputs/{tool-id}/{DATETIME}/`.
12. Parser selected by `tool.parser` consumes outputs for result reporting.

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
