# Library Tools Design

## Summary

Library Tools are a community-facing workflow of best practices, recommendations and tooling that helps scientists and developers produce and discover high-quality containerized research software. The project focuses on reducing operational complexity for users: instead of each team independently learning container best practices, security posture, reproducibility techniques, and metadata publishing conventions, the tooling provides a guided, opinionated path with configurable policy controls.

The design target is a single workflow that works equally well in any local development environment and CI environments across multiple providers while preserving enough flexibility for power users to tune behavior when needed.

## Problem Statement

Why do we need this project?

1. User contributed containers represent >75% of images.
2. While Coral Team maintains a set of best practices and base container images, there is no easy way for users to follow these best practices when authoring their own containers.
3. Coral Team cannot scale to provide guidance and support to the entire community all the time.
4. When working with private repositories, users will need to build and publish their own containers.
5. There is no easy way to search and discover container images and metadata. Currently, you have to label the container with keywords on Harbor Container Registry.

We need a solution that:

- Works for both local development and CI/CD and across different CI providers, e.g. GitHub Actions, GitLab Pipelines, etc.
- Is easy to use for scientists but still supports advanced users who need stronger policy control and automation-friendly outputs.
- We need to curate metadata in a way that is machine-readable and supports discovery.

## Intent

Library Tools exists to make high-quality container delivery the default for research software:

- Author and maintain container build definitions with a human-friendly manifest.
- Run best-practice linting and vulnerability scanning with actionable output.
- Modernize dependency baselines with dedicated refurbishing suggestions.
- Build container images with reproducible, auditable provenance.
- Curate metadata artifacts into machine-ingestible bundles.
- Publish image and metadata artifacts in explicit, auditable phases.
- Search and discover metadata from remote servers.

## Principles

1. **Scientist-first defaults**: workflows must be simple, explainable, and safe by default.
2. **Manifest as contract**: manifest data is canonical for build and metadata intent.
3. **Opinionated, not rigid**: built-in policy profiles ship with override paths.
4. **Deterministic outputs**: produce structured artifacts suitable for automated parsing.

## Manifest-Driven Contract

The manifest is the core system contract and source of truth.

- It is human-editable YAML backed by JSON Schema for validation.
- It is machine-actionable for CLI and CI orchestration.
- It defines canonical metadata and tools used for build labeling and curated outputs.
- It is always named as `{name}.manifest.yaml`.

Metadata precedence is explicit:

- Manifest metadata is canonical, i.e. the source of truth.
- Metadata from Dockerfiles and Container Images metadata may be imported during curation only when explicitly requested.
- Imported metadata is surfaced as suggestions/patches to the manifest, not silent source-of-truth changes.

## Opinionated Workflow with Configurable Policy

The default workflow is intentionally opinionated but policy behavior is configurable.

Default Workflow: `init -> lint -> build -> scan -> refurbish -> curate -> push -> search`

Built-in policy profiles:

- `baseline`: scientist-friendly defaults with high-signal checks.
- `strict`: CI/release profile with stronger policy enforcement.
- `expert`: minimal defaults for advanced users.