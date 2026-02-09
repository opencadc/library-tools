# Frequently Asked Questions

CANFAR Library Tools provides a guided workflow for building and publishing high-quality containerized research software. This FAQ answers common questions about the workflow, scope, and expected outputs.

## Audiences

!!! success "Who is this for?"

    - Scientists who want practical defaults for building secure, reproducible containers.
    - Developers and maintainers who need consistent CLI + CI workflows.
    - Teams publishing reusable research software metadata and container artifacts.

!!! failure "Who is this not for?"

    - Users looking for a lightweight container runtime helper only.
    - Workflows that do not want an opinionated manifest-driven contract.

## What do you mean by `Library Tools`?

CANFAR Library Tools is the community-facing tooling and workflow for producing containerized research software. It includes manifest authoring, linting, vulnerability scanning, dependency modernization, metadata curation, and phase-separated publishing.

The workflow also supports publication of curated base images in the CANFAR `library` namespace on the [CANFAR Image Registry](https://images.canfar.net).

## What commands are in the workflow?

The default workflow is:

- `library init`
- `library lint`
- `library build`
- `library scan`
- `library refurbish`
- `library curate`
- `library push`

`library push` is phase-separated:

- `library push image`
- `library push metadata`
- `library push attestations`
- `library push all`

## Is this workflow opinionated or configurable?

Both. The workflow is opinionated by default, but policy is configurable.

- Built-in profiles: `baseline`, `strict`, `expert`.
- Tool-level overrides are supported for backends like hadolint, trivy, and refurbish integrations.
- CLI flags can override profile behavior for one-off runs.

## Where can I run Library Tools?

Current priority support is:

- Local repository workflows.
- Git-based CI workflows.

Non-repo local directory workflows are planned for a later phase.

## How is metadata handled between manifest and Dockerfile?

The manifest is canonical. During `library curate`, metadata can be explicitly imported from Dockerfile/image outputs and surfaced as patch suggestions, but canonical values are not silently replaced.

Metadata is also extracted from the image build process and added to the manifest. For example, the `LABEL` instructions in the Dockerfile are extracted and added to the manifest.

## How are library images built?

The library images are build using the [Docker Buildx](https://docs.docker.com/buildx/working-with-buildx/) tool.

However, it is strongly recommended to use the GitHub Actions workflow to build images. Here are some of the reasons:

- The GitHub Actions infrastructure to ensure consistent, secure, and reproducible builds.
- The manifest is written in YAML and is validated against the [Library's JSON schema](https://github.com/opencadc/canfar-library/blob/main/.spec.json) to ensure correctness.
- SLSA provenance is only generated when dedicated SLSA builders are used. GitHub Actions is one of the supported builders, along with Google Cloud Build, CircleCI, and GitLab CI/CD etc.

## Where are container image best practices documented?

See [Container Image Best Practices](best-practices/container-images.md).

## Are library tools only for astronomy software?

No, while the library was originally created for the astronomy community, it is not limited to astronomy software. However, the library is hosted under the [Canadian Astronomy Data Centre (CADC)](https://www.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/en/) and the [CANFAR Science Platform](https://www.opencadc.org/canfar/latest/) is focused on astronomy research.

## How do I contribute to the library?

We welcome contributions from the community! Please refer to the [CONTRIBUTING.md](https://github.com/opencadc/canfar-library/blob/main/CONTRIBUTING.md) file for more information on how to contribute.
