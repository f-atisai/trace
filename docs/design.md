# TRACE Design

This document describes the current TRACE architecture and the design principles contributors should preserve.

TRACE is a lightweight structured logging library for Python statistical programming. It builds on Python's standard logging infrastructure and adds a controlled statistical-programming vocabulary, structured events, lifecycle handling, and lightweight program-level provenance.

The goal is not to own statistical computation. pandas, Polars, NumPy, statistical libraries, and user code perform the work; TRACE records the meaningful operations around that work.

## Design principles

TRACE should remain:

- **small** — routine use should require little configuration or ceremony;
- **statistical-programming aware** — the API should describe analytical intent rather than Python logging mechanics;
- **backend-independent** — the same operation vocabulary should work with pandas, Polars, SQL, NumPy, or custom code;
- **structured first** — events are structured records before they are rendered as text;
- **review friendly** — logs should help another programmer understand how a run progressed;
- **non-invasive** — TRACE records work performed elsewhere rather than wrapping or replacing analytical libraries; and
- **explicit about limits** — TRACE output does not establish statistical correctness or replace QC.

## Architecture

The core flow is:

```text
statistical program
       ↓
Trace helper call
       ↓
TraceEvent
       ↓
renderer
       ↓
Python logging
       ↓
console / finalized log
```

A normal call such as:

```python
trace.filter(
    "ADSL",
    "SAFFL == 'Y'",
    before=754,
    after=720,
)
```

creates a structured event representing the operation and its diagnostics. The renderer turns that event into a concise human-readable line:

```text
INFO [FILTER] [ADSL] SAFFL == 'Y' applied – N=754 → 720
```

TRACE must not depend on parsing its own rendered text to reconstruct event meaning.

## Structured event model

A TRACE event conceptually contains:

```text
operation
object
action
metrics
details
status
context
severity
```

The event is the semantic record; the rendered log line is one presentation of it.

Important invariants:

- `operation` uses the TRACE vocabulary;
- `object` identifies a stable statistical or execution concept rather than requiring a Python object;
- `metrics` remain structured values rather than preformatted strings;
- `details` carry supplementary information such as source, result, keys, method, or format;
- `status` is used only where an outcome is meaningful;
- context is logically separate from the event payload; and
- renderers may omit detail for readability but must not change event meaning.

Avoid subject-level sensitive values unless a justified use case explicitly requires them.

## Operation vocabulary

TRACE uses eleven statistical operations:

```text
READ  CHECK  FILTER  SORT  DERIVE  TRANSFORM
MERGE  AGGREGATE  ANALYZE  VALIDATE  OUTPUT
```

`START`, `END`, and `STEP` are lifecycle/system operations rather than statistical operations.

The vocabulary classifies statistical intent, not implementation syntax. Equivalent pandas, Polars, SQL, or custom implementations should map to the same TRACE operation.

Operation boundaries and examples are defined in [TRACE operations](operations.md). The vocabulary should grow slowly and only when realistic programs repeatedly expose a genuine semantic gap.

## Configuration

Configuration belongs on the `Trace` instance rather than on every operation call.

The current constructor is intentionally small:

```python
Trace(
    program,
    *,
    study=None,
    log_file=None,
    level="INFO",
)
```

Routine use should not require knowledge of Python logging handlers, formatters, propagation rules, or dictionary configuration.

Instance configuration establishes shared execution context such as `program`, optional `study`, and run identity. Operation methods should remain focused on describing statistical execution.

## Lifecycle and run identity

Using `Trace` as a context manager creates an explicit run lifecycle:

```python
with Trace("T14_01") as trace:
    ...
```

A managed run emits `START` and `END` events automatically. An ordinary Python exception results in a failed `END` event while the original exception continues to propagate.

One `Trace` instance represents one execution identity and has one stable `run_id`. A completed managed instance should not be silently reused as a new run; create a new `Trace` instance instead.

Lifecycle duration is an execution diagnostic. Program-level provenance separately identifies the run and its artifacts.

## Steps

`trace.step()` provides optional coarse-grained execution scopes:

```python
with trace.step("Analysis population"):
    ...
```

Steps should represent recognizable analytical stages, not individual Python statements. They exist to make a run easier to scan and understand.

