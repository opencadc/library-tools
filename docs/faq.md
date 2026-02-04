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
- `library push all`

## Is this workflow opinionated or configurable?

Both. The workflow is opinionated by default, but policy is configurable.

- Built-in profiles: `baseline`, `strict`, `expert`.
- Tool-level overrides are supported for backends like hadolint, trivy, and refurbish integrations.
- CLI flags can override profile behavior for one-off runs.

## Do I have to add my Dockerfile to this repository to have it built?

No. The manifest points to the source repository and commit you want to build.

## Where can I run Library Tools?

Current priority support is:

- Local repository workflows.
- Git-based CI workflows.

Non-repo local directory workflows are planned for a later phase.

## How is metadata handled between manifest and Dockerfile?

The manifest is canonical. During `library curate`, metadata can be explicitly imported from Dockerfile/image outputs and surfaced as patch suggestions, but canonical values are not silently replaced.

## How are library images used downstream?

When using CANFAR clients, `library` can be used as the default image namespace. For example, to create a new session using `images.canfar.net/library/astroml:latest`, you can run:

```bash
canfar create notebook astroml
```

```python
from canfar.sessions import AsyncSession

async with AsyncSession() as session:
    await session.create(kind="notebook", image="astroml")
```

The clients will automatically expand the shorthand to the fully qualified image name since `images.canfar.net` is the default image registry, `library` is the default image namespace, and `latest` is the default image tag.

## How do I request a new image be added to the library?

The easiest way to request a new image be added to the library is to [open a new issue](https://github.com/opencadc/canfar-library/issues/new/choose) in this repository. Please select the "Request New Image" template and fill out the form. We will review your request and get back to you as soon as possible.

## How are library images built?

The library images are:

- Built in the GitHub Actions infrastructure to ensure consistent, secure, and reproducible builds.
- Based on a manifest that describes the image's source, build configuration, metadata, and other information. The manifest is written in YAML and is validated against the [Library's JSON schema](https://github.com/opencadc/canfar-library/blob/main/.spec.json) to ensure correctness.
- Built using the [Docker Buildx](https://docs.docker.com/buildx/working-with-buildx/) tool triggered by changes to the manifest in the repository.

## Where are container image best practices documented?

See [Container Image Best Practices](best-practices/container-images.md).

## Does the library only contain astronomy software?

No, while the majority of the images in the library are astronomy software, we are open to adding any software that is of interest to the astronomy community. That said, we do have a few requirements for images to be added to the library, which are evaluated on a case-by-case basis.

## How do I contribute to the library?

We welcome contributions from the community! Please refer to the [CONTRIBUTING.md](https://github.com/opencadc/canfar-library/blob/main/CONTRIBUTING.md) file for more information on how to contribute.
