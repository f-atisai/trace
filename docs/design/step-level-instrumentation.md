# TRACE Phase 8 — Step-Level Instrumentation

**Phase:** 8 — Design Step-Level Instrumentation  
**Status:** Draft normative step specification  
**Scope:** Logical execution stages, `trace.step(...)`, context, timing, failure behavior, and nesting

## 1. Decision

TRACE supports logical program stages through a context API:

```python
with trace.step("Safety Population"):
    safety = adsl.loc[adsl["SAFFL"] == "Y"].copy()
    trace.filter(
        "ADSL",
        "SAFFL == 'Y'",
        before=len(adsl),
        after=len(safety),
    )
```

Possible output:

```text
INFO [STEP] [Safety Population] started
INFO [FILTER] [ADSL] SAFFL == 'Y' applied – N=254 → 249
INFO [STEP] [Safety Population] completed – 0.031s
```

> **Steps describe logical execution stages; statistical operations describe what happened inside them.**

`STEP` belongs to TRACE's lifecycle/system layer, not the canonical statistical-operation vocabulary defined in [TRACE Core Operations v0.1](../framework/core-operations-v0.1.md).

## 2. Step lifecycle

Entering a step emits one start event. Normal exit emits one successful completion event with elapsed duration. An unhandled exception emits a failed step event and then propagates normally.

```text
INFO  [STEP] [Safety Population] started
...
INFO  [STEP] [Safety Population] completed – 0.031s
```

or:

```text
INFO  [STEP] [Safety Population] started
ERROR [STEP] [Safety Population] failed – ValueError
```

A failed step inside a context-managed program may therefore produce both a failed STEP event and a failed program END event. They describe different scopes.

Duration follows the lifecycle rules in [TRACE Phase 7 — Lifecycle Behavior](lifecycle.md): store numeric `duration_seconds`, use monotonic timing, and leave presentation to the renderer.

## 3. Step context

Events emitted inside a step inherit the active step identity as structured context. Existing program, study, and run context remain inherited; step context supplements rather than replaces them.

Nested steps may additionally retain a structured `step_path` so hierarchy can be reconstructed without repeating the full path in every human-readable message.

The context model itself is defined in [TRACE Domain Model Specification](domain-model.md).

## 4. Naming and granularity

Step names should describe meaningful analytical stages rather than implementation details.

Prefer:

```text
Read analysis data
Safety Population
Baseline derivations
Treatment-emergent adverse events
Overall Survival analysis
Write table
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

> **Use a step when its name helps a reviewer understand the program's analytical structure.**

TRACE should not require a step around every operation. Successful steps add two lifecycle events, so excessive instrumentation creates noise quickly. Small programs may need no explicit steps at all.

## 5. Steps are explicit

TRACE does not infer steps automatically from Python functions, notebook cells, source-code blocks, or Quarto headings.

A programmer may choose a step name that aligns with a Quarto section or program section, but the relationship is intentional rather than automatic. This keeps TRACE independent of authoring environment and prevents structural noise from becoming execution semantics.

## 6. Interaction with program lifecycle

Steps work with either construction style:

```python
trace = Trace("T14_01")
with trace.step("Safety Population"):
    ...
```

or:

```python
with Trace("T14_01") as trace:
    with trace.step("Safety Population"):
        ...
```

The second form additionally provides automatic program START/END events. Step behavior must not depend on the program context manager being active.

## 7. Nested steps

Nested steps may be useful for genuinely hierarchical workflows, but should remain uncommon because excessive nesting makes logs noisy.

```text
Program
└── Safety analysis
    └── Adverse-event summary
```

Events inside the inner scope should retain enough structured context to reconstruct that hierarchy without repeating the full path in every human-readable message.

## 8. Failure and safety rules

`trace.step(...)` must not suppress or replace the underlying exception. The original program exception takes precedence over any secondary TRACE logging failure.

Safe exception metadata may be recorded under the same privacy constraints as program lifecycle events. TRACE should not assume arbitrary exception messages are safe for every sink.

Step exit must restore the previous context reliably, including when the block fails.

## 9. Example

```python
with Trace("T14_01") as trace:
    adsl = pd.read_parquet("analysis/adsl.parquet")
    trace.read(
        "ADSL",
        source="analysis/adsl.parquet",
        rows=len(adsl),
        columns=len(adsl.columns),
    )

    with trace.step("Safety Population"):
        safety = adsl.loc[adsl["SAFFL"] == "Y"].copy()
        trace.filter(
            "ADSL",
            "SAFFL == 'Y'",
            before=len(adsl),
            after=len(safety),
        )

    with trace.step("Demographic summary"):
        summary = safety.groupby(["TRT01A", "SEX"]).size().reset_index(name="N")
        trace.aggregate(
            "Safety Population",
            by=["TRT01A", "SEX"],
            result="demographics_summary",
        )
```

Possible output:

```text
INFO [START]     [T14_01] execution started
INFO [READ]      [ADSL] loaded – N=254, Vars=16
INFO [STEP]      [Safety Population] started
INFO [FILTER]    [ADSL] SAFFL == 'Y' applied – N=254 → 249
INFO [STEP]      [Safety Population] completed – 0.031s
INFO [STEP]      [Demographic summary] started
INFO [AGGREGATE] [Safety Population] summarized – by=TRT01A,SEX, result=demographics_summary
INFO [STEP]      [Demographic summary] completed – 0.018s
INFO [END]       [T14_01] execution completed – 0.071s
```

The step name can make the analytical result concept visible to a reviewer without changing FILTER's source identity or requiring a new `POPULATION` operation.

## 10. Related specifications

- [TRACE Phase 7 — Lifecycle Behavior](lifecycle.md) — timing, exception propagation, and program lifecycle.
- [TRACE Domain Model Specification](domain-model.md) — event context, status, metrics, and severity.
- [TRACE Core Operations v0.1](../framework/core-operations-v0.1.md) — canonical statistical operations.
- [TRACE Reviewer Experience](reviewer-experience.md) — reviewer-facing evidence and diagnostic origins.
- [Using TRACE with Quarto](../guides/quarto.md) — optional Quarto workflow without automatic step inference.
