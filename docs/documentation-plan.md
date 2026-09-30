# TRACE documentation consolidation plan

This file is the temporary migration plan for reducing TRACE documentation to the minimum needed for the Developer Preview release. It defines the target structure and the disposition of the current documentation set. It should be removed once the consolidation is complete.

## Target release documentation

```text
README.md
CONTRIBUTING.md
LICENSE

docs/
├── getting-started.md
├── logging-with-trace.md
├── operations.md
└── design.md
```

The release documentation should support three reader needs:

1. **Adoption** — understand what TRACE is and try it quickly.
2. **Usage** — instrument statistical programs consistently.
3. **Contribution** — understand development workflow and the current architecture.

Historical design reasoning does not need to remain as active documentation because Git history preserves it.

## Document ownership

| Document | Owns |
|---|---|
| `README.md` | Product definition, value proposition, quick example, installation, release status, links to user docs |
| `docs/getting-started.md` | First complete TRACE workflow from installation to reading a generated log |
| `docs/logging-with-trace.md` | General usage model: `Trace`, lifecycle, steps, console/file logging, structured events, program-level provenance, review/QC boundaries, host-environment guidance |
| `docs/operations.md` | The eleven statistical operations, selection guidance, boundaries, examples, lifecycle operation notes |
| `CONTRIBUTING.md` | Development setup, contribution workflow, testing, API-change expectations, documentation rules |
| `docs/design.md` | Current architecture and design invariants only |
| `LICENSE` | Project license |

Each concept should have one authoritative home. Other documents should link rather than repeat the explanation.

## Current documentation disposition

### Root documents

| Current document | Decision | Destination / action |
|---|---|---|
| `README.md` | **KEEP** | Remains the repository front door; simplify during onboarding sprint |
| `CONTRIBUTING.md` | **KEEP** | Absorb contributor documentation rules and update paths |
| `LICENSE` | **KEEP** | No change |
| `CODE_OF_CONDUCT.md` | **REMOVE** | Not required for the initial TRACE release |
| `CHANGELOG.md` | **REVIEW FOR REMOVAL** | Remove for Developer Preview if release notes are maintained through GitHub Releases |

### `docs/api/`

| Current document | Decision | Destination / action |
|---|---|---|
| `docs/api/README.md` | **REMOVE AFTER MERGE** | Keep only any usage details not already covered by `logging-with-trace.md` or `operations.md`; formal API docs are deferred |

### `docs/concepts/`

| Current document | Decision | Destination / action |
|---|---|---|
| `docs/concepts/README.md` | **REMOVE** | Directory/index no longer needed |
| `docs/concepts/structured-events.md` | **MERGE** | User-relevant explanation → `docs/logging-with-trace.md`; architecture detail → `docs/design.md` |
| `docs/concepts/provenance.md` | **MERGE** | User behavior → `docs/logging-with-trace.md`; internal architecture/invariants → `docs/design.md` |

### `docs/contributing/`

| Current document | Decision | Destination / action |
|---|---|---|
| `docs/contributing/documentation-guidelines.md` | **MERGE** | Concise documentation rules → `CONTRIBUTING.md` |

### `docs/framework/`

| Current document | Decision | Destination / action |
|---|---|---|
| `docs/framework/README.md` | **REMOVE** | Framework index no longer needed |
| `docs/framework/core-operations-v0.1.md` | **MERGE** | Preserve only current operation semantics/boundaries not already in `docs/operations.md` |
| `docs/framework/reviewer-guide.md` | **MERGE** | Practical log-reading and review/QC boundaries → `docs/logging-with-trace.md` |

### `docs/guides/`

| Current document | Decision | Destination / action |
|---|---|---|
| `docs/guides/README.md` | **REMOVE** | Guide index not needed in flat structure |
| `docs/guides/getting-started.md` | **KEEP / MOVE** | Becomes `docs/getting-started.md` |
| `docs/guides/operations.md` | **KEEP / MOVE** | Becomes `docs/operations.md` |
| `docs/guides/quarto.md` | **MERGE** | Keep only concise host-environment guidance in `docs/logging-with-trace.md` |

