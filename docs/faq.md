# Frequently Asked Questions

As stewards of the CANFAR Container Library and maintainers of many images in the library, we understand the importance of providing a smooth and efficient experience for users. To that end, we have compiled a list of frequently asked questions and their answers to help you get the most out of the library.

## Audiences

!!! success "Who is this for?"

    - Maintainers of software who want to provide a convenient way for users to discover their software.
    - Follow best practices for auditable, secure, and reproducible software supply-chain.

!!! failure "Who is this not for?"

    - Users who want to run / prototype their software for themselves.

## What do you mean by `Library`?

The CANFAR Container Library is a collection of container images that are built and published under the `library` namespace on the [CANFAR Image Registry](https://images.canfar.net). We use the term "library" to refer to this collection of images, as well as the process and tools for building and maintaining these images in this repository.

When using CANFAR clients to create a new session, `library` is the default image namespace. For example, to create a new session using the `images.canfar.net/library/astroml:latest` image, you can simply run the following shorthand:

```bash
canfar create notebook astroml
```

```python
from canfar.sessions import AsyncSession

async with AsyncSession() as session:
    await session.create(kind="notebook", image="astroml")
```

The clients will automatically expand the shorthand to the fully qualified image name since `images.canfar.net` is the default image registry, `library` is the default image namespace, and `latest` is the default image tag.

## Do I have to add my Dockerfile to this repository to have it built?

No, you do not have to add your Dockerfile to this repository to have it built. See the next question for more details.

## How do I request a new image be added to the library?

The easiest way to request a new image be added to the library is to [open a new issue](https://github.com/opencadc/canfar-library/issues/new/choose) in this repository. Please select the "Request New Image" template and fill out the form. We will review your request and get back to you as soon as possible.

## How are library images built?

The library images are:

- Built in the GitHub Actions infrastructure to ensure consistent, secure, and reproducible builds.
- Based on a manifest that describes the image's source, build configuration, metadata, and other information. The manifest is written in YAML and is validated against the [Library's JSON schema](https://github.com/opencadc/canfar-library/blob/main/.spec.json) to ensure correctness.
- Built using the [Docker Buildx](https://docs.docker.com/buildx/working-with-buildx/) tool triggered by changes to the manifest in the repository.

## Does the library only contain astronomy software?

No, while the majority of the images in the library are astronomy software, we are open to adding any software that is of interest to the astronomy community. That said, we do have a few requirements for images to be added to the library, which are evaluated on a case-by-case basis.

## How do I contribute to the library?

We welcome contributions from the community! Please refer to the [CONTRIBUTING.md](https://github.com/opencadc/canfar-library/blob/main/CONTRIBUTING.md) file for more information on how to contribute.
