# Manifest Build System

## Executive Summary

The CANFAR Container Library uses a manifest-driven workflow to curate, build, and publish container images for scientific research. This technical design describes a continuous integration driven build and security system that validates upstream Dockerfiles when manifests change, enforces container best practices, and blocks PRs with critical or high vulnerabilities. The system integrates multiple vulnerability sources (Trivy, OSV, CISA KEV), supports optional image tests defined in manifests, and uses timeline-based escalation with security team oversight.

## System Architecture

### High-Level Flow

1. A user curated pull request updates a manifest in `manifests/`.
2. CI fetches the upstream Dockerfile from the referenced in the manifest with the following required fields to retrieve the Dockerfile:
    - `git.repo`: Git repository URL.
    - `git.fetch`: Git fetch reference.
    - `git.commit`: SHA commit hash to build.
    - `build.path`: Directory containing the Dockerfile.
    - `build.dockerfile`: Dockerfile name.
3. CI runs `hadolint` against the Dockerfile to enforce best practices checks on the Dockerfile.
4. CI runs `renovate` to ensure the latest dependencies are used and pinned to specific versions in the Dockerfile.
5. CI builds the image from the Dockerfile.
6. CI runs vulnerability scanning on the image.
7. CI runs optional `build.test` commands defined in the manifest.
8. CI posts a detailed build report as a PR comment, tagging maintainers.
9. Critical / high vulnerabilities block the PR until resolved.
10. If a PR is not resolved within 4 weeks, it will be closed and marked as stale.
11. Once the PR is merged:

    - CI will build the image for all the `build.platforms` and push with all the tags defined in `build.tags`.
    - CI will generate provenance information about the build and image contents, including SBOMs, attestations, and metadata.
    - CI will will sign the image using [cosign](https://github.com/sigstore/cosign).
    - CI will push the image to container registry.

### PR Escalation Timeline

- If a PR does not pass the CI checks, it will be blocked with a tagging the maintainers listed in the manifest.
- Blocked PRs are tagged with the label - `build:blocked`.
- If a blocked PR is not resolved within 4 weeks, it will be closed and marked as stale.

The security team (@canfar/security) provides oversight only; maintainers remain responsible for remediation.

### Core Components

- **Manifest**: Manifest is written in YAML and validated against the [Library's JSON schema](https://github.com/opencadc/canfar-library/blob/main/.spec.json).
- **Hadolint Configuration**: Dockerfile linting tool to enforce best practices, e.g. `--no-install-recommends`, `RUN --mount=type=cache` etc.
- **Renovate Configuration**: Defines update cadence, release age rules, datasource policies, and digest pinning.
- **Security Scanners**: `Trivy` for OS packages, `OSV` & `Grype` for language packages, and `CISA KEV` for exploited vulnerability prioritization.
- **Provenance System**: Attestations are generated for each image build, including SBOMs, provenance, and metadata and signed using [cosign](https://github.com/sigstore/cosign).
- **Notification System**: Posts PR comments with details and tags maintainers; escalates to `@canfar/security` after two weeks.

## Hadolint Integration

Hadolint is run against the Dockerfile referenced in the manifest to enforce best practices. The CI will fail if the Dockerfile does not pass hadolint.

The Hadolint configuration is defined in the [`.hadolint.yaml`](https://github.com/opencadc/canfar-library/blob/main/.hadolint.yaml) file in the root of the repository. The configuration is based on the [dockerfile best practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/) and the [hadolint documentation](https://github.com/hadolint/hadolint/wiki). These checks include but are not limited to:

    - Digest-pinned upstream OS layer images.
    - Use of `--no-install-recommends` for apt packages.
    - Cleanup of package lists in the same layer as install.
    - Minimized layers and multi-stage build usage where applicable.
    - Renovate annotations for dependency tracking.

## Renovate Bot Integration

Renovate is triggered by changes to manifests in the `manifests/` directory. Alternatively, it can be triggered manually by commenting `/run renovate` in a PR.

- **Update Cadence**: Monthly on the 1st of each month at 03:14 UTC.
- **Rate limits**: 5 PRs per hour and 10 concurrent PRs.
- **Datasource Rules**: Separate settings per datasource for extensibility.
- **Digest pinning**: Always on for Docker images.

The renovate configuration is defined in the [renovate.json5](https://github.com/opencadc/canfar-library/blob/main/renovate.json5) file in the root of the repository.

### Responsibilities

- Update pinned dependencies for upstream images and tagged dependencies in dockerfiles.
- Enforce digest pinning for reproducible builds.
- Ensure minimum release ages per update type:
  - Patch: 1 day
  - Minor: 7 days
  - Major: 30 days
- Generate structured upgrade metadata for reporting.

## Security Scanning Architecture

### Vulnerability Sources

1. **Trivy** for OS packages and upstream OS layer images, using vendor advisories.
2. **Grype / OSV** for language ecosystem dependencies (Python, JavaScript, Go, etc.).
3. **CISA KEV** for prioritization of actively exploited vulnerabilities.

### Severity and Response

| Severity | CVSS Range | Escalation To | PR Action |
| --- | --- | --- | --- |
| Critical | 9.0–10.0 | Maintainers | Blocked PR |
| High | 7.0–8.9 | Maintainers | Blocked PR |
| Medium | 4.0–6.9 | Maintainers | PR Warning |
| Low | 0.1–3.9 | Maintainers | PR Warning |

## Test Command Integration

If `build.test` is present in a manifest, CI will run the following command:

    ```bash
    docker run --rm <built-image> <build.test>
    ```

If the test fails, the PR is blocked. If no test is provided, CI proceeds with warning informing the maintainer to add a test command.