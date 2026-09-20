# TRACE for Python — v0.1.0-alpha API

> **Developer Preview:** TRACE is under active API development. This release is intended for experimentation and feedback from statistical programmers. APIs may change before v1.0.

This document is the authoritative user-facing reference for the TRACE for Python alpha public API. A programmer should not need the design documents to determine how to call a supported public method.

## Import

The supported top-level import is intentionally small:

```python
from trace_tlf import Trace
```

`TraceEvent`, `TraceContext`, `Operation`, `Severity`, `Status`, renderers, provenance internals, logger internals, event factories, and step implementation objects are not top-level alpha APIs.

## `Trace(...)`

```python
Trace(
    program,
    *,
    study=None,
    log_file=None,
    level="INFO",
)
```

- `program` — required non-empty statistical-program identity, for example `"T14_01"`.
- `study` — optional study identity inherited by events.
- `log_file` — optional string or `Path` identifying a UTF-8 persistent log.
- `level` — logging threshold. Supported names are `DEBUG`, `INFO`, `WARNING`, `ERROR`, and `CRITICAL`, case-insensitively. The default is `INFO`.

Each `Trace` instance receives a stable `run_id` when constructed.

Invalid or empty `program` values are rejected. `study`, when supplied, must be a string, and unsupported logging levels are rejected.

The alpha does not expose constructor arguments for handlers, formatters, propagation, streams, JSON sinks, hashing, environment capture, or runtime integrations.

### Managed and unmanaged logging

Both construction styles are public:

```python
trace = Trace("T14_01", log_file="logs/T14_01.log")
trace.check("ADSL", "required variables present")
```

Without a context manager, TRACE does not emit automatic START/END events. When `log_file` is configured, emitted events are written to the file immediately as ordinary TRACE event text.

The preferred program-level form is:

```python
with Trace("T14_01", log_file="logs/T14_01.log") as trace:
    ...
```

The managed form emits START/END lifecycle events. Console events remain live during execution. When the managed run ends normally or through an ordinary Python exception, TRACE attempts to publish a finalized review log with program-level provenance followed by the same semantic event stream.

```text
TRACE EXECUTION

Program:  T14_01
Run ID:   7eab...
Executed: 2026-09-14T14:32:18Z

Input artifacts:
  data/adsl.xpt

Output artifacts:
  outputs/T14_01.rtf

INFO [START] [T14_01] execution started
...
INFO [END] [T14_01] execution completed – 0.84s
```

A `READ` source and `OUTPUT` path can contribute physical artifact identities to this program-level provenance. Artifact hashing is not part of the alpha API.

A `Trace` instance cannot be nested with itself or reused after its managed lifecycle has ended. Exceptions from the statistical program propagate; TRACE does not suppress them.

## Return values and common conventions

The semantic helpers and `trace.log()` return the structured event TRACE creates internally. The event classes themselves are internal in the alpha compatibility contract; normal user code should not need to import or construct them.

Across the Tier 1 API:

- core semantic identities are positional where appropriate;
- richer evidence is keyword-only;
- `details` carries uncommon descriptive metadata;
- `metrics` carries structured diagnostics where the method exposes it;
- named count diagnostics must be non-negative integers;
- TRACE records the operation after the statistical program performs it rather than owning the transformation.

For example:

```python
safety = adsl.query("SAFFL == 'Y'")
trace.filter(
    "ADSL",
    "SAFFL == 'Y'",
    result="Safety Population",
    before=len(adsl),
    after=len(safety),
)
```

## `trace.read()`

Records acquisition of a statistical input.

```python
trace.read(
    name,
    *,
    source=None,
    rows=None,
    columns=None,
    details=None,
)
```

- `name` — semantic input identity such as `"ADSL"`.
- `source` — optional physical source identity such as `"data/adsl.xpt"`. In a managed run with `log_file`, it is also registered as an input artifact for program-level provenance.
- `rows` — optional supplied row count.
- `columns` — optional supplied column count.
- `details` — optional descriptive metadata mapping.

```python
adsl = pd.read_sas("data/adsl.xpt", format="xport")
trace.read(
    "ADSL",
    source="data/adsl.xpt",
    rows=len(adsl),
    columns=len(adsl.columns),
)
```

TRACE Core does not require or retain the runtime DataFrame.

## `trace.check()`

Records an observation without asserting pass/fail correctness.

```python
trace.check(
    name,
    check,
    *,
    metrics=None,
    details=None,
)
```

- `name` — object being inspected.
- `check` — reviewer-readable observation.
- `metrics` — optional diagnostic mapping.
- `details` — optional descriptive metadata.