Nested step behavior belongs to lifecycle context; step names are execution labels rather than statistical operations.

## Program-level provenance

TRACE provenance is intentionally run-level rather than repeated on each statistical event.

The current Developer Preview records:

```text
program
run_id
executed
input_artifacts
output_artifacts
```

During a managed run:

- `trace.read(..., source=...)` can register an input artifact;
- `trace.output(..., path=...)` can register an output artifact;
- duplicate paths are listed once; and
- artifact registration does not change the semantic meaning of READ or OUTPUT events.

A finalized log therefore has two layers:

```text
program-level provenance
          ↓
ordered event stream
```

Artifact hashes, environment fingerprints, Git metadata, package inventories, and automatic recovery of interrupted runs are not part of the current release.

## Finalized log behavior

TRACE streams rendered events to the console as execution proceeds.

When a managed run uses `log_file`, TRACE also preserves the event stream so it can publish a finalized provenance-first log when the context exits.

Conceptually:

```text
TraceEvent
   ├──► console immediately
   └──► event spool
              ↓
       run completes
              ↓
       provenance rendered
              ↓
       finalized log published
```

The implementation uses a file-backed spool rather than buffering the complete run in memory. Final publication is assembled separately so the configured log represents one complete run.

The statistical program's active exception takes precedence over TRACE finalization failures. TRACE must not replace an original program exception with a secondary logging/finalization error.

Hard process termination can bypass normal context-manager finalization; the Developer Preview does not guarantee recovery in that case.

## Public and internal boundaries

The supported top-level import is intentionally small:

```python
from trace_stat import Trace
```

Internal classes such as `TraceEvent`, context objects, renderers, provenance helpers, operation/status enums, and spool/finalization machinery are implementation details unless explicitly promoted to the public API in a future release.

Contributors should avoid forcing users to depend on internal objects merely because those objects are importable from implementation modules.

## Backend independence

TRACE Core should not depend on pandas, Polars, or another dataframe library.

The correct relationship is:

```text
pandas / Polars / statistical library / user code
                    ↓
              performs the work
                    ↓
                   TRACE
                    ↓
          records the operation
```

Optional integrations may inspect or simplify instrumentation for specific libraries, but they should not make that backend a core dependency or change the meaning of the TRACE vocabulary.

## Rendering and Python logging

Python logging remains the transport and severity mechanism. TRACE adds statistical structure above it.

Severity answers questions such as:

```text
How serious is this event?
```

TRACE operations answer:

```text
What happened in the statistical workflow?
```

These concepts should remain separate. Operation helpers should not expose routine logging-handler configuration or require callers to build message strings manually.

## Extension principles

New features should preserve the small core rather than broaden it by default.

A new operation, integration, renderer, sink, configuration option, or provenance field should be added only when a concrete statistical-programming use case demonstrates that the existing model is insufficient.

Prefer:

- optional integrations over new core dependencies;
- structured fields over encoded strings;
- existing operations over synonyms;
- stable statistical identities over implementation variable names; and
- small public APIs over exposing internals for convenience.

## Contributor invariants

Changes should preserve these rules unless there is an explicit design decision to change them:

1. TRACE records statistical work; it does not own the underlying transformation or analysis.
2. Structured events remain the source of semantic truth.
3. The operation vocabulary remains backend-independent.
4. `START`, `END`, and `STEP` stay separate from the statistical-operation vocabulary.
5. One managed `Trace` instance represents one run identity.
6. Program-level provenance remains separate from individual statistical events.
7. READ and OUTPUT describe workflow semantics; provenance records the associated physical artifact paths.
8. An active program exception must not be masked by a TRACE finalization failure.
9. Internal implementation objects are not automatically public API.
10. TRACE output must not be presented as proof of statistical correctness.

## Documentation ownership

The release documentation intentionally stays small:

- [Getting Started](getting-started.md) — first successful TRACE program;
- [Logging with TRACE](logging-with-trace.md) — practical usage, lifecycle, steps, logs, provenance, and review boundaries;
- [TRACE operations](operations.md) — operation vocabulary and selection rules;
- this document — current architecture and contributor invariants.
