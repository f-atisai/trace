# TRACE Phase 8 — Step-Level Instrumentation

**Phase:** 8 — Design Step-Level Instrumentation  
**Status:** Draft normative step instrumentation specification  
**Scope:** Logical execution stages, `trace.step(...)`, nested context, timing, failure behavior, and interaction with program lifecycle

## 1. Purpose

TLF programs naturally consist of logical stages.

Typical examples:

```text
Read source data
Select analysis population
Derive analysis variables
Generate statistics
Format table
Write output
```

TRACE should make those stages visible without forcing programmers to redesign their code around decorators or a workflow engine.

The preferred API is:

```python
with trace.step("Analysis population"):
    safety = adsl.query("SAFFL == 'Y'")

    trace.filter(
        "ADSL",
        "SAFFL == 'Y'",
        before=len(adsl),
        after=len(safety),
    )
```

Possible output:

```text
INFO [STEP] [Analysis population] started
INFO [FILTER] [ADSL] SAFFL == 'Y' applied – N=754 → 720
INFO [STEP] [Analysis population] completed – 0.031s
```

> **Steps describe logical execution stages; Tier 1 operations still describe what happened inside them.**

---

# 2. Step Is a Scope, Not a Core Operation

Phase 1 defined the canonical statistical operations:

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

A step is different.

Examples:

```text
Analysis population
Demographics derivation
Safety summary
Kaplan-Meier analysis
Table formatting
QC comparison
```

These are execution scopes containing one or more semantic operations.

Therefore `STEP` should not be added to the Phase 1 core operation vocabulary as a peer of `FILTER`, `DERIVE`, or `ANALYZE`.

Instead, step events belong to TRACE's execution/lifecycle layer.

---

# 3. Preferred API

Canonical form:

```python
with trace.step("Analysis population"):
    ...
```

No separate step object should normally be required.

Inside the block, ordinary TRACE methods remain unchanged:

```python
with trace.step("Analysis population"):
    safety = adsl.query("SAFFL == 'Y'")

    trace.filter(
        "ADSL",
        "SAFFL == 'Y'",
        before=len(adsl),
        after=len(safety),
    )
```

This preserves the Phase 2 principle:

> TRACE should complement the code, not dominate it.

---

# 4. Step Start Event

Entering a step should emit one step-start event.

Example:

```python
with trace.step("Analysis population"):
    ...
```

Possible rendering:

```text
INFO [STEP] [Analysis population] started
```

Conceptual structured representation:

```json
{
  "operation": "STEP",
  "object": "Analysis population",
  "action": "started",
  "status": null
}
```

Although `STEP` appears in rendering, it is a lifecycle/system event category rather than a statistical core operation.

---

# 5. Step Completion Event

Normal step exit should emit:

```text
INFO [STEP] [Analysis population] completed – 0.031s
```

Conceptually:

```json
{
  "operation": "STEP",
  "object": "Analysis population",
  "action": "completed",
  "status": "SUCCESS",
  "metrics": {
    "duration_seconds": 0.031
  }
}
```

As with program lifecycle, duration should be stored numerically and rendered separately.

---

# 6. Failed Step Event

If an unhandled exception leaves the step:

```python
with trace.step("Analysis population"):
    raise ValueError("SAFFL missing")
```

TRACE should emit:

```text
ERROR [STEP] [Analysis population] failed – ValueError
```

Conceptually:

```json
{
  "operation": "STEP",
  "object": "Analysis population",
  "action": "failed",
  "status": "FAIL",
  "details": {
    "exception_type": "ValueError"
  }
}
```

The exception must then propagate normally.

---

# 7. Failure Propagation

`trace.step(...)` must not suppress errors.

Behavior:

```text
record failed step
    ↓
exit step scope
    ↓
re-raise original exception
```

If the step is inside:

```python
with Trace("T14_01") as trace:
    ...
```

the program-level context manager will then also observe the exception and emit the failed program END event.

Example:

```text
INFO  [START] [T14_01] execution started
INFO  [STEP]  [Analysis population] started
ERROR [STEP]  [Analysis population] failed – ValueError
ERROR [END]   [T14_01] execution failed – ValueError
```

This duplication is intentional because the events describe different scopes.

---

# 8. Step Context

Events emitted inside a step should inherit the active step name as structured context.

Example:

```python
with trace.step("Analysis population"):
    trace.filter(
        "ADSL",
        "SAFFL == 'Y'",
        before=754,
        after=720,
    )
```

Conceptually:

```json
{
  "operation": "FILTER",
  "object": "ADSL",
  "context": {
    "program": "T14_01",
    "step": "Analysis population"
  }
}
```