```python
trace.check(
    "ADSL",
    "treatment groups observed",
    metrics={"treatment_groups": 3},
)
```

Use `VALIDATE`, not `CHECK`, when the program is explicitly testing an expectation.

## `trace.filter()`

Records selection or exclusion of records, including analysis-population selection.

```python
trace.filter(
    name,
    condition,
    *,
    result=None,
    before=None,
    after=None,
    removed=None,
    details=None,
)
```

- `name` — source object being filtered.
- `condition` — reviewer-readable selection condition.
- `result` — optional semantic identity of the resulting analytical object or population.
- `before`, `after`, `removed` — optional non-negative record diagnostics.
- `details` — optional descriptive metadata.

```python
trace.filter(
    "ADSL",
    "SAFFL == 'Y'",
    result="Safety Population",
    before=len(adsl),
    after=len(safety),
)
```

If `before` and `after` are supplied and `removed` is omitted, TRACE derives `removed = before - after`. `after > before` is rejected for FILTER, and if all three diagnostics are supplied they must reconcile.

`result` preserves analytical result identity while `name` remains the source. TRACE does not define a separate `POPULATION` operation.

## `trace.sort()`

Records material ordering of an analytical object.

```python
trace.sort(
    name,
    *,
    by,
    ascending=None,
    details=None,
)
```

- `name` — object sorted.
- `by` — required sort variable or sequence of variables.
- `ascending` — optional boolean or sequence describing direction.
- `details` — optional descriptive metadata.

```python
adsl = adsl.sort_values(["TRT01A", "USUBJID"])
trace.sort("ADSL", by=["TRT01A", "USUBJID"], ascending=True)
```

Use SORT when ordering materially matters to subsequent analysis, derivation, reporting, or reproducibility.

## `trace.derive()`

Records creation of a named analytical concept or variable.

```python
trace.derive(
    variable,
    *,
    dataset=None,
    source=None,
    method=None,
    details=None,
)
```

- `variable` — derived variable or analytical concept.
- `dataset` — optional containing dataset.
- `source` — optional source variable or sequence of source variables.
- `method` — optional concise derivation method.
- `details` — optional descriptive metadata.

```python
adsl["AGEGR1"] = pd.cut(adsl["AGE"], bins=[0, 64, 200])
trace.derive(
    "AGEGR1",
    dataset="ADSL",
    source="AGE",
    method="age category",
)
```

## `trace.transform()`

Records a material representation or structural change when a more specific TRACE operation does not fit.

```python
trace.transform(
    name,
    transformation,
    *,
    source=None,
    result=None,
    details=None,
)
```

- `name` — analytical object being transformed.
- `transformation` — reviewer-readable transformation.
- `source` — optional source identity.
- `result` — optional result identity.
- `details` — optional descriptive metadata.

```python
trace.transform(
    "AE summary",
    "pivoted to reporting layout",
    source="ae_counts",
    result="ae_display",
)
```

## `trace.merge()`

Records combination of two analytical sources.

```python
trace.merge(
    left,
    right,
    *,
    on=None,
    how=None,
    result=None,
    left_rows=None,
    right_rows=None,
    result_rows=None,
    metrics=None,
    details=None,
)
```

- `left`, `right` — semantic identities of the two inputs.
- `on` — optional merge key or keys.
- `how` — optional merge method such as `"inner"`.
- `result` — optional semantic result identity.
- `left_rows`, `right_rows`, `result_rows` — optional non-negative row diagnostics.
- `metrics` — optional domain-specific diagnostics such as `matched_subjects` or `unmatched_keys`.
- `details` — optional descriptive metadata.

```python
adae_safety = adae.merge(adsl_safety, on="USUBJID", how="inner")
trace.merge(
    "ADAE",
    "Safety Population",
    on="USUBJID",
    how="inner",
    result="Safety ADAE",
    left_rows=len(adae),
    right_rows=len(adsl_safety),
    result_rows=len(adae_safety),
)
```

## `trace.aggregate()`

Records grouping, reduction, or summarization.

```python
trace.aggregate(
    name,
    *,
    by=None,
    result=None,
    method=None,
    rows=None,
    details=None,
)
```

- `name` — source being summarized.
- `by` — optional grouping variable or variables.
- `result` — optional summary identity.
- `method` — optional description such as `"unique participant count"`.
- `rows` — optional number of resulting rows.
- `details` — optional descriptive metadata.

```python
trace.aggregate(
    "Safety ADAE",
    by=["AESOC", "AEDECOD", "TRT01A"],
    result="AE incidence",
    method="unique participant count",
    rows=len(ae_summary),
)
```

