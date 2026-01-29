# CLI Tooling

The `library` CLI provides commands for validating manifests, linting Dockerfiles, and running Renovate in a containerized workflow.

All commands are available through the `library` entrypoint:

```bash
library --help
```

## `validate`

Validate a manifest against the Pydantic schema in `library/schema.py`.

```sh
library validate manifests/example.yml
```

## `lint`

Lint a Dockerfile from a manifest or a local Dockerfile.

```bash
library lint manifests/example.yml
library lint --dockerfile images/python/Dockerfile
```

## `renovate`

Renovate a Dockerfile from a manifest or a local Dockerfile.

```bash
library renovate manifests/example.yml
library renovate --dockerfile images/python/Dockerfile
```

## Future Commands (TBD)

```bash
library build manifests/example.yml   # build a manifest locally
library build --dockerfile images/python/Dockerfile
```

```bash
library update manifests/python.yaml  # update a manifest to latest commit hash
library publish manifests/python.yaml # create a pull request with the changes to canfar-library
```
