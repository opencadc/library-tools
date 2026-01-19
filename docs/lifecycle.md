# Image Lifecycle

Let's walk through the full lifecycle of a library image from start to finish to help you understand how the library works and how you can contribute to it.

## Image Request

To request a new image be added to the library, you need to open a new issue in this repository. Please select the "Request New Image" template and fill out the form. We will review your request and get back to you as soon as possible.
In the request issue, you will be asked to provide the following information:

1. Link to the upstream project (git repository)
2. Upstream maintainer contact information (mapped to manifest `maintainers`)
3. Container details mapped to schema fields (image name, tags, platforms, metadata identifier/project, optional test command)
4. Confirmation that the source is under an [OSI Approved License](https://opensource.org/licenses) and the license name (for example, MIT)
5. Astronomy relevance and community use case
6. Link to the manifest pull request to be reviewed and merged once the request is approved
7. Whether the image is based on an existing runtime layer (for example, `python` or `r`); if not, explain why and note any new runtime request
8. Confirmation that the manifest pull request passes automated integration tests

## Image Manifest

The image manifest is a YAML file that describes the image's source, build configuration, metadata, and other information. The manifest is written in YAML and is validated against the [Library's JSON schema](https://github.com/opencadc/canfar-library/blob/main/.spec.json) to ensure correctness.

```yaml
name: python
maintainers:
  - name: Shiny Brar
    email: shiny.brar@nrc-cnrc.gc.ca
    github: shinybrar
git:
  repo: https://github.com/opencadc/canfar-library
  fetch: refs/heads/main
  commit: 1234567890123456789012345678901234567890
build:
  path: images/python
  dockerfile: Dockerfile
  context: .
  platforms:
    - linux/amd64
    - linux/arm64
  tags:
    - 3.12
  labels:
    org.opencontainers.image.title: "CANFAR Python Runtime"
    org.opencontainers.image.description: "Python runtime for CANFAR Science Platform"
    org.opencontainers.image.vendor: "Canadian Astronomy Data Centre"
    org.opencontainers.image.source: "https://github.com/opencadc/canfar-library"
    org.opencontainers.image.licenses: "AGPL-3.0"
  annotations:
    canfar.image.type: "runtime"
    canfar.image.runtime: "python"
  test: python --version
metadata:
  identifier: canfar-python
  project: canfar
```

## How are library images updated?

1. A change gets committed to the relevant image source Git repository, for example a new version release or a bug fix.
2. A PR to the relevant image manifest (`manifests/XXXX.yaml`) is opened in this repository to update relevant fields, typically `git.commit` (and `git.fetch` when non-default), `build.tags`, and `metadata` fields, etc.
3. The library automation detects the change and updates the PR with a full diff of the actual `Dockerfile` changes upstream.
4. The library automation runs a basic build test on `linux/amd64` to ensure the image builds successfully and executes `build.test` if provided.
5. Once the PR is approved and merged, the library automation builds the image for all the platforms specified in the manifest.
6. The build process generates provenance information about the build and image contents.
7. The image is pushed to the `images.canfar.net/library/<image>:<tag>` and signed using [cosign](https://github.com/sigstore/cosign).
8. The image is available for use downstream.