The text renderer does not need to repeat the step name on every operation line.

The structured event should still retain it.

---

# 9. Why Step Context Matters

Structured step context enables downstream questions such as:

```text
Which operations occurred during analysis-population selection?
Which validations failed during table generation?
How long did each execution stage take?
Which outputs were generated during which step?
```

This is especially valuable for:

```text
batch review
QC summaries
execution manifests
performance diagnostics
JSON logs
clinical-programming audit trails
```

---

# 10. Step Naming

The first argument should be a human-readable semantic label:

```python
with trace.step("Analysis population"):
    ...
```

Good examples:

```text
Read source data
Analysis population
Derive analysis variables
Generate statistics
Format table
Write output
QC comparison
```

Avoid forcing machine-style identifiers such as:

```text
STEP_01
stage_2
func_aggregate_data
```

Programmers may use those if useful, but TRACE should optimize for readable execution narratives.

---

# 11. Step Name Is Not a Python Function Name

TRACE should not infer step labels from call-stack or function names.

For example:

```python
def build_pop():
    ...
```

should not automatically become:

```text
[STEP] [build_pop]
```

unless a future decorator explicitly requests that behavior.

The explicit label:

```python
with trace.step("Analysis population"):
```

is clearer for statistical review.

---

# 12. Step Duration

Step duration should use the same timing principles as program lifecycle.

Store:

```text
duration_seconds
```

Use a monotonic clock internally.

Render:

```text
0.031s
```

or another canonical duration format.

Step durations will usually be shorter than program durations, so the renderer may choose compact formatting.

---

# 13. Program Lifecycle Is Optional

This should work:

```python
trace = Trace("T14_01")

with trace.step("Analysis population"):
    ...
```

even without:

```python
with Trace(...) as trace:
```

The step context itself provides an explicit bounded scope.

Therefore step instrumentation should not depend on automatic program lifecycle being active.

---

# 14. Run Identity Still Applies

A step created from a `Trace` instance should inherit that instance's `run_id`.

Conceptually:

```text
run_id
program
study
step
```

become part of event context.

This allows events to be correlated even when only step-level contexts are used.

---

# 15. Nested Steps

Larger programs may benefit from nested logical scopes.

Example:

```python
with trace.step("Generate statistics"):

    with trace.step("Demographics"):
        ...

    with trace.step("Baseline characteristics"):
        ...
```

TRACE should support nested steps eventually.

Recommended model:

```text
Generate statistics
    ├── Demographics
    └── Baseline characteristics
```

Nested steps should maintain a step path rather than overwrite parent context.

---

# 16. Step Path

For nested steps, structured context should support a hierarchy.

Conceptually:

```json
{
  "step": "Demographics",
  "step_path": [
    "Generate statistics",
    "Demographics"
  ]
}
```

Exact field naming may be refined later.

The important requirement is that parent-child scope is not lost.

---

# 17. Initial Nested-Step Policy

Phase 8 recommendation:

- allow nested steps;
- maintain an internal stack;
- each event inherits the active step path;
- step START/END events pair correctly;
- exiting a child restores the parent step context.

This is more useful than prohibiting nesting and does not require a large public API.

---

# 18. Example Nested Output

Code:

```python
with trace.step("Generate statistics"):
    with trace.step("Demographics"):
        trace.aggregate(
            "ADSL",
            by=["TRT01A", "SEX"],
            result="summary",
        )
```

Possible text output:

```text
INFO [STEP]      [Generate statistics] started
INFO [STEP]      [Demographics] started
INFO [AGGREGATE] [ADSL] summarized – by=TRT01A,SEX, result=summary
INFO [STEP]      [Demographics] completed – 0.014s
INFO [STEP]      [Generate statistics] completed – 0.021s
```

The text renderer need not visually indent nested steps initially.

Structured context preserves hierarchy.

---

# 19. Step Failure in Nested Scopes

If a child step fails:

```python
with trace.step("Generate statistics"):
    with trace.step("Demographics"):
        raise ValueError()
```

expected event sequence:

```text
INFO  [STEP] [Generate statistics] started
INFO  [STEP] [Demographics] started
ERROR [STEP] [Demographics] failed – ValueError
ERROR [STEP] [Generate statistics] failed – ValueError
```

If inside automatic program lifecycle:

```text
ERROR [END] [T14_01] execution failed – ValueError
```

Each active scope records its own failed boundary while the exception propagates.

---

# 20. No Implicit Step Creation

TRACE should not automatically create steps around every operation.

Avoid behavior such as:

```text
FILTER call → implicit FILTER step
DERIVE call → implicit DERIVE step
```

