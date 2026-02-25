# CLI Tooling

The `library` CLI provides a manifest-driven workflow for building and publishing high-quality containerized research software.

All commands are available through the `library` entrypoint:

```bash
library --help
```

## Command Workflow

For `lint`, `build`, `scan`, and `refurbish`, `--manifest` defaults to
`./.library.manifest.yaml`.

### `init`

Create a manifest that describes software, build intent, and metadata intent.
`init` uses a RichForms interactive form over the canonical `Schema` model in
`library/schema.py`. Internal fields are excluded from prompting with RichForms
metadata (`config`, `metadata.discovery.created`, and
`metadata.discovery.revision`). It writes a runtime-ready manifest that includes
fully materialized tool defaults.

```bash
library init
library init --output manifests/my-image.yaml
```

`--output` defaults to `./.library.manifest.yaml`. If the output file exists,
the CLI prompts before overwrite. If you decline overwrite, the command exits
without changing the file.

### `lint`

Lint Dockerfile and manifest configuration against policy defaults or selected profile.

```bash
library lint
library lint --manifest manifests/my-image.yaml
```

### `build`

Build a container image from manifest intent. Supports buildx passthrough args via `--`.

```bash
library build
library build --manifest manifests/my-image.yaml
library build --manifest manifests/my-image.yaml -- --progress=plain
```

### `scan`

Scan a container image for vulnerabilities.
If you omit IMAGE and a manifest exists, `scan` derives the image reference from
`registry.host`, `registry.project`, `registry.image`, and the first
`build.tags` entry. If IMAGE is provided and no manifest is available, `scan`
uses the built-in default scanner configuration.

```bash
library scan images.canfar.net/library/my-image:1.0
library scan --manifest manifests/my-image.yaml
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
