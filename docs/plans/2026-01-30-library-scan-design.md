# Library Scan (Trivy) Design

## Goal
Add a new CLI command `library scan DOCKERIMAGE` that pulls a container image (if missing locally) and runs Trivy in a container to report CVEs as JSON, filtered to HIGH and CRITICAL severities. The command should be deterministic, easy to parse, and suitable for CI.

## User Experience
- Command: `library scan ghcr.io/org/image:tag`
- Behavior:
  - If the image is not present locally, pull it first.
  - Run Trivy via Docker (`docker.io/aquasec/trivy:latest`).
  - Emit JSON to stdout (no extra formatting).
  - Exit non-zero when HIGH/CRITICAL vulnerabilities are found (Trivy `--exit-code 1`).
  - Allow a configurable Trivy cache directory for DB persistence.

## Implementation Overview
- New module: `library/cli/trivy.py` with a `run(image, cache_dir, verbose) -> int` helper.
- New config: `library/.trivy.yaml` defining output format, severity threshold, and CVE-only scanning.
- CLI wiring: add `scan` command in `library/cli/main.py`, export in `library/cli/__init__.py`, and a constant `TRIVY_CONFIG_PATH` in `library/__init__.py`.

## Trivy Invocation Details
- Ensure the target image exists locally:
  - Try `docker image inspect <image>`; if that fails, `docker pull <image>`.
- Pull Trivy image on each run (aligns with hadolint/renovate approach).
- Run Trivy in a container with Docker socket access:
  - Mount `/var/run/docker.sock` for local image scanning.
  - Mount the cache directory to `/trivy-cache` and set `TRIVY_CACHE_DIR=/trivy-cache`.
  - Mount a temp workspace with `Dockerfile`-style config handling and pass `--config /work/.trivy.yaml`.
  - Trivy args: `image --format json --severity HIGH,CRITICAL --exit-code 1 --quiet --no-progress <image>`.

## Trivy Config Principles
- CVE-only scanning (vulnerability scanner only).
- JSON output for machine consumption.
- Report HIGH and CRITICAL severities.
- Keep unfixed vulnerabilities visible by default (security-first signal).

## Error Handling
- If Trivy fails (non-zero exit code) due to scan errors, surface the exit code as-is.
- If Trivy finds HIGH/CRITICAL CVEs, exit non-zero (CI-friendly).
- Always emit JSON to stdout when Trivy produces output.

## Security-First Notes
- Prefer digest-pinned images in manifests (already handled by renovate policy).
- Keep Trivy DB cache persistent to avoid stale DB errors and reduce runtime.
- Treat HIGH/CRITICAL as blockers in CI; consider adding an allowlist ignorefile for vetted exceptions.