## `trace.analyze()`

Records execution of a statistical analysis, model, estimator, or method.

```python
trace.analyze(
    source,
    analysis,
    *,
    method,
    population=None,
    result=None,
    details=None,
)
```

- `source` — analytical dataset or input.
- `analysis` — semantic analysis identity.
- `method` — required statistical method.
- `population` — optional analysis population.
- `result` — optional result identity.
- `details` — optional descriptive metadata.

```python
trace.analyze(
    "ADTTE",
    "Overall Survival",
    method="Kaplan-Meier",
    population="ITT",
    result="km_curve",
)
```

## `trace.validate()`

Records the outcome of an explicitly implemented expectation.

```python
trace.validate(
    name,
    check,
    *,
    passed,
    metrics=None,
    details=None,
)
```

- `name` — object or result being validated.
- `check` — implemented validation criterion.
- `passed` — required Python `bool` indicating whether that criterion passed.
- `metrics` — optional supporting diagnostics.
- `details` — optional descriptive metadata.

```python
trace.validate(
    "Safety Population",
    "participant count equals treatment totals",
    passed=safety_total == treatment_total,
    metrics={"participants": safety_total},
)
```

A passing event means only that the implemented criterion evaluated successfully. It does not establish broader statistical correctness. Non-boolean `passed` values are rejected.

## `trace.output()`

Records production of an output artifact.

```python
trace.output(
    name,
    path,
    *,
    format=None,
    rows=None,
    details=None,
)
```

- `name` — semantic output identity.
- `path` — required non-empty string or `Path` identifying the physical output.
- `format` — optional format description.
- `rows` — optional output row count.
- `details` — optional descriptive metadata.

```python
write_rtf(table, "outputs/tlf_population.rtf")
trace.output(
    "TLF_POPULATION",
    "outputs/tlf_population.rtf",
    format="RTF",
)
```

In a managed run with `log_file`, the output path is also registered as a program-level output artifact.

## `trace.step()`

Creates an optional logical execution scope.

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

STEP emits lifecycle evidence around a coarse analytical stage. Nested steps are supported, and events inside a step inherit its context. Steps should not be wrapped around every individual line or operation.

## `trace.log()` — advanced public escape hatch

```python
trace.log(
    operation,
    *,
    object=None,
    action,
    metrics=None,
    details=None,
    status=None,
)
```

Use the Tier 1 semantic helper whenever one fits. `trace.log()` exists for unusual structured events using TRACE's canonical operation vocabulary.

```python
trace.log(
    "CHECK",
    object="Treatment Mapping",
    action="reconciled against randomization specification",
    metrics={"unmapped_subjects": 0},
)
```

Common aliases are deliberately rejected rather than silently normalized. For example, use `FILTER` rather than `SUBSET` or `WHERE`, `MERGE` rather than `JOIN` or `COMBINE`, `READ` rather than `LOAD`, and `OUTPUT` rather than `EXPORT`.

## Public API boundary

| Classification | Meaning |
|---|---|
| Alpha public | Supported and deliberately exposed for Developer Preview feedback |
| Advanced public | Supported escape hatch, but not the preferred programming style |
| Internal | Implementation detail; no alpha compatibility commitment |
| Not in alpha | Deliberately deferred from the first release |

**Alpha public:** `Trace(...)`, context-managed lifecycle, all eleven semantic helpers, and `trace.step()`.

**Advanced public:** `trace.log()`.

**Internal:** `TraceEvent`, `TraceContext`, `Operation`, `Severity`, `Status`, renderers, provenance/spool/staging internals, logger internals, event factories, and step implementation objects.

**Not in alpha:** pandas/Polars/PyArrow integrations, custom public renderers or sinks, provenance configuration controls, automatic artifact hashing, environment fingerprinting, automatic instrumentation, and public recovery APIs for incomplete event spools.

Program-level provenance in the finalized managed `log_file` is implemented behavior; what remains deferred is additional public provenance configuration such as hashing or environment capture.

## Where to go next

- [Getting Started with TRACE](../guides/getting-started.md) — first complete TRACE workflow.
- [TRACE Core Operations v0.1](../framework/core-operations-v0.1.md) — canonical operation meanings.
- [Reviewing Statistical Programs with TRACE](../framework/reviewer-guide.md) — how to review TRACE evidence.
- [TRACE Statistical Programming Examples](../../examples/README.md) — executable public-data examples.

The design documents explain rationale and architecture history, but they are not required to use the alpha public API.