### `docs/design/`

The design directory currently preserves development phases and historical reasoning. Only current-state architecture and invariants should survive in active documentation.

| Current document | Decision | Destination / action |
|---|---|---|
| `docs/design/README.md` | **REPLACE** | Replaced by the single `docs/design.md` |
| `docs/design/api-design-plan.md` | **REMOVE** | Historical planning; Git history is sufficient |
| `docs/design/comparative-review.md` | **REMOVE** | Historical research |
| `docs/design/configuration.md` | **MERGE SELECTIVELY** | Only current configuration/public-boundary invariants → `docs/design.md` |
| `docs/design/domain-model.md` | **MERGE SELECTIVELY** | Current event/domain model → `docs/design.md` |
| `docs/design/generic-structured-logging.md` | **REMOVE / MERGE SELECTIVELY** | Preserve only current architectural conclusions if not covered elsewhere |
| `docs/design/lifecycle.md` | **MERGE SELECTIVELY** | Current lifecycle invariants → `docs/design.md`; user behavior → `docs/logging-with-trace.md` |
| `docs/design/minimum-programmer-experience.md` | **REMOVE** | Historical phase document |
| `docs/design/object-vs-operation.md` | **REMOVE / MERGE SELECTIVELY** | Preserve only current operation-model invariant if needed in `docs/design.md` |
| `docs/design/provenance.md` | **MERGE SELECTIVELY** | Current provenance architecture/invariants → `docs/design.md` |
| `docs/design/reference-prototype-findings.md` | **REMOVE** | Historical findings |
| `docs/design/reference-prototype.md` | **REMOVE** | Historical prototype contract |
| `docs/design/reviewer-experience-findings.md` | **REMOVE** | Historical findings |
| `docs/design/reviewer-experience.md` | **REMOVE / MERGE SELECTIVELY** | Preserve only current review boundary if not already captured in `logging-with-trace.md` |
| `docs/design/step-level-instrumentation.md` | **MERGE SELECTIVELY** | Current step invariants → `docs/design.md`; usage → `docs/logging-with-trace.md` |
| `docs/design/tier-1-api.md` | **REMOVE / MERGE SELECTIVELY** | Current public/internal boundary → `docs/design.md`; formal API spec deferred |

## Consolidation rules

- Preserve **current behavior**, not the chronology of how it was designed.
- Do not retain phase numbers, sprint history, prototype findings, or rejected alternatives as release documentation.
- Keep examples statistical-programming focused and backend-independent where possible.
- Keep API signatures in docstrings/code unless a user guide needs them for an example.
- Do not duplicate operation definitions between `logging-with-trace.md`, `operations.md`, and `design.md`.
- `operations.md` is authoritative for operation meaning.
- `logging-with-trace.md` is authoritative for normal runtime usage.
- `design.md` is authoritative for architecture and maintainer invariants.

## Migration order

1. Simplify `README.md` and `getting-started.md`.
2. Create `logging-with-trace.md` and merge runtime/concept/reviewer material.
3. Finalize `operations.md` as the sole operation reference.
4. Create the single current-state `design.md`.
5. Consolidate contributor guidance into `CONTRIBUTING.md`.
6. Remove obsolete documentation and old directory structure.
7. Run a repository-wide link and terminology cleanup.
8. Remove this migration plan.

## Acceptance criteria for the final state

- A first-time user needs only `README.md`, `getting-started.md`, `logging-with-trace.md`, and `operations.md`.
- A contributor needs only `CONTRIBUTING.md` plus `docs/design.md` when architecture context is required.
- No active documentation exists solely to preserve design history.
- No user-facing content depends on `docs/api/`, `docs/concepts/`, `docs/framework/`, `docs/contributing/`, or the old `docs/design/` directory.
- No dead links or references to removed paths remain.
