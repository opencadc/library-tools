# Technical Design

Library Tools is a manifest-driven CLI and CI workflow for producing high-quality containerized research software. It standardizes authoring, linting, building, scanning, dependency modernization, metadata curation, and publishing into an auditable sequence that is easy for scientists to use and configurable for advanced users.

## Commands

## `library init`

Creates a manifest from user input using a RichForms interactive Pydantic form.
The command prompts an init-focused form model and then materializes a strict
runtime `Schema` instance before writing YAML. Internal runtime-only fields are
excluded from prompting via `json_schema_extra` RichForms metadata.
`metadata.discovery.created` uses a UTC default factory, and
`metadata.discovery.revision` plus full `config` defaults are injected by init.

CLI surface:

- `library init [--output|-o PATH]`

Behavior:

- Output defaults to `./.library.manifest.yaml`.
- If output exists, users get an overwrite confirmation prompt.
- Parent directories for `--output` are created automatically.
- Non-interactive init modes are deferred to a later phase.

## `library lint`

Runs policy checks against Dockerfile and manifest-driven expectations. Under the hood, integrates hadolint and related validation logic, while allowing config overrides.

CLI surface:

- `library lint [--manifest|-m PATH] [--verbose|-v]`

## `library build`

Builds container images from manifest intent. Supports passthrough args to buildx (`-- <args>`) with guardrails that prevent overriding manifest-owned fields (for example tag/platform/file metadata controls).

CLI surface:

- `library build [--manifest|-m PATH] [-- <buildx-args>]`

## `library scan`

Runs vulnerability analysis against target images (Trivy backend initially), with profile-controlled thresholds and optional explicit scanner config overrides.

CLI surface:

- `library scan [IMAGE] [--manifest|-m PATH] [--verbose|-v]`

Behavior:

- If IMAGE is omitted and a manifest exists, scan derives an image reference
  from `registry.*` and the first `build.tags` entry.
- If IMAGE is provided and no manifest exists, scan runs with packaged default
  scanner configuration.

## `library refurbish`

Replaces `library renovate` as the dependency modernization command. Updates Dockerfile dependency references and emits structured summaries suitable for curation and review.

CLI surface:

- `library refurbish [--manifest|-m PATH] [--verbose|-v] [--json]`

## `library curate`

Assembles a coherent metadata package from:

- Manifest content.
- Lint results.
- Scan results.
- Refurbish outputs.
- Build outputs.

Curation can explicitly import metadata hints from Dockerfile/image, but imported values become suggestions unless accepted into manifest source.

## `library push`

Publishes in explicit phases:

- `push image`: pushes container image artifacts to configured registry targets.
- `push metadata`: writes local publish bundles in P0.
- `push all`: orchestrates both phases in sequence with clear partial-failure reporting.

## Data and Metadata Model

## Manifest as Canonical Contract

The manifest is the source of truth for build and metadata intent. The schema remains strict and machine-validated.

Metadata precedence rules:

1. Manifest values are canonical.
2. Dockerfile/image metadata may be inspected during curation only when explicitly requested.
3. Conflicts are reported; source values are not silently replaced.

## OCI Metadata Handling

OCI keys are expected to be fully resolvable from manifest metadata. Build operations inject label/annotation values from manifest intent so generated artifacts remain consistent and auditable.

## Policy Configuration Model

Policy is layered and transparent:

1. Built-in profile defaults (`default`, `strict`, `expert`).
2. Repository policy file overrides.
3. Tool-specific config files (hadolint/trivy/refurbish backend).
4. CLI flag overrides.

Tool catalog behavior:

- Default: package-shipped tools/CLI mapping are used.
- Runtime loading uses `library/schema.py`, and recommended defaults are
  provided by `library/tools/defaults.py`.
- Defaults are materialized into manifests at creation/save time.
- `config.tools` and `config.cli` are consumed as provided; deep merge semantics are not used.
- Token validation, CLI mapping integrity, duplicate tool-id checks, and
  destination path checks are implemented in `library/schema.py`.
- Canonical YAML load/save helpers (`from_yaml`, `from_dict`, `save`) are
  implemented in `library/schema.py`.

Each command should emit effective policy information to reduce ambiguity and simplify debugging.

## CI/CD Behavior

In CI, the same command contract is used with stricter profile defaults and structured outputs for automated evaluation. The system is designed so that local workflows and CI workflows are behaviorally aligned, with policy-level differences made explicit.

## Failure Handling Principles

- Commands emit deterministic exit codes and machine-readable outputs.
- Phase boundaries permit retry and recovery (`push metadata` can run independently of `push image`).
- Tool backend failures are surfaced with actionable remediation guidance.
- Profile and override resolution is logged to explain why checks passed/failed.
