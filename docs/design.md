# Library Tools Design

## Summary

Library Tools are a community-facing workflow of best practices recommendations and CLI tooling that helps scientists and developers produce high-quality containerized research software. The project focuses on reducing operational complexity for users: instead of each team independently learning container best practices, security posture, reproducibility techniques, and metadata publishing conventions, the tooling provides a guided, opinionated path with configurable policy controls.

The design target is a single workflow that works in local development and CI environments, while preserving enough flexibility for power users to tune behavior when needed.

## Intent

Library Tools exists to make high-quality container delivery the default for research software:

- Author and maintain container build definitions with a human-friendly manifest.
- Run best-practice linting and vulnerability scanning with actionable output.
- Modernize dependency baselines with a dedicated refurbish step.
- Curate build, scan, and metadata artifacts into machine-ingestible metadata bundles.
- Publish image and metadata artifacts in explicit, auditable phases.

This project is no longer only a governance framework for centralized image curation. It is a user workflow product intended for scientists first, while still supporting developers and platform maintainers.

## Design Principles

1. **Scientist-first defaults**: workflows must be simple, explainable, and safe by default.
2. **Manifest as contract**: manifest data is canonical for build and metadata intent.
3. **Opinionated, not rigid**: built-in policy profiles ship with override paths.
4. **Deterministic outputs**: commands produce structured artifacts suitable for automation.
5. **Explicit phase boundaries**: build, curate, and push are separable to improve reliability and recovery.

## Manifest-Driven Contract

The manifest is the core system contract and source of truth.

- It is human-editable YAML backed by JSON schema.
- It is machine-actionable for CLI and CI orchestration.
- It defines canonical metadata used for build labeling and curated outputs.

Metadata precedence is explicit:

- Manifest metadata is canonical.
- Metadata from Dockerfiles and Container Images metadata may be imported during curation only when explicitly requested.
- Imported metadata is surfaced as suggestions/patches, not silent source-of-truth changes.

## Opinionated Workflow with Configurable Policy

The default workflow is intentionally opinionated (`init -> lint -> build -> scan -> refurbish -> curate -> push`) but policy behavior is configurable.

Built-in policy profiles:

- `baseline`: scientist-friendly defaults with high-signal checks.
- `strict`: CI/release profile with stronger policy enforcement.
- `expert`: minimal defaults for advanced users.

Override model:

1. Profile defaults.
2. Repository-level policy overrides.
3. Tool-specific configuration overrides (e.g., hadolint, trivy, refurbish backend).
4. Command-line flags.

## Delivery Scope and Boundaries

### Phase 0: Local Development and CI

- Contexts: local repositories and Git-based CI.
- Commands: `library init`, `library lint`, `library build`, `library scan`, `library refurbish`, `library curate`, `library push`.
- `library push` includes explicit phase separation:
  - `library push image`
  - `library push metadata`
  - `library push all`
- Metadata publish in P0 is file-based output (publish bundle), not metadata-server API integration.
- `library build` supports buildx passthrough with guardrails.

### Phase 1: Future Enhancements

- SLSA/provenance generation and verification workflows.
- Metadata server integration for remote metadata publication.
- `library search`.
- Non-repo local directory mode with reduced capabilities.

## Architecture Outlook

Library Tools continues to support layered container practices (OS, runtime, science application stacks), but the primary architectural concern is now workflow composition and artifact quality across user environments.

Future additions (P1+) should preserve the same contract:

- manifest-first metadata semantics,
- policy profile model,
- explicit phase boundaries,
- deterministic, auditable outputs.
