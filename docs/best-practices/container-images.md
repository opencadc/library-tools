# Best Practices for Container Images

This document captures the best practices used by the CANFAR Container Library and the base image publication workflow.

These practices are intended to reduce operational burden on scientists and developers by providing a consistent, auditable model for building and maintaining container images.

## Design Philosophy

The library favors stability over rapid churn. Updates are intended to be visible, auditable, and time-boxed. A layered model isolates OS, runtime, and science stacks so that changes can be absorbed incrementally. The goal is to reduce downstream breakage while still allowing steady evolution.

Security is treated as a baseline expectation rather than an optional add-on. Sources are pinned, deltas are documented, and metadata supports discoverability, provenance, and supply-chain verification. The library encourages thin layers, minimal divergence from upstream, and a clear path for community contributions.

## Architecture Overview

The library uses a layered container model to separate concerns and reduce churn:

- **Layer 0: OS** - Upstream OS distributions (Ubuntu LTS, Debian, Alpine, etc.) with digest pinning provide the operating system foundation.
- **Layer 1: Runtime** - Language runtimes (e.g., Python, R, Julia) plus shared baseline packages for the community. Built and published on a monthly cadence.
- **Layer 2: Science** - Curated science stacks built on top of the runtime layer. Maintained by the community and published on project maintainers' cadence.

This layered model is designed to scale to new runtimes and science stacks without changing the governance model.

## Versioning, Support, and Release Cadence

The support policy balances stability with forward motion.

- The **OS Layer** tracks the lifecycle of the chosen upstream distribution, with transitions managed after a 3 month grace period to allow for community testing and feedback.
- The **Runtime Images** are rebuilt monthly with refreshed pins and track the newest upstream patch release for their declared version (for example, `python:3.14` is the newest 3.14 at build time).
- The **Science Images** are built on the user-provided version and published on the maintainer's cadence. Maintainers are required to pin each release to a specific commit via a new version update to the manifest.

## Security, Reproducibility, and Supply Chain

The library enforces reproducibility through pinned sources and explicit dependency tracking through continuous integration automation. For example, the current runtime image implementation uses digest-pinned upstream OS layers and Renovate annotations to make changes auditable over time.

Provenance and metadata are considered first-class outputs. Builds automatically produce attestations, cosign signatures, software bill of materials (SBOM), and metadata suitable for downstream discovery and verification.

## CI/CD and Delivery Model

Automation is manifest-driven: schema validation, build/test, and publishing are triggered by manifest updates. Multi-architecture builds are a baseline expectation, with support expanding as needed.

Promotion is treated as an explicit lifecycle step, for example promoting from `library/python:2026.1` to `library/python:2026.2`. The architecture requires promotion to be deterministic and auditable, with the details of replication, rollback, and credential management captured in follow-on decisions.

## Governance, Lifecycle, and Open Questions

The library is intended to evolve into a structured community workflow with clear onboarding, maintainership, and lifecycle states (proposal, incubation, official, retired). CODEOWNERS, review policies, and contribution checklists enforce consistency without centralizing all image ownership.

Open questions to be resolved via ADRs or targeted design addenda:

- Service levels and deprecation policy for curated science images.
- Canonical platform naming across schema and manifests.

## Base Image Publication with Library Tools

These best practices are implemented through the Library Tools workflow and applied to published base images.

In practice:

- The manifest captures canonical build and metadata intent.
- The CLI workflow (`init`, `lint`, `build`, `scan`, `refurbish`, `curate`, `push`) enforces consistent quality controls.
- Curated outputs are designed for both user-facing documentation and machine ingestion.
- Published base images follow layered architecture guidance and auditable release practices.
