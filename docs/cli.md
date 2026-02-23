# CLI Tooling

The `library` CLI provides a manifest-driven workflow for building and publishing high-quality containerized research software.

All commands are available through the `library` entrypoint:

```bash
library --help
```

## Command Workflow

For `lint`, `scan`, and `refurbish`, `--manifest` defaults to
`./.library.manifest.yaml`. The file must exist and be readable.

### `init`

Create a manifest that describes software, build intent, and metadata intent.

```bash
library init
library init --output manifests/my-image.yaml
```

### `lint`

Lint Dockerfile and manifest configuration against policy defaults or selected profile.

```bash
library lint
library lint --manifest manifests/my-image.yaml
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
library scan images.canfar.net/library/my-image:1.0 --manifest manifests/my-image.yaml
```

### `refurbish`

Modernize Dockerfile dependencies and emit structured update results.

```bash
library refurbish
library refurbish --manifest manifests/my-image.yaml
library refurbish --manifest manifests/my-image.yaml --json
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

- `default` (scientist-friendly defaults)
- `strict` (CI/release policy)
- `expert` (power-user minimal defaults)

Tool backends (for example hadolint, trivy, and refurbish integrations) can be overridden with user-supplied configuration.

Default/override behavior:

- Recommended defaults are implemented in `library/tools/defaults.py`.
- `library init` and `Schema.save()` materialize defaults into YAML.
- Runtime commands require a fully materialized manifest on disk.
- `config.tools` and `config.cli` are used directly as provided (no deep merge).
- The canonical contract in `library/schema.py` owns schema validation, invariant
  checks, and YAML load/save helpers.

## Roadmap Notes

- `library search` is planned for P1.
- SLSA/provenance workflows and remote metadata server integration are planned for P1.
