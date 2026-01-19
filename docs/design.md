# CANFAR Container Library Design

## Summary

The CANFAR Container Library defines the architecture and operating model for how container images are curated, built, and published for use with the CANFAR Science Platform. It establishes a shared approach that prioritizes predictability, reproducibility, and security while keeping the system understandable for maintainers and contributors. The CANFAR Container Library is not an application platform; it is the governance layer that standardizes how images are defined and how they evolve over time.

## Design Philosophy

The library favors stability over rapid churn. Updates are intended to be visible, auditable, and time-boxed. A layered model isolates OS, runtime, and science stacks so that changes can be absorbed incrementally. The goal is to reduce downstream breakage while still allowing steady evolution.

Security is treated as a baseline expectation rather than an optional add-on. Sources are pinned, deltas are documented, and metadata supports discoverability, provenance, and supply-chain verification. The library encourages thin layers, minimal divergence from upstream, and a clear path for community contributions.

## Architecture Overview

The library uses a layered container model to separate concerns and reduce churn:

- **Layer 0: OS** - Upstream Ubuntu LTS with digest pinning as the OS foundation to ensure a stable base.
- **Layer 1: Base** - A minimal, explicit toolset that downstream images can rely on. This layer is intentionally thin and reproducible. Built and published on a monthly cadence.
- **Layer 2: Runtime** - Language runtimes (e.g., Python, R, Julia) are provided as shared baselines for science images. Built and published on a monthly cadence.
- **Layer 3: Science** - Curated science stacks built on top of the runtime layers. Maintained by the community and published on project maintainers' cadence.

This layered model is designed to scale to new runtimes and science stacks without changing the governance model.

## Versioning, Support, and Release Cadence

The support policy balances stability with forward motion.

- The **OS Layer** targets the most recent Ubuntu LTS, with transitions between LTS releases being explicitly managed after a 3 month grace period to allow for community testing and feedback.
- The **Base Layers** are rebuilt monthly with refreshed pins and are published using [CalVer](https://calver.org/) tags (for example, `base:2026.1`, `base:2026.2`).
- The **Runtime Images** are rebuilt monthly as well and always track the newest upstream patch release for their declared version (for example, `python:3.14` is the newest 3.14 at build time) on the newest base from the same cadence.
- The **Science Images** are built on the user-provided version and published on the maintainer's cadence. Maintainers are **required** to pin each release to a specific commit via `git.commit`; when building from a non-default ref, the manifest must also set `git.fetch`.

Tags are not invented by the library; they are declared explicitly by maintainers in manifests. This makes ownership and intent clear and ensures that automation publishes only what maintainers approve. We strongly encourage maintainers to use either [semantic versioning](https://semver.org/) or [CalVer](https://calver.org/) for image tags. Image tags live under `build.tags`, while source pinning is expressed via `git.commit` (and `git.fetch` when non-default).

## Manifest-Driven Model

The core unit of definition for a library image is the **manifest**. A manifest is a single, reviewable YAML artifact stored in `manifests/` and validated against the library schema (`library/schema.py`, published as `.spec.json`). It captures ownership, build source, build intent, and downstream identity.

Manifests are the unit of review and the trigger for automation. They allow contributors to keep Dockerfiles in their own repositories while still participating in a shared build pipeline and policy framework.

## Security, Reproducibility, and Supply Chain

The library enforces reproducibility through pinned sources and explicit dependency tracking through continuous integration automation. For example, the current base image implementation uses digest-pinned upstream images and Renovate annotations to make changes auditable over time.

Provenance and metadata are considered first-class outputs. Builds automatically produce attestations, cosign signatures, software bill of materials (SBOM), and metadata suitable for downstream discovery and verification.

## CI/CD and Delivery Model

Automation is manifest-driven: schema validation, build/test, and publishing are triggered by manifest updates. Multi-architecture builds are a baseline expectation, with support expanding as needed.

Promotion is treated as an explicit lifecycle step, for example promoting from `library/base:2026.1` to `library/base:2026.2`. The architecture requires promotion to be deterministic and auditable, with the details of replication, rollback, and credential management captured in follow-on decisions.

## Governance, Lifecycle, and Open Questions

The library is intended to evolve into a structured community workflow with clear onboarding, maintainership, and lifecycle states (proposal, incubation, official, retired). CODEOWNERS, review policies, and contribution checklists enforce consistency without centralizing all image ownership.

Open questions to be resolved via ADRs or targeted design addenda:

- Service levels and deprecation policy for curated science images.
- Canonical platform naming across schema and manifests.

## Changelog

- Reframed "build definitions" and "image recipes" as **manifests**.
- Updated paths and sources of truth (manifests in `manifests/`, schema in `library/schema.py`).
- Aligned architecture language with current implementation details (digest pinning, Renovate annotations, pinned packages).
- Clarified versioning rules: monthly CalVer base tags, runtimes track upstream patches, science images follow user versions, and source pinning uses `git.commit` (plus `git.fetch` when needed).
- Documented current open questions for follow-on decisions.
