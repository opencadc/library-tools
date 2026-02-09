# Library Tools

!!! warning "Work in Progress"
    This document is a work in progress. It is based on the current design and is subject to change. 

This document explains how tool configuration works in the Library manifest, how tool execution is normalized, and how to customize or extend tooling safely.

## Goals

- Provide a single, opinionated workflow that is still configurable for power users.
- Keep tooling consistent across local runs and CI/CD.
- Make tool outputs machine-parseable and auditable.
- Minimize per-tool special cases by standardizing execution.

## Concepts

### Tools (config.tools)

Each CLI command maps to a tool configuration in the manifest under `config.tools`:

- `library lint` -> `config.tools.lint`
- `library scan` -> `config.tools.scan`
- `library refurbish` -> `config.tools.refurbish`
- `library curate` -> `config.tools.curate`
- `library provenance` -> `config.tools.provenance`
- `library push` -> `config.tools.push`

Each tool configuration includes:

- `parser`: which built-in parser to use for the JSON output.
- `config` (optional): host path to a tool config file.
- `runner` (optional): inline runner configuration.
- `output`: host path where the tool writes JSON output.

### Parsers

Parsers are built-in, name-locked implementations.

Current parser options:

- `hadolint`
- `trivy`
- `renovate`
- `curate`
- `provenance`
- `push`

If you need a new parser, it should be implemented in the library (e.g., `library.parsers.<name>`) and then added to the schema enum.

### Runners

Runners describe how to execute a tool. In P0 we support Docker-only runners.

Runners are embedded directly in each tool configuration via `config.tools.<tool>.runner`.

## Fixed Workspace Contract

All tools run in a standardized workspace. The CLI is responsible for preparing the workspace and wiring paths into the container.

Inside the tool container:

- `/workspace/src` is the project working directory, usually mapped to the `.`.
- `/workspace/tool-config.yaml` is the tool configuration file provided via `--config` or `config`.
- `/workspace/tool-output.json` is the output file target corresponding to `output`.

This contract eliminates tool-by-tool mount configuration. Tool runners should always reference these paths.

## Tool Output Contract

Every tool must write a JSON file to `output` on the host. The CLI copies this to `/workspace/tool-output.json` inside the container and parses it after execution.

## Defaults

If you do not specify tool configurations, the schema supplies defaults for each tool (including default output locations). You can override any field explicitly.

Default output paths:

- `lint` -> `./artifacts/lint.json`
- `scan` -> `./artifacts/scan.json`
- `refurbish` -> `./artifacts/refurbish.json`
- `curate` -> `./artifacts/curate.json`
- `provenance` -> `./artifacts/provenance.json`
- `push` -> `./artifacts/push.json`

## Examples

### Minimal tool config (accept defaults)

```yaml
config: {}
```

### Lint with a custom hadolint config

```yaml
config:
  tools:
    lint:
      parser: hadolint
      config: ./ci/hadolint.yaml
      output: ./artifacts/lint.json
      runner:
        kind: docker
        image: docker.io/hadolint/hadolint:latest
        command:
          - hadolint
          - --format
          - json
          - --config
          - /workspace/tool-config.yaml
          - /workspace/src/Dockerfile
```

### Scan with Trivy (image scan)

```yaml
config:
  tools:
    scan:
      parser: trivy
      output: ./artifacts/scan.json
      runner:
        kind: docker
        image: docker.io/aquasec/trivy:latest
        command:
          - trivy
          - image
          - --format
          - json
          - --output
          - /workspace/tool-output.json
          - --config
          - /workspace/tool-config.yaml
          # The CLI injects the image reference for the current build.
```

### Refurbish with Renovate

```yaml
config:
  tools:
    refurbish:
      parser: renovate
      config: ./renovate.json5
      output: ./artifacts/refurbish.json
      runner:
        kind: docker
        image: renovate/renovate:latest
        command:
          - renovate
          - --platform
          - local
          - --config-file
          - /workspace/tool-config.yaml
```

### Curate and Provenance (built-in Python tools)

Curate and provenance can run without a Docker runner. If `runner` is omitted, the CLI uses the built-in Python implementation.

```yaml
config:
  tools:
    curate:
      parser: curate
      output: ./artifacts/curate.json

    provenance:
      parser: provenance
      output: ./artifacts/provenance.json
```

### Push (built-in Python tool)

Push behavior is configured by the tool config file (not the manifest). If you need to change push behavior, point `config` at a custom config file.

```yaml
config:
  tools:
    push:
      parser: push
      config: ./ci/push.yaml
      output: ./artifacts/push.json
```

## CLI Overrides

CLI flags override manifest settings:

- `--config` overrides `config`.
- `--output` overrides `output`.

The CLI always stages these into `/workspace/tool-config.yaml` and `/workspace/tool-output.json` before executing the runner.

## Custom Tools

If you want to add a new tool:

1. Implement a parser in the library (`library.parsers.<name>`).
2. Add the parser name to the `Tool.parser` enum in the schema.
3. Define the tool configuration under `config.tools.<tool>` and provide a runner or built-in implementation.

This keeps the manifest stable while allowing extension via code.