That would add noise and blur the distinction between scopes and operations.

Steps are programmer-defined logical stages.

---

# 21. No Decorator Requirement

A decorator API may be useful later:

```python
@trace.step("Generate statistics")
def generate_statistics(...):
    ...
```

But it should not be required.

The context-manager form should remain the canonical initial step API because:

- scope is visible in-place;
- no function refactoring is necessary;
- it works with procedural TLF scripts;
- it keeps instrumentation close to the relevant code.

---

# 22. Potential Decorator Later

If decorators are introduced, they should use the same underlying step machinery.

Conceptually:

```text
context manager
        ┐
decorator
        ├──→ Step scope state
manual future API
        ┘
```

There should not be separate semantics for decorated and context-managed steps.

---

# 23. Step Metadata

A minimal future extension could allow optional metadata:

```python
with trace.step(
    "Analysis population",
    details={"population": "Safety"},
):
    ...
```

However, the initial API should remain:

```python
trace.step(name)
```

Additional metadata should be added only if real clinical examples demonstrate clear value.

---

# 24. Proposed Initial Signature

Recommended:

```python
trace.step(name)
```

returning a context manager.

Conceptually:

```python
with trace.step("Analysis population"):
    ...
```

The step context manager should not require users to instantiate another public class directly.

---

# 25. Relationship to `START` / `END`

Program lifecycle uses:

```text
START
END
```

Step lifecycle uses:

```text
STEP started
STEP completed
STEP failed
```

This distinction keeps program boundaries visually separate from internal execution stages.

Do not render step boundaries as:

```text
[START] [Analysis population]
[END] [Analysis population]
```

because that would make program and step lifecycle ambiguous.

---

# 26. Why `STEP` Rendering Is Useful

The rendered pattern:

```text
[STEP] [Analysis population] started
```

is immediately understandable and avoids adding multiple new operation terms such as:

```text
STEP_START
STEP_END
STAGE_START
STAGE_END
```

Structured fields already capture status and action.

---

# 27. Step Events and Canonical Vocabulary

Although text rendering uses `STEP`, `STEP` is a reserved system category.

It should not become a valid generic statistical operation in:

```python
trace.log(...)
```

for ordinary users.

Users should create step boundaries through:

```python
with trace.step(...):
```

This preserves lifecycle consistency.

---

# 28. Step State Stack

Internally, a `Trace` instance should conceptually maintain:

```text
[]
```

then:

```text
["Generate statistics"]
```

then:

```text
["Generate statistics", "Demographics"]
```

and restore the stack correctly on exit.

The active stack is inherited into operation events.

---

# 29. Step Object Identity

The step label itself should serve as the semantic object for step boundary events.

Example:

```text
operation = STEP
object    = Analysis population
action    = started/completed/failed
```

This follows the lifecycle pattern established in Phase 7.

---

# 30. Step Status and Severity

Recommended mapping:

```text
step started
    status   = None
    severity = INFO

step completed
    status   = SUCCESS
    severity = INFO

step failed
    status   = FAIL
    severity = ERROR
```

This mirrors program lifecycle.

---

# 31. Step Exception Details

Failed steps should capture at minimum:

```text
exception_type
```

Potentially:

```text
exception_message
```

subject to the same privacy considerations defined for program lifecycle.

Do not automatically capture locals, dataframe values, or subject-level data.

---

# 32. Step Instrumentation Is Observational

A step must not:

```text
change dataframe behavior
retry operations
commit/rollback data
manage transactions
parallelize execution
schedule work
control workflow dependencies
```

TRACE is not a workflow orchestrator.

A step is an execution-observation scope.

---

# 33. Typical Clinical Example

```python
with Trace("T14_01") as trace:

    with trace.step("Read source data"):
        adsl = pd.read_parquet("adsl.parquet")
        trace.read(
            "ADSL",
            source="adsl.parquet",
            rows=len(adsl),
            columns=len(adsl.columns),
        )

    with trace.step("Analysis population"):
        safety = adsl.loc[adsl["SAFFL"] == "Y"].copy()
        trace.filter(
            "ADSL",
            "SAFFL == 'Y'",
            before=len(adsl),
            after=len(safety),
        )

    with trace.step("Derive analysis variables"):
        safety["AGEGR1"] = pd.cut(
            safety["AGE"],
            bins=[0, 65, float("inf")],
            labels=["<65", ">=65"],
        )
        trace.derive(
            "AGEGR1",
            dataset="ADSL",
            source="AGE",
        )

    with trace.step("Generate statistics"):
        summary = (
            safety.groupby(["TRT01A", "AGEGR1"])
            .size()
            .reset_index(name="N")
        )
        trace.aggregate(
            "ADSL",
            by=["TRT01A", "AGEGR1"],
            result="summary",
        )

    with trace.step("Write output"):
        summary.to_excel("T14_01.xlsx")
        trace.output(
            "T14_01",
            "T14_01.xlsx",
            rows=len(summary),
        )
```

