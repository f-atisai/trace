# TRACE Design Documentation

The `docs/design/` directory preserves the reasoning, decisions, and empirical findings that shaped TRACE. It is not intended to duplicate the normative framework or public API documentation.

## Documentation rule

TRACE documentation follows one principle:

> **Define each concept once in its authoritative document; reference it elsewhere.**

A design document should primarily do one or more of the following:

- record a design decision;
- explain the evidence or trade-offs behind that decision;
- document consequences for later phases; or
- preserve findings from experiments, prototypes, or comparative research.

It should not restate an established specification merely to provide context.

## Authoritative ownership

| Concept | Authoritative document |
|---|---|
| Event structure and core domain concepts | [TRACE Domain Model Specification](domain-model.md) |
| Canonical statistical-operation vocabulary | [TRACE Core Operations v0.1](../framework/core-operations-v0.1.md) |
| Public Tier 1 API contract | [TRACE Tier 1 API Specification](tier-1-api.md) |
| Configuration behavior | [TRACE Phase 6 — Configuration](configuration.md) |
| Program lifecycle | [TRACE Phase 7 — Lifecycle Behavior](lifecycle.md) |
| Step instrumentation | [TRACE Phase 8 — Step-Level Instrumentation](step-level-instrumentation.md) |
| Programmer experience principles | [TRACE Phase 2 — Minimum Programmer Experience](minimum-programmer-experience.md) |
| Reviewer model and diagnostic evidence | [TRACE Reviewer Experience](reviewer-experience.md) |
| Execution provenance | [TRACE Execution Provenance](provenance.md) |
| Prototype findings | [TRACE Reference Prototype Findings](reference-prototype-findings.md) |

When a later design phase depends on one of these concepts, it should link to the authoritative document instead of redefining it.

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
framework specifications
     │
     ├──────────────► API reference
     │
     └──────────────► guides and examples
```

- `docs/framework/` explains what TRACE means.
- `docs/api/` explains how to call the Python implementation.
- `docs/guides/` explains how to accomplish statistical-programming tasks with TRACE.
- `docs/design/` explains why TRACE was designed this way.

This separation keeps the user-facing documentation concise while preserving architectural history.
