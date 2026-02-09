# Library Tools Roadmap

## Timeline and Dependencies

- **Phase 0:** Local development + Git-based CI workflows.
- **Phase 1:** Metadata server delivered by end of Phase 1; upstream publishing capabilities unlocked.
- **Phase 2:** Remote server integration features that depend on Phase 1 delivery.

> **Gate:** Phase 2 starts only after the upstream metadata server is delivered at the end of Phase 1.

## Phase 0: Local Development and CI

### Contexts

- Local repositories.
- Git-based CI/CD (GitHub, GitLab, etc.).

### Commands

- `library init`
- `library lint`
- `library build`
- `library scan`
- `library refurbish`

### Capabilities

- Manifest-canonical metadata model.
- `library build` uses buildx passthrough with guardrails.

### Out of scope

- Metadata server integration.
- Remote discovery/search.
- Non-repo local directory mode.
- `library curate` and `library push`.

## Phase 1: Curate and Push

### New Commands

- `library curate`.
- `library push` phase separation:
  - `library push image`
  - `library push metadata`
  - `library push all`

### New Capabilities

- `library curate` and `library push` are implemented.
- Metadata server integration for publishing curated metadata.

### Improvements

- Expand `library refurbish` to support multiple backends (e.g., `apt`, `pip`).

### Acceptance Criteria

- Metadata server delivered and stable.
- End-to-end publish + search flow validated.

## Phase 2: Remote Server Integration (Post‑Phase 1)

- Improve `library curate` with import/suggestion flow from Dockerfile or image during curation.
- Policy profile management and overrides:
  - `baseline`, `strict`, `expert` + tool-level override support.
  - `library set policy <profile>`
  - `library get policy`
  - `library list policy`
- Provenance workflows:
  - `library search` for discovery.
  - `library attest`
  - `library verify`
- `library push` phase separation additions:
  - `library push attestations`
- Remote metadata workflows:
  - `library pull` (fetch image + metadata)
  - `library diff` (compare local vs remote)
  - `library tag` (tag local image + metadata)
  - `library deprecate` (deprecate image + metadata)
