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

Lifecycle events are system events, distinct from the canonical statistical-operation vocabulary.

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

## 4. Duration and run timestamps

Elapsed duration should be measured with a monotonic clock and stored numerically as `duration_seconds`.

Program-level provenance records canonical UTC ISO 8601 run timestamps separately:

```text
started_at
ended_at
```

```text
UTC wall clock   → run started_at / ended_at
monotonic clock  → elapsed duration
```

Event-level timestamps are a separate concern. Human-readable duration formatting belongs to the renderer. Provenance timestamp semantics are defined in [`provenance.md`](provenance.md).

## 5. Exception handling

```text
observe exception
      ↓
record failed END event if safe
      ↓
close TRACE lifecycle state
      ↓
re-raise original exception
```

The original program exception takes precedence over any secondary TRACE logging failure. `KeyboardInterrupt` and `SystemExit` must also propagate.

Exception messages may contain sensitive content. `exception_type` is the safe baseline; message capture remains subject to privacy/output policy.

## 6. Simple construction

This remains valid:

```python
trace = Trace("T14_01")
trace.read("ADSL", rows=254, columns=16)
trace.output("T14_01", "outputs/T14_01.xlsx")
```

Simple construction does **not** imply automatic START/END events. Do not emit START from `__init__()`, END from `__del__()`, or use garbage collection as lifecycle control.

## 7. Lifecycle state and reuse

A context-managed instance progresses conceptually through:

```text
NOT_STARTED → RUNNING → ENDED
```

Reject nested entry of the same instance, duplicate START/END events, END before START, and automatic reuse of an ended instance. A new run should normally create a new `Trace` instance.

## 8. Run identity and provenance

One `Trace` instance represents one execution identity. Events from the instance share a stable `run_id`, including events emitted without the context-manager lifecycle.

Configured context such as `program` and optional `study` applies to lifecycle and semantic events.

`run_id` is also the identifier used by program-level execution provenance; TRACE should not introduce a second competing provenance identifier.

Program-level provenance additionally records:

```text
program
started_at
ended_at
input_artifacts
output_artifacts
optional artifact hashes
```

That provenance is recorded once for the run rather than repeated across semantic events. Artifact-registration and finalization mechanics remain an implementation concern.

## 9. Severity and status defaults

```text
START               severity=INFO   status=None
successful END      severity=INFO   status=SUCCESS
failed END          severity=ERROR  status=FAIL
```

This mapping is specific to lifecycle events.

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

The row counts in this Core example are supplied diagnostics. An integration that directly inspects runtime objects may record equivalent values as observed evidence.

## 11. Related specifications

- [`domain-model.md`](domain-model.md) — status, severity, metrics, and context.
- [`configuration.md`](configuration.md) — `Trace(...)` construction and inherited context.
- [`provenance.md`](provenance.md) — program-level timestamps and artifact provenance.
- [`reviewer-experience.md`](reviewer-experience.md) — evidence origin and reviewer interpretation.
- [`step-level-instrumentation.md`](step-level-instrumentation.md) — logical execution scopes.
- [`../framework/core-operations-v0.1.md`](../framework/core-operations-v0.1.md) — statistical operation vocabulary.