Possible output:

```text
INFO [START]     [T14_01] execution started
INFO [STEP]      [Read source data] started
INFO [READ]      [ADSL] loaded – N=754, Vars=16
INFO [STEP]      [Read source data] completed – 0.042s
INFO [STEP]      [Analysis population] started
INFO [FILTER]    [ADSL] SAFFL == 'Y' applied – N=754 → 720
INFO [STEP]      [Analysis population] completed – 0.031s
INFO [STEP]      [Derive analysis variables] started
INFO [DERIVE]    [AGEGR1] created – dataset=ADSL, source=AGE
INFO [STEP]      [Derive analysis variables] completed – 0.006s
INFO [STEP]      [Generate statistics] started
INFO [AGGREGATE] [ADSL] summarized – by=TRT01A,AGEGR1, result=summary
INFO [STEP]      [Generate statistics] completed – 0.018s
INFO [STEP]      [Write output] started
INFO [OUTPUT]    [T14_01] written – T14_01.xlsx
INFO [STEP]      [Write output] completed – 0.090s
INFO [END]       [T14_01] execution completed – 00:00:00.19
```

---

# 34. When Steps Are Appropriate

Use steps for meaningful logical stages.

Good:

```text
Analysis population
Derive analysis variables
Generate statistics
QC comparison
Write output
```

Avoid:

```text
Create temporary variable x
Reset index
Rename column
Call helper function
```

A step should help someone reviewing the log understand program structure.

---

# 35. Step Granularity Principle

A practical rule:

> If a stage would deserve a short comment or section header in the TLF program, it is probably a reasonable TRACE step.

This keeps step instrumentation useful without becoming noisy.

---

# 36. Documentation Guidance

Basic tutorials should not require steps.

Progressive disclosure should remain:

```text
Level 1
    Trace(...)
    Tier 1 operation helpers

Level 2
    with Trace(...) lifecycle

Level 3
    with trace.step(...)

Level 4
    integrations / decorators / advanced outputs
```

This preserves five-minute adoption.

---

# 37. Phase 8 Decisions

**P8-01** — TRACE provides explicit logical execution scopes through:

```python
with trace.step(name):
    ...
```

**P8-02** — Step instrumentation is optional.

**P8-03** — Steps are execution scopes, not replacements for Tier 1 statistical operations.

**P8-04** — Step entry emits an INFO step-start event.

**P8-05** — Normal step exit emits an INFO step-completed event with `SUCCESS` and `duration_seconds`.

**P8-06** — Exceptional step exit emits an ERROR step-failed event with `FAIL`.

**P8-07** — Step failures re-raise the original exception.

**P8-08** — Events inside a step inherit structured step context.

**P8-09** — Step duration uses a monotonic clock.

**P8-10** — Step instrumentation works with or without program-level context-manager lifecycle.

**P8-11** — Nested steps are supported through an internal scope stack.

**P8-12** — Nested event context preserves the full step path.

**P8-13** — `STEP` is a reserved lifecycle/system event category, not a new Phase 1 statistical operation.

**P8-14** — Users should create step events through `trace.step()`, not manually through `trace.log("STEP", ...)`.

**P8-15** — Decorators may be added later but must use the same underlying step semantics.

**P8-16** — Steps remain observational and do not become workflow-control constructs.

---

# 38. Acceptance Criteria

Phase 8 is complete when:

1. programmers can group meaningful operations into named logical scopes;
2. step boundaries are automatically recorded;
3. step duration is captured;
4. step failures are visible without suppressing exceptions;
5. operation events retain their existing Tier 1 semantics inside steps;
6. active step context is available in structured events;
7. nested steps preserve hierarchy correctly;
8. step usage remains optional;
9. no decorators are required;
10. step instrumentation does not turn TRACE into a workflow engine.

---

# 39. Outcome

TRACE can now represent three execution layers:

```text
Program lifecycle
    START / END

Logical stages
    STEP

Statistical operations
    READ / FILTER / DERIVE / ANALYZE / OUTPUT / ...
```

Example:

```text
START T14_01
    STEP Analysis population
        FILTER ADSL
    STEP Generate statistics
        AGGREGATE ADSL
    STEP Write output
        OUTPUT T14_01
END T14_01
```

The governing principle is:

> **Steps make program structure visible while ordinary TRACE operations remain the source of statistical meaning.**
