# TRACE framework reference

TRACE is a structured logging library for statistical programming. Most users should begin with the [Getting Started guide](../guides/getting-started.md), then use the [TRACE operations guide](../guides/operations.md), [TRACE API](../api/README.md), and examples as needed.

This directory contains the deeper reference material that defines TRACE's statistical-operation vocabulary and reviewer methodology.

## Framework reference

- [TRACE Core Operations v0.1](core-operations-v0.1.md) — canonical statistical-operation vocabulary and operation semantics.
- [Reviewing Statistical Programs with TRACE](reviewer-guide.md) — how reviewers use TRACE logs alongside programs and outputs.

For practical operation selection and examples, see [TRACE operations](../guides/operations.md).

For the concepts behind TRACE's public behavior, see:

- [Structured events](../concepts/structured-events.md)
- [Program-level provenance](../concepts/provenance.md)

For the supported Python interface, see the [TRACE API](../api/README.md).

## Statistical-operation vocabulary

TRACE deliberately uses a controlled vocabulary for common statistical-programming activity:

```text
READ
CHECK
FILTER
SORT
DERIVE
TRANSFORM
MERGE
AGGREGATE
ANALYZE
VALIDATE
OUTPUT
```

Lifecycle operations are:

```text
START
END
STEP
```

The canonical definitions and boundaries for these operations are maintained in [TRACE Core Operations v0.1](core-operations-v0.1.md). The [TRACE operations guide](../guides/operations.md) translates those rules into practical examples from statistical workflows.

## Architecture and design history

TRACE internally represents recorded activity as structured events and keeps program-level provenance separate from ordinary event rendering. Those concepts are documented under [`docs/concepts/`](../concepts/README.md).

Design history, implementation rationale, experimental models, and terminology that is not part of the normal user path belong under [`docs/design/`](../design/README.md).

A clean TRACE run does not establish statistical correctness or replace specification review, code review, output review, or independent QC.
