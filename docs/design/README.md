# TRACE Design Documentation

The `docs/design/` directory preserves the reasoning, decisions, and empirical findings that shaped TRACE. It is not intended to duplicate the public API, concept pages, or task-oriented user documentation.

## Documentation rule

TRACE documentation follows one principle:

> **Define each concept once in its authoritative document; reference it elsewhere.**

A design document should primarily do one or more of the following:

- record a design decision;
- explain the evidence or trade-offs behind that decision;
- document consequences for later phases; or
- preserve findings from experiments, prototypes, or comparative research.

It should not restate an established public concept merely to provide context.

## Authoritative ownership

| Concept | Authoritative document |
|---|---|
| User-facing structured-event concept | [Structured events](../concepts/structured-events.md) |
| User-facing program-level provenance concept | [Program-level provenance](../concepts/provenance.md) |
| Event structure and internal domain concepts | [TRACE Domain Model Specification](domain-model.md) |
| Canonical statistical-operation vocabulary | [TRACE Core Operations v0.1](../framework/core-operations-v0.1.md) |
| Public Tier 1 API contract | [TRACE Tier 1 API Specification](tier-1-api.md) |
| Configuration behavior | [TRACE Phase 6 — Configuration](configuration.md) |
| Program lifecycle | [TRACE Phase 7 — Lifecycle Behavior](lifecycle.md) |
| Step instrumentation | [TRACE Phase 8 — Step-Level Instrumentation](step-level-instrumentation.md) |
| Programmer experience principles | [TRACE Phase 2 — Minimum Programmer Experience](minimum-programmer-experience.md) |
| Reviewer model and diagnostic evidence | [TRACE Reviewer Experience](reviewer-experience.md) |
| Provenance implementation design | [TRACE Execution Provenance](provenance.md) |
| Prototype findings | [TRACE Reference Prototype Findings](reference-prototype-findings.md) |

When a later design phase depends on one of these concepts, it should link to the authoritative document instead of redefining it.

## Advanced evidence-origin terminology

Design work may distinguish diagnostic values by how they were obtained:

```text
SUPPLIED   caller passed the value
OBSERVED   TRACE or an integration inspected runtime state or an artifact
DERIVED    TRACE calculated the value from diagnostics with known origins
```

This terminology belongs to architecture and integration design rather than the normal user documentation path. TRACE Core currently relies primarily on programmer-supplied diagnostics. User-facing documentation should describe what TRACE records without requiring users to classify evidence origin.

If future integrations expose observed or derived diagnostics as a meaningful public capability, the public documentation can introduce those distinctions at that time.

## Design records and background research

The following files primarily preserve design evidence or historical reasoning rather than define a public contract:

- [TRACE API Design Plan](api-design-plan.md)
- [Comparative Design Review](comparative-review.md)
- [TRACE Phase 5 — Generic Structured Logging](generic-structured-logging.md)
- [TRACE Phase 4 — Object vs Operation](object-vs-operation.md)
- [TRACE Reference Prototype Contract](reference-prototype.md)

These documents are useful when reviewing why TRACE made a particular decision, but ordinary users should not need to read them to use TRACE.

## Relationship to the rest of the documentation

```text
design records
     │
     │ accepted decisions
     ▼
concepts and framework reference
     │
     ├──────────────► API reference
     │
     └──────────────► guides and examples
```

- `docs/concepts/` explains the small set of ideas behind TRACE's public behavior.
- `docs/framework/` defines the statistical-operation vocabulary and reviewer methodology.
- `docs/api/` explains how to call the Python implementation.
- `docs/guides/` explains how to accomplish statistical-programming tasks with TRACE.
- `docs/design/` explains why TRACE was designed this way and preserves internal architecture history.

This separation keeps the user-facing documentation concise while preserving architectural depth.
