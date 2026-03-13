# Library Tools vision

Library Tools should make container quality and publication simple for
scientists and robust for automation. This document defines the target user
experience and system behavior for a three-command workflow:

- `library init`
- `library check`
- `library publish <TAG>`

The goal is to keep the user surface small while still supporting strong
security checks, dependency modernization, metadata quality, and publication
consistency.

> **Note:** This is a preview feature currently under active development.

## Why this vision exists

Today, users often need to learn many separate systems to release a container:
lint tools, scanners, dependency tools, metadata workflows, and publishing
steps. That complexity slows adoption and creates release mistakes.

Library Tools should remove that burden by becoming a single orchestration
layer. Users run one check command before merge and one publish command at
release time. The command internals can evolve without changing that simple
interface.

## Product principles

This vision is built on a few non-negotiable principles. They keep the product
easy to use and stable at scale.

- Keep user workflow to three top-level commands.
- Keep release authority tag-driven with `library publish <TAG>`.
- Keep the manifest as canonical build and metadata intent.
- Stay provider agnostic for CI systems and PR or MR workflows.
- Integrate existing tools when useful instead of replacing them.
- Emit deterministic artifacts for humans and machines.
- Return actionable failures with concrete next-step commands.

## Primary user workflow

The intended user mental model is intentionally small.

1. Run `library init` once to create or update manifest intent.
2. Run `library check` locally or in CI for quality gates.
3. Run `library publish <TAG>` when releasing.

This model keeps onboarding simple for scientific users and still supports
advanced policy and automation behavior behind the scenes.

## `library check` contract

`library check` is the top-level all-encompassing check command. It wraps and
orchestrates checks that exist today and checks we add in the future.

### Supported targets

By default, `library check` runs all enabled checks.

- `library check` or `library check all`: run all checks.
- `library check security`: run security checks, centered on scan.
- `library check deps`: run dependency checks, centered on refurbish.
- `library check dependencies`: alias of `deps`.
- `library check style`: run style and policy checks, centered on lint.

### Execution model

The check command is recipe-driven. A recipe defines which tools run and how
findings are aggregated. Built-in targets map to built-in recipes. Future
recipes can be added without changing the top-level command surface.

Recommended runtime modes:

- `auto`: ingest external artifacts if present and run missing checks.
- `internal`: run only library-managed checks.
- `ingest`: only parse existing artifacts and do not execute checks.

### Reporting contract

`library check` must always emit:

- `check.json` for machine consumers.
- `pr-summary.md` for provider-neutral PR or MR feedback.

`library check` should emit:

- `check.sarif` when active checks support SARIF output.

Exit codes must be deterministic:

- `0`: pass.
- `1`: policy failure from findings.
- `2`: invalid manifest or configuration.
- `3`: runtime or tool execution failure.

## `library publish <TAG>` contract

`library publish <TAG>` is the full release train command. It can run in CI or
locally. The user provides a release tag, and the command executes the entire
release workflow with consistency checks.

### Release authority and invariants

The `<TAG>` argument is the only release authority.

`library publish <TAG>` resolves:

- release version from tag.
- revision from `git rev-parse HEAD`.
- created timestamp in UTC.

It must fail if release intent is inconsistent, for example:

- tag-derived version does not match manifest discovery version.
- working tree is dirty for a non-dry-run release.
- required build tags cannot be resolved.

### Publish stage model

Recommended stage order:

1. Validate manifest and environment.
2. Resolve release context from tag and git.
3. Run `library check` with strict profile by default.
4. Run curate stage for release metadata bundle.
5. Run build stage for container artifacts.
6. Run push stage for image artifacts.
7. Run metadata push stage.
8. Emit final publish summaries and status.

### Publish outputs

`library publish <TAG>` must emit:

- `publish.json`
- `publish.md`
- metadata bundle reference and path

## Ecosystem compatibility

Library Tools must coexist with established ecosystem tooling. The project wins
adoption when users can keep their current tools and still use a unified Library
workflow.

### Dependency tooling

For dependency workflows, Library should ingest external dependency artifacts if
they already exist, or run internal refurbish checks when they do not. Both
paths must normalize to the same findings model and summary format.

### Release tooling

Users may use any release automation tool that creates tags. Library does not
need to own external release semantics. Once a tag exists, `library publish
<TAG>` performs a consistent release train.

### Lint and scan tooling

Lint and scan execution can continue to use proven tooling, but reporting must
improve. The user must receive fewer duplicate findings, clearer severity, and
explicit remediation commands.

## Better reporting goals

Improving report quality is a primary requirement, not a cosmetic enhancement.
Users need fast understanding and clear next actions.

Every check summary should include:

- overall status
- top findings by severity
- the exact file or image context
- concise remediation guidance
- links or paths to full machine-readable artifacts

Every publish summary should include:

- release tag, resolved version, and revision
- stage-by-stage pass or fail status
- pushed artifact references
- metadata publication status
- explicit retry guidance if a stage fails

## Provider-agnostic feedback pattern

Library CLI should remain provider agnostic. It should not require direct
GitHub, GitLab, or other provider API integration in core behavior.

The portable pattern is:

1. `library check` produces `pr-summary.md` and `check.json`.
2. CI uploads these artifacts.
3. A provider-specific wrapper step posts `pr-summary.md` to PR or MR threads.

This keeps the core tool portable and makes platform integration a thin layer.

## Concrete command examples

These examples show the intended day-to-day usage.

### Local usage

```bash
library init
library check
library publish v1.2.3
```

### Targeted checks

```bash
library check security
library check deps
library check dependencies
library check style
```

### Provider-neutral CI check step

```bash
set -euo pipefail
library check --manifest .library.manifest.yaml --output-dir .library/reports/check
cat .library/reports/check/pr-summary.md
```

### Provider-neutral CI publish step

```bash
set -euo pipefail
TAG="${CI_TAG:-v0.0.0}"
library publish "$TAG" --manifest .library.manifest.yaml --output-dir .library/reports/publish
cat .library/reports/publish/publish.md
```

## Adoption strategy

This vision should roll out in phases to reduce migration risk.

1. Ship top-level command surface with stable artifact contracts.
2. Improve lint, scan, and refurbish report quality and consistency.
3. Add artifact ingestors for common external workflows.
4. Publish provider-neutral CI playbooks and wrapper examples.

## Success metrics

Success should be measured with product-level outcomes.

- Time to first successful `library check`.
- Percentage of releases executed through `library publish <TAG>`.
- Rate of version and tag mismatch failures.
- Metadata publish completeness and discovery coverage.
- User-reported clarity of check and publish summaries.

## Risks and mitigations

This model introduces risks that need explicit control.

- Risk: hidden complexity under simple commands.
  - Mitigation: stable command, output, and exit code contracts.
- Risk: duplicate checks in mixed CI ecosystems.
  - Mitigation: clear `auto`, `internal`, and `ingest` behavior.
- Risk: noisy reports reduce trust.
  - Mitigation: deduplicate findings and prioritize remediation-first summaries.
- Risk: ecosystem drift over time.
  - Mitigation: adapter interface plus compatibility tests for ingested artifacts.

## Next steps

To implement this vision, the project should:

1. Add `library check` target routing for `all`, `security`, `deps`,
   `dependencies`, and `style`.
2. Add `library publish <TAG>` as the canonical release train command.
3. Define canonical findings and publish artifact schemas.
4. Upgrade lint, scan, and refurbish reporting quality.
5. Publish CI wrapper examples that consume `pr-summary.md` and `publish.md`.
