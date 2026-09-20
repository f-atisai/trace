# TRACE Framework

TRACE is a **semantic execution evidence framework for statistical programming**. It defines how meaningful execution activity is represented so programmers and reviewers can understand what happened during a run and reconcile that evidence with the program and its outputs.

The framework combines three evidence pillars:

```text
TRACE
 |
 +-- Semantic events
 +-- Structured diagnostics with evidence origin
 +-- Program-level execution provenance
```

A clean TRACE execution does not establish statistical correctness or replace specification review, code review, output review, or independent QC.

## Public framework documentation

- [TRACE Core Operations v0.1](core-operations-v0.1.md) — canonical statistical-operation vocabulary and semantic boundaries.
- [Reviewing Statistical Programs with TRACE](reviewer-guide.md) — how reviewers use TRACE alongside statistical programs and outputs.
- [TRACE API](../api/README.md) — authoritative TRACE for Python Developer Preview API.
- [Getting Started with TRACE](../guides/getting-started.md) — first complete programmer workflow.

## Core model

A TRACE event conceptually carries:

```text
Event
├── severity
├── operation
├── object
├── action
├── metrics
├── details
├── status
└── context
```

The canonical semantic operations are:

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

Lifecycle/system operations are:

```text
START
END
STEP
```

The operation vocabulary is defined in detail in [TRACE Core Operations v0.1](core-operations-v0.1.md).

## Evidence origin

Structured diagnostics distinguish conceptually between:

```text
SUPPLIED   caller passed the value
OBSERVED   TRACE or an integration inspected runtime state or an artifact
DERIVED    TRACE calculated the value from diagnostics with known origins
```

TRACE Core currently emphasizes caller-supplied diagnostics. Future integrations may observe runtime objects without changing the semantic operation model.

## Program-level provenance

For managed Python runs with `log_file`, TRACE can finalize a review log that identifies the program execution and the physical input/output artifacts registered through READ and OUTPUT events.

Provenance is recorded once for the run rather than repeated on every event. The Developer Preview does not expose artifact hashing, environment fingerprinting, or provenance configuration controls.

See the public [TRACE API](../api/README.md) for the supported behavior programmers can rely on.
