# TRACE for Python — v0.1.0-alpha API

> **Developer Preview:** TRACE is under active API development. This release is intended for experimentation and feedback from statistical programmers. APIs may change before v1.0.

This document defines the supported public surface for the first TRACE developer preview. Anything not documented here is not part of the alpha compatibility contract.

## Import

The supported top-level import is intentionally small:

```python
from trace_tlf import Trace
```

`TraceEvent`, `TraceContext`, `Operation`, `Severity`, `Status`, renderers, logger internals, event factories, and other implementation classes are not top-level alpha APIs. They may be used internally by TRACE and its tests, but external programs should not rely on them yet.

## Constructor

```python
Trace(
    program,
    *,
    study=None,
    log_file=None,
    level="INFO",
)
```

- `program` — required semantic program identity, for example `"T14_01"`.
- `study` — optional study identity inherited by events.
- `log_file` — optional path for a persistent UTF-8 text log. Console output remains enabled.
- `level` — optional logging threshold; defaults to `"INFO"`.

The alpha does not expose constructor arguments for handlers, formatters, propagation, streams, JSON sinks, provenance capture, hashing, environment capture, or integrations.

## Program lifecycle

Both construction styles are public:

```python
trace = Trace("T14_01")
```

This does not automatically emit program START/END events.

```python
with Trace("T14_01") as trace:
    ...
```

The context-managed form emits automatic START/END lifecycle events and is the preferred pattern when a program has a clear execution boundary.

## Primary semantic workflow

The alpha quick-start experience emphasizes:

```text
READ → FILTER → DERIVE → MERGE → AGGREGATE → ANALYZE → VALIDATE → OUTPUT
```

All eleven canonical semantic helpers are public:

```python
trace.read(...)
trace.check(...)
trace.filter(...)
trace.sort(...)
trace.derive(...)
trace.transform(...)
trace.merge(...)
trace.aggregate(...)
trace.analyze(...)
trace.validate(...)
trace.output(...)
```

`CHECK`, `SORT`, and `TRANSFORM` are secondary only in documentation prominence. They have the same alpha-public status as the other Tier 1 helpers.

The canonical meanings of these operations are defined in [`../framework/core-operations-v0.1.md`](../framework/core-operations-v0.1.md). Full signatures and argument semantics are defined in [`../design/tier-1-api.md`](../design/tier-1-api.md).

## Named FILTER results

`FILTER` can preserve both the source object and the resulting analytical concept:

```python
trace.filter(
    "ADSL",
    "SAFFL == 'Y'",
    result="Safety Population",
    before=len(adsl),
    after=len(safety),
)
```

The event source remains `ADSL`; `Safety Population` is recorded as structured result identity. `result` does not imply a Python variable of that name exists.

TRACE does not introduce a separate `POPULATION` operation.

## Steps

`trace.step()` is alpha public and optional:

```python
with trace.step("Analysis population"):
    safety = adsl.query("SAFFL == 'Y'")
    trace.filter(
        "ADSL",
        "SAFFL == 'Y'",
        result="Safety Population",
        before=len(adsl),
        after=len(safety),
    )
```

Steps should describe coarse analytical stages. They are not required around every operation.

## Advanced structured events

`trace.log()` is a supported **advanced public escape hatch**:

```python
trace.log(
    "CHECK",
    object="Treatment Mapping",
    action="reconciled against randomization specification",
    metrics={"unmapped_subjects": 0},
)
```

Use Tier 1 semantic helpers whenever one fits. `trace.log()` exists for unusual semantic events and accepts canonical TRACE operations; it is deliberately not the normal introductory programming style.

## Public API boundary

For the developer preview, interfaces are classified internally as:

| Classification | Meaning |
|---|---|
| Alpha public | Supported and deliberately exposed for developer-preview feedback |
| Advanced public | Supported escape hatch, but not the preferred programming style |
| Internal | Implementation detail; no alpha compatibility commitment |
| Not in alpha | Deliberately deferred from the first release |

### Alpha public

```text
Trace(...)
Trace context-manager lifecycle
trace.read()
trace.check()
trace.filter()
trace.sort()
trace.derive()
trace.transform()
trace.merge()
trace.aggregate()
trace.analyze()
trace.validate()
trace.output()
trace.step()
```

### Advanced public

```text
trace.log()
```

### Internal

```text
TraceEvent
TraceContext
Operation
Severity
Status
renderers
logger internals
event factories
step implementation objects
```

### Not in alpha

```text
pandas / Polars / PyArrow integrations
custom public renderers or sinks
program-level provenance configuration
automatic artifact hashing
environment fingerprinting
automatic instrumentation
```

## Alpha compatibility rule

The documented API above is the supported `v0.1.0-alpha` surface. The release is explicitly pre-stable: public alpha APIs may still change based on statistical-programmer feedback before v1.0. Undocumented package internals should be treated as implementation details rather than accidental public APIs.
