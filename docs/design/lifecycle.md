# TRACE Phase 7 — Lifecycle Behavior

**Phase:** 7 — Define Lifecycle Behavior  
**Status:** Normative Developer Preview lifecycle specification  
**Scope:** Program START/END events, context-manager behavior, duration, failure handling, run identity, and relationship to finalized run provenance

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

Lifecycle events are system events, distinct from the canonical statistical-operation vocabulary.

## 2. Lifecycle behavior

Entering a context-managed run emits:

```text
INFO [START] [T14_01] execution started
```

Normal exit emits a successful END event. Unhandled failure emits a failed END event and re-raises the original exception:

```text
ERROR [END] [T14_01] execution failed – ValueError
```

Semantic events, including START, STEP, and END, stream live. TRACE does not delay them until run completion.

When `log_file` is configured, the same rendered events are also written in order to an internal file-backed spool. At context exit TRACE attempts to assemble and atomically publish the finalized provenance-first review log.

## 3. Structured semantics

Conceptually:

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
  "metrics": {"duration_seconds": 8.24}
}
```

A failed END uses `status="FAIL"`, `severity="ERROR"`, and safe exception metadata such as `exception_type`.

## 4. Duration and run provenance

Elapsed duration is measured with a monotonic clock and stored numerically as `duration_seconds`.

Program-level provenance separately records the stable `program`, `run_id`, one UTC ISO 8601 `executed` timestamp, and registered input/output artifacts. Provenance belongs to the run rather than individual semantic events.

```text
UTC wall clock   → run provenance identity
monotonic clock  → elapsed lifecycle duration
```

The provenance and final-log rules are defined in [`provenance.md`](provenance.md).

## 5. Exception handling and precedence

The lifecycle failure path is:

```text
observe program exception
        ↓
record failed STEP/END evidence where applicable
        ↓
close lifecycle state
        ↓
attempt finalized review log
        ↓
propagate original exception unchanged
```

The original program exception takes precedence over secondary TRACE failures. A provenance-rendering, spool-reading, staging, publication, or cleanup failure must not replace an already-active program exception.

`KeyboardInterrupt` and `SystemExit` also propagate. TRACE may attempt finalization as context exit unwinds, but the active exception remains authoritative.

If no program exception is active and configured log finalization fails, TRACE raises a runtime error instead of silently presenting the managed execution as fully finalized.

Exception messages may contain sensitive content. `exception_type` is the safe baseline; message capture remains subject to privacy/output policy.

## 6. Finalization and hard termination

For managed runs with `log_file`:

```text
normal completion → END → finalization → finalized review log
Python exception  → failed END → finalization attempt → original exception
```

Finalization uses a file-backed spool and staging file rather than a full-run in-memory buffer. The staging file is flushed and closed before atomic replacement of the configured destination where supported.

Hard process termination can bypass `__exit__`. In that case finalization is not guaranteed and an internal event spool may remain. The alpha Developer Preview does not automatically discover or recover incomplete spools.

## 7. Simple construction

This remains valid:

```python
trace = Trace("T14_01")
trace.read("ADSL", rows=254, columns=16)
trace.output("T14_01", "outputs/T14_01.xlsx")
```

Simple construction does **not** imply automatic START/END events or finalized run provenance. Do not emit START from `__init__()`, END from `__del__()`, or use garbage collection as lifecycle control.

## 8. Lifecycle state and reuse

A context-managed instance progresses conceptually through:

```text
NOT_STARTED → RUNNING → ENDED
```

Reject nested entry of the same instance, duplicate START/END events, END before START, and automatic reuse of an ended instance. A new run should normally create a new `Trace` instance.

## 9. Run identity

One `Trace` instance represents one execution identity. Events from the instance share a stable `run_id`, including events emitted without the context-manager lifecycle.

Configured context such as `program` and optional `study` applies to lifecycle and semantic events. The same `run_id` identifies the program-level provenance block; TRACE does not introduce a competing provenance identifier.

## 10. Severity and status defaults

```text
START               severity=INFO   status=None
successful END      severity=INFO   status=SUCCESS
failed END          severity=ERROR  status=FAIL
```

This mapping is specific to lifecycle events.

## 11. Example

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

During execution, the semantic events appear immediately on the console. After context exit, `logs/T14_01.log` is the finalized provenance-first review artifact containing those same events in execution order.

## 12. Developer Preview guarantees

- semantic events stream live;
- no full-run in-memory event buffer is used;
- program-level provenance is finalized after execution;
- configured `log_file` is published as a complete review artifact rather than incrementally modified;
- normal Python failures still attempt finalization;
- TRACE finalization failures never mask an active program exception;
- finalization failure without a program exception is surfaced;
- successful finalization cleans temporary spool/staging files;
- hard termination may prevent finalization;
- automatic recovery and artifact hashing remain outside alpha scope;
- the public constructor remains unchanged.

## 13. Related specifications

- [`domain-model.md`](domain-model.md) — status, severity, metrics, and context.
- [`configuration.md`](configuration.md) — `Trace(...)` construction and inherited context.
- [`provenance.md`](provenance.md) — program-level provenance and finalized review logs.
- [`reviewer-experience.md`](reviewer-experience.md) — evidence origin and reviewer interpretation.
- [`step-level-instrumentation.md`](step-level-instrumentation.md) — logical execution scopes.
- [`../framework/core-operations-v0.1.md`](../framework/core-operations-v0.1.md) — statistical operation vocabulary.
