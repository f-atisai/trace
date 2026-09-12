# TRACE Phase 8 — Step-Level Instrumentation

**Phase:** 8 — Design Step-Level Instrumentation  
**Status:** Draft normative step specification  
**Scope:** Logical execution stages, `trace.step(...)`, context, timing, failure behavior, and nesting

## 1. Decision

TRACE supports logical program stages through a context API:

```python
with trace.step("Analysis population"):
    safety = adsl.query("SAFFL == 'Y'")
    trace.filter("ADSL", "SAFFL == 'Y'", before=len(adsl), after=len(safety))
```

Possible output:

```text
INFO [STEP] [Analysis population] started
INFO [FILTER] [ADSL] SAFFL == 'Y' applied – N=754 → 720
INFO [STEP] [Analysis population] completed – 0.031s
```

> **Steps describe logical execution stages; statistical operations describe what happened inside them.**

`STEP` belongs to TRACE's lifecycle/system layer, not the canonical statistical-operation vocabulary defined in [`../framework/core-operations-v0.1.md`](../framework/core-operations-v0.1.md).

## 2. Step lifecycle

Entering a step emits one start event. Normal exit emits one successful completion event with elapsed duration. An unhandled exception emits a failed step event and then propagates normally.

Conceptually:

```text
INFO  [STEP] [Analysis population] started
...
INFO  [STEP] [Analysis population] completed – 0.031s
```

or:

```text
INFO  [STEP] [Analysis population] started
ERROR [STEP] [Analysis population] failed – ValueError
```

A failed step inside a context-managed program may therefore produce both a failed STEP event and a failed program END event. They describe different scopes.

Duration follows the lifecycle rules in [`lifecycle.md`](lifecycle.md): store numeric `duration_seconds`, use monotonic timing, and leave presentation to the renderer.

## 3. Step context

Events emitted inside a step inherit the active step identity as structured context:

```python
with trace.step("Analysis population"):
    trace.filter(
        "ADSL",
        "SAFFL == 'Y'",
        before=754,
        after=720,
    )
```

Conceptually the FILTER event carries:

```json
{
  "context": {
    "step": "Analysis population"
  }
}
```

Existing program, study, and run context remain inherited. Step context supplements rather than replaces them.

The context model itself is defined in [`domain-model.md`](domain-model.md).

## 4. Naming and granularity

Step names should describe meaningful analytical stages rather than implementation details.

Prefer:

```text
Analysis population
Baseline derivations
Safety summary
Overall survival analysis
Table formatting
QC comparison
```

Avoid granular names such as:

```text
Create dataframe
Rename columns
Run groupby
Call helper
Write temporary file
```

A useful rule is:

> **Use a step when its name helps a reviewer understand the program's analytical structure.**

TRACE should not require a step around every operation. Operations remain useful without steps, and small programs may need no explicit steps at all.

## 5. Interaction with program lifecycle

Steps may be used inside either construction style:

```python
trace = Trace("T14_01")

with trace.step("Analysis population"):
    ...
```

or:

```python
with Trace("T14_01") as trace:
    with trace.step("Analysis population"):
        ...
```

The second form additionally provides automatic program START/END events. Step behavior must not depend on the program context manager being active.

## 6. Nested steps

Nested steps may be useful for genuinely hierarchical workflows, but should remain uncommon because excessive nesting makes logs noisy.

If supported, context should behave as a stack:

```text
Program
└── Safety analysis
    └── Adverse-event summary
```

Events inside the inner scope should retain enough structured context to reconstruct that hierarchy without repeating the full path in every human-readable message.

Implementation details for parent identifiers or internal stacks are deferred until needed.

## 7. Failure and safety rules

`trace.step(...)` must not suppress or replace the underlying exception. The original program exception takes precedence over any secondary TRACE logging failure.

Safe exception metadata may be recorded under the same privacy constraints as program lifecycle events. TRACE should not assume arbitrary exception messages are safe for every sink.

Step exit must also restore the previous context reliably, including when the block fails.

## 8. Example

```python
with Trace("T14_01") as trace:
    adsl = pd.read_csv("adsl.csv")
    trace.read("ADSL", rows=len(adsl), columns=len(adsl.columns))

    with trace.step("Analysis population"):
        safety = adsl.loc[adsl["SAFFL"] == "Y"].copy()
        trace.filter("ADSL", "SAFFL == 'Y'", before=len(adsl), after=len(safety))

    with trace.step("Safety summary"):
        summary = safety.groupby("TRT01A").size().reset_index(name="N")
        trace.aggregate("Safety Population", by="TRT01A", result="summary")
```

Possible output:

```text
INFO [START]     [T14_01] execution started
INFO [READ]      [ADSL] loaded – N=754, Vars=16
INFO [STEP]      [Analysis population] started
INFO [FILTER]    [ADSL] SAFFL == 'Y' applied – N=754 → 720
INFO [STEP]      [Analysis population] completed – 0.031s
INFO [STEP]      [Safety summary] started
INFO [AGGREGATE] [Safety Population] summarized – by=TRT01A
INFO [STEP]      [Safety summary] completed – 0.018s
INFO [END]       [T14_01] execution completed – 0.071s
```

## 9. Related specifications

- [`lifecycle.md`](lifecycle.md) — timing, exception propagation, and program lifecycle.
- [`domain-model.md`](domain-model.md) — event context, status, metrics, and severity.
- [`../framework/core-operations-v0.1.md`](../framework/core-operations-v0.1.md) — canonical statistical operations.
- [`reviewer-experience.md`](reviewer-experience.md) — reviewer-facing guidance on useful versus noisy instrumentation.
