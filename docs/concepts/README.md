# TRACE concepts

TRACE is a structured logging library for statistical programming. Most users can begin with the [Getting Started guide](../guides/getting-started.md) and the [TRACE operations guide](../guides/operations.md) without reading these pages first.

The concept pages explain the small set of ideas behind TRACE's public behavior:

- [Structured events](structured-events.md) — how TRACE represents recorded operations before rendering them as log lines.
- [Program-level provenance](provenance.md) — how TRACE identifies a run and its registered input/output artifacts.

For practical operation selection and examples, see [TRACE operations](../guides/operations.md). For the normative vocabulary rules, see [TRACE Core Operations v0.1](../framework/core-operations-v0.1.md). For reviewer workflow, see [Reviewing Statistical Programs with TRACE](../framework/reviewer-guide.md).

Design history and internal rationale remain under [`docs/design/`](../design/README.md).
