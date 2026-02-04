# Library Workflow Lifecycle

This document describes the lifecycle of containerized research software under the Library Tools.

The workflow is command-oriented and manifest-driven, designed for scientists and developers who need reproducible, secure outputs without manually stitching together container quality tooling.

## Lifecycle Overview

Phase 0 Lifecycle Stages:

1. Initialize manifest (`library init`)
2. Validate quality policy (`library lint`)
3. Build image (`library build`)
4. Scan vulnerabilities (`library scan`)
5. Modernize dependencies (`library refurbish`)
6. Curate metadata/artifacts (`library curate`)
7. Publish in phases (`library push image`, `library push metadata`, or `library push all`)

Phase 1 Lifecycle Stages:

1. Generate SLSA provenance (`library provenance generate`)
2. Verify SLSA provenance (`library verify`)
3. Publish provenance to remote server (`library push provenance`)
4. Publish metadata to remote server (`library push metadata`)
5. Search for metadata (`library search`)
6. Expand `library refurbish` to support multiple additional backends (e.g. `apt`, `pip`, etc.)

## 1) Initialize Manifest

`library init` creates a structured manifest that captures:

- Project and maintainer identity.
- Build source and build intent.
- Image naming and tagging intent.
- Discovery metadata intent.

The manifest is the canonical contract for later commands.

## 2) Lint and Policy Validation

`library lint` evaluates manifest and Dockerfile quality against a selected policy profile:

- `baseline`: default scientist-friendly profile.
- `strict`: CI/release-oriented profile.
- `expert`: power-user minimal baseline.

Users can override defaults using repository policy files, tool-specific config files, or CLI flags.

## 3) Build

`library build` executes buildx-compatible image builds from manifest intent.

Advanced users can pass extra buildx arguments via passthrough (`-- <args>`), while the CLI protects manifest-owned options from accidental override. e.g. `library build manifest.yaml --ssh=default` will pass the `--ssh` flag to buildx.

## 4) Scan

`library scan` runs vulnerability checks against target images. Results are structured for both human review and downstream curation.

## 5) Refurbish (Dependency Modernization)

`library refurbish` updates Dockerfile dependency references and modernization opportunities. This step replaces the previous `renovate` command naming and aligns with the broader workflow language.

## 6) Curate (Metadata + Artifact Packaging)

`library curate` assembles a coherent package from:

- Manifest fields.
- Lint outputs.
- Scan outputs.
- Refurbish outputs.
- Build outputs.

Metadata source-of-truth behavior:

- Manifest remains canonical.
- Dockerfile/image metadata import is explicit and optional.
- Imported values are emitted as suggestions/patch proposals unless explicitly accepted.

## 7) Push (Phase-Separated Publication)

Publication is explicitly split to improve reliability and operational clarity:

- `library push image`: push image artifacts to registry targets.
- `library push metadata`: emit metadata publish bundles (P0 file-based output).
- `library push provenance`: push provenance information to registry targets.
- `library push all`: run all push commands in sequence.

This phase separation enables partial retries and predictable recovery behavior.

## CI Lifecycle Alignment

In Git-based CI, e.g. GitHub Actions, GitLab Pipelines, the same lifecycle applies with stricter profile defaults and machine-readable outputs for automation.

The local developer workflow and CI workflow should stay behaviorally aligned; only policy strictness and credentials differ by environment.

## Out of Scope in P0

The following are deferred to P1:

- SLSA/provenance generation and verification workflows.
- Remote metadata server publish integration.
- `library search`.
- Non-repo local directory reduced mode.

## Example Manifest Direction

The manifest schema remains the central contract and is expected to evolve to better represent discovery metadata and publication intent.

Key direction for metadata semantics:

- Canonical metadata is declared in manifest.
- OCI label/annotation materialization happens during build/curation from manifest intent.
- Dockerfile labels can be inspected and proposed back to the manifest, but do not silently replace canonical values.
