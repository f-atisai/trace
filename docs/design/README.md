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
| Event structure and core domain concepts | [`domain-model.md`](domain-model.md) |
| Canonical statistical-operation vocabulary | [`../framework/core-operations-v0.1.md`](../framework/core-operations-v0.1.md) |
| Public Tier 1 API contract | [`tier-1-api.md`](tier-1-api.md) |
| Configuration behavior | [`configuration.md`](configuration.md) |
| Program lifecycle | [`lifecycle.md`](lifecycle.md) |
| Step instrumentation | [`step-level-instrumentation.md`](step-level-instrumentation.md) |
| Programmer experience principles | [`minimum-programmer-experience.md`](minimum-programmer-experience.md) |
| Reviewer model and execution evidence | [`reviewer-experience.md`](reviewer-experience.md) |
| Prototype findings | [`reference-prototype-findings.md`](reference-prototype-findings.md) |

When a later design phase depends on one of these concepts, it should link to the authoritative document instead of redefining it.

## Design records and background research

The following files primarily preserve design evidence or historical reasoning rather than define a public contract:

- [`api-design-plan.md`](api-design-plan.md)
- [`comparative-review.md`](comparative-review.md)
- [`generic-structured-logging.md`](generic-structured-logging.md)
- [`object-vs-operation.md`](object-vs-operation.md)
- [`reference-prototype.md`](reference-prototype.md)

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
