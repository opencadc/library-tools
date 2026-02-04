# CLI Tooling

The `library` CLI provides a manifest-driven workflow for building and publishing high-quality containerized research software.

All commands are available through the `library` entrypoint:

```bash
library --help
```

## Command Workflow

### `init`

Create a manifest that describes software, build intent, and metadata intent.

```bash
library init
library init --output manifests/my-image.yaml
```

### `lint`

Lint Dockerfile and manifest configuration against policy defaults or selected profile.

```bash
library lint manifests/my-image.yaml
library lint manifests/my-image.yaml --profile strict
```

### `build`

Build a container image from manifest intent. Supports buildx passthrough args via `--`.

```bash
library build manifests/my-image.yaml
library build manifests/my-image.yaml -- --progress=plain
```

### `scan`

Scan a container image for vulnerabilities.

```bash
library scan images.canfar.net/library/my-image:1.0
```

### `refurbish`

Modernize Dockerfile dependencies and emit structured update results.

```bash
library refurbish manifests/my-image.yaml
```

### `curate`

Assemble manifest, lint, scan, and build outputs into a coherent metadata bundle.

```bash
library curate manifests/my-image.yaml --output-dir ./artifacts
```

`curate` supports explicit metadata inspection/import from Dockerfile/image inputs, while keeping manifest values canonical.

### `push`

Publish is phase-separated for reliability and operational clarity.

```bash
library push image manifests/my-image.yaml
library push metadata manifests/my-image.yaml --output-dir ./publish
library push all manifests/my-image.yaml
```

- `push image`: publish container image artifacts.
- `push metadata`: emit metadata publish bundles (P0 file-based output).
- `push all`: run both phases in sequence.

## Policy Profiles and Overrides

Built-in policy profiles:

- `baseline` (scientist-friendly defaults)
- `strict` (CI/release policy)
- `expert` (power-user minimal baseline)

Tool backends (for example hadolint, trivy, and refurbish integrations) can be overridden with user-supplied configuration.

## Roadmap Notes

- `library search` is planned for P1.
- SLSA/provenance workflows and remote metadata server integration are planned for P1.
