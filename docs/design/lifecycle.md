# TRACE Phase 7 — Lifecycle Behavior

**Phase:** 7 — Define Lifecycle Behavior  
**Status:** Draft normative lifecycle specification  
**Scope:** Program START/END events, context-manager behavior, duration, failure handling, run identity, and relationship to run provenance

## 1. Decision

TRACE supports an optional program lifecycle through the `Trace` context manager:

```python
with Trace("T14_01") as trace:
    ...
```

This emits automatic START and END events while preserving the simpler construction style:

```python
trace = Trace("T14_01")
```

> **Lifecycle automation adds explicit execution boundaries without making context-manager usage mandatory.**

Lifecycle events are system events. They are distinct from the canonical statistical-operation vocabulary defined in [`../framework/core-operations-v0.1.md`](../framework/core-operations-v0.1.md).

## 2. Lifecycle behavior

Entering a context-managed run emits:

```text
INFO [START] [T14_01] execution started
```

Normal exit emits:

```text
INFO [END] [T14_01] execution completed – 00:00:08.24
```

Unhandled failure emits a failed END event and re-raises the original exception:

```text
ERROR [END] [T14_01] execution failed – ValueError
```

TRACE must not swallow, replace, retry, or silently recover from the underlying exception.

## 3. Structured semantics

Conceptually, successful lifecycle events contain:

```json
{
  "operation": "START",
  "object": "T14_01",
  "action": "execution started"
}
```

and:

```json
{
  "operation": "END",
  "object": "T14_01",
  "action": "execution completed",
  "status": "SUCCESS",
  "metrics": {
    "duration_seconds": 8.24
  }
}
```

A failed END uses `status="FAIL"`, `severity="ERROR"`, and safe exception metadata such as `exception_type`.

The event-model definitions for status, severity, metrics, and context belong to [`domain-model.md`](domain-model.md).

## 4. Duration and run timestamps

Elapsed duration should be measured with a monotonic clock and stored numerically as `duration_seconds`.

Program-level provenance records canonical run timestamps separately:

```text
started_at
ended_at
```

These are UTC ISO 8601 timestamps as defined in [`provenance.md`](provenance.md). Event-level timestamps are a separate concern and are not required for the minimal provenance model.

```text
UTC wall clock   → run started_at / ended_at
monotonic clock  → elapsed duration
```

Human-readable duration formatting belongs to the renderer.

## 5. Exception handling

The lifecycle contract is:

```text
observe exception
      ↓
record failed END event if safe
      ↓
close TRACE lifecycle state
      ↓
re-raise original exception
```

The original program exception takes precedence over any secondary TRACE logging failure.

`KeyboardInterrupt` and `SystemExit` must also propagate. TRACE may record an unsuccessful END event when safe, but must not suppress process-level control flow.

Exception messages may contain paths, data values, identifiers, credentials, or other sensitive content. `exception_type` is the safe baseline; message capture remains subject to privacy/output policy.

## 6. Simple construction

This remains valid:

```python
trace = Trace("T14_01")
trace.read("ADSL", rows=254, columns=16)
trace.output("T14_01", "outputs/T14_01.xlsx")
```

Simple construction does **not** imply automatic START/END events. Object creation is not a reliable execution boundary, and object destruction is not a reliable completion boundary.

For that reason:

- do not emit START from `__init__()`;
- do not emit END from `__del__()`; and
- do not use garbage collection as lifecycle control.

A future explicit `start()` / `end()` API may reuse the same lifecycle state machine, but it is not required by the current design.

## 7. Lifecycle state and reuse

A context-managed `Trace` instance should conceptually progress through:

```text
NOT_STARTED → RUNNING → ENDED
```

The implementation should reject ambiguous lifecycle behavior such as nested entry of the same instance, duplicate START/END events, END before START, or automatic reuse of an already ended instance.

A new program run should normally create a new `Trace` instance.

## 8. Run identity and provenance

One `Trace` instance represents one execution identity. Events from the instance share a stable `run_id`, including events emitted without the context-manager lifecycle.

Lifecycle events inherit configured context such as `program` and optional `study`:

```python
with Trace("T14_01", study="ABC123") as trace:
    ...
```

`run_id` is also the identifier used by program-level execution provenance. TRACE should not introduce a second competing provenance identifier.

Program-level provenance additionally records:

```text
program
started_at
ended_at
input_artifacts
output_artifacts
optional artifact hashes
```

That provenance is recorded once for the run rather than repeated across semantic events. Exact artifact-registration and finalization mechanics remain an implementation concern.

## 9. Severity and status defaults

Recommended lifecycle mapping:

```text
START               severity=INFO   status=None
successful END      severity=INFO   status=SUCCESS
failed END          severity=ERROR  status=FAIL
```

This mapping is specific to lifecycle events and does not define general severity inference for all TRACE operations.

## 10. Example

```python
from trace_tlf import Trace

with Trace(
    "T14_01",
    study="ABC123",
    log_file="logs/T14_01.log",
) as trace:
    adsl = pd.read_parquet("analysis/adsl.parquet")
    trace.read(
        "ADSL",
        source="analysis/adsl.parquet",
        rows=len(adsl),
        columns=len(adsl.columns),
    )

    safety = adsl.loc[adsl["SAFFL"] == "Y"].copy()
    trace.filter(
        "ADSL",
        "SAFFL == 'Y'",
        result="Safety Population",
        before=len(adsl),
        after=len(safety),
    )

    summary = safety.groupby(["TRT01A", "SEX"]).size().reset_index(name="N")
    trace.aggregate(
        "Safety Population",
        by=["TRT01A", "SEX"],
        result="demographics_summary",
    )

    summary.to_excel("outputs/T14_01.xlsx")
    trace.output("T14_01", "outputs/T14_01.xlsx", rows=len(summary))
```

Possible output:

```text
INFO [START]     [T14_01] execution started
INFO [READ]      [ADSL] loaded – N=254, Vars=16
INFO [FILTER]    [ADSL] SAFFL == 'Y' applied – N=254 → 249
INFO [AGGREGATE] [Safety Population] summarized – by=TRT01A,SEX, result=demographics_summary
INFO [OUTPUT]    [T14_01] written – outputs/T14_01.xlsx
INFO [END]       [T14_01] execution completed – 00:00:08.24
```

The row counts in this Core example are supplied diagnostics. An integration that directly inspects the runtime objects may record equivalent values as observed evidence.

## 11. Related specifications

- [`domain-model.md`](domain-model.md) — status, severity, metrics, and context.
- [`configuration.md`](configuration.md) — `Trace(...)` construction and inherited context.
- [`provenance.md`](provenance.md) — program-level timestamps and artifact provenance.
- [`reviewer-experience.md`](reviewer-experience.md) — evidence origin and reviewer interpretation.
- [`step-level-instrumentation.md`](step-level-instrumentation.md) — nested logical execution scopes.
- [`../framework/core-operations-v0.1.md`](../framework/core-operations-v0.1.md) — statistical operation vocabulary.
