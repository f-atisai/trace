# Comparative Design Review

**Phase:** 0 supporting design note  
**Status:** Adopt / reject / differentiate decisions  
**Reviewed projects:** `pdlog`, `pandas-log`, `TracePipe`, `dframe-trace`, `whylogs`  
**Review date:** 2026-09-03

## Purpose

TRACE should not be designed in isolation.

These projects address adjacent concerns:

- logging DataFrame transformations;
- automatically instrumenting pandas pipelines;
- row/cell provenance;
- structural pipeline observability;
- dataset profiling; and
- machine-readable execution or data summaries.

This note records what TRACE deliberately adopts, rejects, and does differently.

> TRACE records structured, statistical-programming-aware execution events that can be rendered as concise, review-ready logs and reused by machine-readable downstream consumers.

---

## Summary Matrix

| Project | Primary concern | TRACE adopts | TRACE rejects | TRACE distinction |
|---|---|---|---|---|
| `pdlog` | Dense production logging for pandas operations | concise one-line messages; operation-local feedback | DataFrame accessor as core API; pandas-method vocabulary as TRACE vocabulary | TRACE records statistical intent |
| `pandas-log` | Automatic feedback on ordinary pandas transformations | near-zero-friction activation; before/after transformation metadata; unobtrusive workflow | transparent interception as canonical semantics; pandas-only scope | TRACE prefers explicit semantic events, with automatic instrumentation optional |
| `TracePipe` | Row/cell lineage and provenance | provenance thinking; before/after evidence; derived reports | row/cell capture by default; runtime patching as primary architecture | TRACE records execution evidence, not full lineage |
| `dframe-trace` | Structural pipeline observability/debugging | optional dataframe backends; structural snapshots; queryable history | autopatching as canonical API; structural diffs as event meaning | semantic operation first, structural evidence second |
| `whylogs` | Statistical profiling and data/ML observability | structured metrics; serializable records; summaries rather than raw data | broad profiling as TRACE core; ML-observability scope | TRACE describes execution, not dataset distributions |

---

# 1. `pdlog`

## What it does

`pdlog` provides logging through a pandas DataFrame accessor such as:

```python
df = df.log.dropna()
```

It mirrors common pandas methods and emits compact messages intended to be useful in production logs.

Its own documentation distinguishes it from `pandas-log`: `pdlog` aims for dense single-line production feedback, while `pandas-log` is described as friendlier and more interactive.

## What TRACE adopts

### Dense, review-friendly output

TRACE should produce logs that can be scanned quickly:

```text
INFO [FILTER] [ADSL] SAFFL == 'Y' applied – N=754 → 720
```

### Feedback close to the operation

The logging statement should normally appear immediately after, or be directly associated with, the transformation it describes.

### Standard vocabulary for recurring operations

`pdlog` validates the usefulness of predefined conventions around common operations.

TRACE raises those conventions to the statistical-programming level:

```text
READ
FILTER
DERIVE
MERGE
VALIDATE
OUTPUT
```

## What TRACE rejects

### DataFrame accessor as the canonical API

TRACE should not require:

```python
df.trace.filter(...)
```

because TRACE events can describe variables, validations, analysis procedures, outputs, program lifecycle, and other non-DataFrame objects.

### pandas implementation vocabulary as TRACE vocabulary

These:

```python
df.query(...)
df.loc[...]
```

may represent the same TRACE operation:

```text
FILTER
```

The implementation mechanism must not define the domain meaning.

## What TRACE does differently

`pdlog` primarily answers:

> What did this pandas operation do?

TRACE answers:

> What meaningful statistical-programming operation occurred?

---

# 2. `pandas-log`

## What it does

`pandas-log` is a Python implementation inspired by R's `tidylog`.

Its goal is to provide feedback about common pandas operations such as:

```text
query
apply
merge
group_by
assign
dropna
reset_index
```

A particularly important ergonomic feature is that a user can enable logging around ordinary pandas code:

```python
import pandas_log

with pandas_log.enable():
    ...
```

and continue writing standard pandas expressions rather than replacing every transformation with a special logging API.

The project positions this as useful for long transformation pipelines where an unexpected result can otherwise be difficult to localize.

## What TRACE adopts

### A. Five-minute adoption must be real

`pandas-log` demonstrates a very strong adoption principle:

> Observability is much more likely to be used when it does not require rewriting the entire program.

TRACE should preserve this idea.

Adding TRACE to an established TLF program should not require architectural restructuring.

### B. Ordinary statistical code should remain ordinary statistical code

TRACE should not turn:

```python
safety = adsl.query("SAFFL == 'Y'")
```

into an unnatural transformation API such as:

```python
safety = trace.query_and_return_dataframe(...)
```

TRACE observes execution; it does not replace pandas.

### C. Before/after metadata is highly valuable

`pandas-log` reinforces that transformation feedback becomes useful when it explains the effect of an operation.

TRACE should standardize relevant metrics such as:

```json
{
  "before": 754,
  "after": 720
}
```

### D. Scoped activation is attractive

The conceptual pattern:

```python
with pandas_log.enable():
    ...
```

supports a useful TRACE design idea:

```python
with Trace("T14_01") as trace:
    ...
```

The meanings are different, but scoped execution context is ergonomically strong.

### E. Pipeline feedback should help localize unexpected results

TRACE should make a statistical pipeline narrate its meaningful execution history.

For example:

```text
READ ADSL
FILTER Safety population
DERIVE AGEGR1
AGGREGATE treatment × age group
VALIDATE expected treatment groups
OUTPUT T14_01
```

A reviewer should be able to see where an unexpected population or output emerged.

## What TRACE rejects

### A. Transparent interception as the canonical semantic source

The strongest difference is architectural.

`pandas-log` can add feedback while ordinary pandas methods execute.

TRACE should **not** rely on observing a pandas method and assuming that the method name fully captures statistical intent.

For example:

```python
df.query("SAFFL == 'Y'")
```

may clearly be a population filter.

But:

```python
df.assign(...)
```

could represent:

```text
DERIVE
TRANSFORM
CHECK
normalization
temporary implementation detail
```

Only the programmer or a domain-aware integration may know the intended meaning.

Therefore:

> Automatic instrumentation may capture structural facts, but explicit TRACE semantics remain authoritative.

### B. pandas-only execution model

TRACE must support statistical programming beyond pandas.

The event:

```text
FILTER ADSL using SAFFL == 'Y'
```

should mean the same whether implemented using:

```text
pandas
Polars
PyArrow
SQL
DuckDB
custom Python
```

### C. Logging every low-level DataFrame operation

Not every pandas operation deserves a TRACE event.

A TLF may contain dozens of incidental transformations that are implementation details.

TRACE should favor **meaningful execution events**, not maximal method coverage.

### D. Automatic messages as the source of truth

Even if an integration automatically detects a transformation, the resulting information should be converted into a structured TRACE Event.

Rendered feedback remains downstream.

## What TRACE does differently

`pandas-log` asks:

> What feedback can we automatically provide while pandas code runs?

TRACE asks:

> What execution events are meaningful enough to form the auditable narrative of a statistical program?

This leads to an important design hierarchy:

```text
programmer intent
      ↓
TRACE semantic event
      ↓
optional automatically collected metrics
      ↓
renderer / JSON / manifest / summary
```

rather than:

```text
intercept pandas method
      ↓
method name becomes semantic truth
```

## Design consequence

`pandas-log` makes a strong case for a future optional TRACE integration mode.

For example, TRACE may eventually support an opt-in pandas integration capable of deriving row counts or other structural metrics automatically.

But the canonical API remains explicit:

```python
trace.filter(
    "ADSL",
    "SAFFL == 'Y'",
    before=754,
    after=720,
)
```

or a future API where the objects allow metrics to be inferred while the programmer still supplies the semantic operation.

---

# 3. TracePipe

## What it does

TracePipe targets pandas provenance at much greater depth.

Its concerns include:

- row drops;
- changed cell values;
- merge provenance;
- row history;
- cell history; and
- debugging why a particular observation ended up in its current state.

## What TRACE adopts

### Provenance thinking

TRACE should preserve structured evidence of:

```text
what object
what operation
what condition/key/source
what before/after metrics
what result
```

### Reports derived from captured state

Execution summaries, QC summaries, manifests, and dashboards should be generated from TRACE Events.

### Different diagnostic depth can be useful

TRACE may eventually support routine and diagnostic levels of metadata collection.

The event semantics should stay stable across those levels.

## What TRACE rejects

### Full row/cell lineage by default

TRACE should not persist source or derived clinical values merely to explain an execution step.

Default behavior should remain:

```text
aggregate metadata, not record copies
```

### Runtime patching as primary behavior

Invisible instrumentation should not be the foundation of an audit-oriented semantic event model.

## What TRACE does differently

TracePipe asks:

> Why does this row or cell look like this?

TRACE asks:

> What did this statistical program do, and what execution evidence describes it?

---

# 4. `dframe-trace`

## What it does

`dframe-trace` focuses on structural observability across DataFrame pipeline steps.

Relevant information includes:

- row-count deltas;
- columns added or removed;
- dtype changes;
- null changes;
- memory changes.

It supports pandas and Polars while keeping those backend libraries optional, and offers context managers, decorators, and optional automatic patching.

## What TRACE adopts

### Optional backend integrations

This directly supports the TRACE Phase 0 decision:

```text
TRACE Core
├── pandas
├── polars
└── future adapters
```

### Structural snapshots instead of dataset copies

TRACE can safely enrich events with:

```json
{
  "rows": 754,
  "columns": 16
}
```

without retaining full data.

### Queryable execution history

The structured event stream should eventually support questions such as:

```text
show failed validations
show population-reducing filters
show outputs
show merges with unmatched records
```

### Context-manager ergonomics

This remains a strong candidate:

```python
with Trace("T14_01") as trace:
    ...
```

## What TRACE rejects

### Structural change as the event's meaning

This:

```text
rows: -34
```

is evidence.

This is meaning:

```text
FILTER ADSL using SAFFL == 'Y'
```

TRACE puts semantic intent first.

### Automatic patching as canonical behavior

Autopatching may be useful for optional diagnostics, but not as TRACE's primary contract.

## What TRACE does differently

`dframe-trace` provides structural pipeline observability.

TRACE provides semantic execution reporting.

---

# 5. `whylogs`

## What it does

`whylogs` creates structured statistical profiles describing datasets and model-related data.

Its profiles can contain metrics such as:

- counts;
- nulls;
- data types;
- distributions;
- cardinality;
- frequent values; and
- user-defined metrics.

The profiles are designed for serialization, aggregation, monitoring, and downstream validation.

## What TRACE adopts

### Structured state before presentation

This strongly reinforces TRACE's central decision:

```text
TRACE Event
    ├── .log renderer
    ├── JSON
    ├── execution manifest
    ├── QC summary
    └── dashboard
```

### Stable metric semantics

Prefer:

```json
{
  "before": 754,
  "after": 720
}
```

over:

```json
{
  "message": "N=754 -> 720"
}
```

### Aggregate summaries rather than raw records

This is particularly important for clinical data.

### Serialization as an architectural requirement

TRACE Events should remain serializable without requiring logger objects, DataFrames, file handles, or other live runtime objects.

## What TRACE rejects

### Broad statistical profiling by default

TRACE should not profile every variable distribution simply because it can.

### ML observability as core scope

TRACE's initial identity is statistical-programming execution reporting.

### Profiling as validation

A profile may provide evidence, but a TRACE `VALIDATE` event describes an explicit check and its result.

## What TRACE does differently

whylogs asks:

> What does this data statistically look like?

TRACE asks:

> What happened during this program's execution?

---

# 6. Cross-Project Decisions

## CR-01 — Statistical intent is canonical

TRACE vocabulary represents concepts such as:

```text
FILTER
DERIVE
MERGE
VALIDATE
OUTPUT
```

not implementation calls such as:

```text
query
assign
loc
dropna
```

## CR-02 — Structured events precede rendering

No TRACE consumer should need to parse human-readable log messages.

## CR-03 — Core TRACE remains dataframe-library independent

pandas, Polars, and other integrations are optional.

## CR-04 — Explicit semantic instrumentation is canonical

TRACE's authoritative meaning comes from explicit semantic events.

Automatic instrumentation may enrich or assist but must not redefine intent.

## CR-05 — Automatic metadata collection is encouraged where reliable

Integrations may infer:

```text
rows
columns
before
after
removed
null counts
merge counts
```

when doing so is deterministic and transparent.

## CR-06 — Automatic semantic inference is treated cautiously

Inferring:

```text
query → FILTER
```

may be straightforward.

Inferring:

```text
assign → DERIVE
```

may not be.

TRACE should distinguish **metric inference** from **semantic inference**.

This is an important architectural rule.

## CR-07 — No row/cell capture by default

Aggregate metrics and metadata are the normal TRACE evidence model.

## CR-08 — Successful runs must produce value

TRACE is not a debugging-only system.

A clean production execution should result in a useful review trail.

## CR-09 — Execution history must be queryable

The event model must support downstream questions without text parsing.

## CR-10 — TRACE should not absorb specialist problem spaces

TRACE should complement rather than replace:

```text
pdlog          dense pandas operation logging
pandas-log     automatic pandas feedback
TracePipe      row/cell lineage
dframe-trace   structural debugging
whylogs        data profiling
Python logging logging infrastructure
```

---

# 7. The Most Important Lesson from `pandas-log`

This comparison adds an important distinction to TRACE's architecture:

> **Automatic metric collection and automatic semantic classification are not the same thing.**

TRACE should be comfortable automating the first.

For example, given supported DataFrames, TRACE can safely determine:

```text
before = 754
after  = 720
removed = 34
```

But TRACE should be much more cautious about automatically deciding:

```text
this operation means FILTER
```

The programmer-facing semantic API should remain the authority.

This gives TRACE a practical middle ground:

```text
                EXPLICIT                     AUTOMATIC

Meaning         FILTER           ← programmer/domain API
Object          ADSL             ← programmer/context
Action          SAFFL == 'Y'     ← programmer/domain API

Metrics         before=754       ← integration may infer
                after=720        ← integration may infer
                removed=34       ← integration may derive

Rendering       INFO [...]       ← TRACE renderer
```

This preserves both:

- the low-friction lesson from `pandas-log`; and
- the auditable semantic precision TRACE needs.

---

# 8. Resulting TRACE Position

```text
pdlog
  └── dense pandas-operation logging

pandas-log
  └── automatic feedback around pandas pipelines

TracePipe
  └── row/cell lineage

dframe-trace
  └── structural dataframe observability

whylogs
  └── statistical data profiling

TRACE
  └── semantic statistical-program execution events
      ├── structured context
      ├── structured metrics
      ├── review-ready logs
      └── machine-readable downstream records
```

TRACE's key abstraction remains:

```text
TRACE Event
├── severity
├── operation
├── object
├── action
├── metrics
├── details
├── status
└── context
```

The comparison does not require changing the Phase 0 domain model.

It strengthens the separation between:

```text
semantic intent
```

and:

```text
automatically observed execution evidence
```

---

# 9. Design Guardrails

Future TRACE proposals should be tested against these questions:

1. Is this statistical-programming meaning or a library implementation detail?
2. Can it be expressed as structured event data?
3. Is semantic meaning explicit or being guessed from implementation syntax?
4. Can safe metrics be collected automatically instead?
5. Does this require pandas in TRACE core?
6. Does it unnecessarily capture subject-level values?
7. Does it introduce hidden monkeypatching?
8. Can a reviewer understand the event without pandas expertise?
9. Can downstream software consume it without parsing text?
10. Is it useful during a successful production run?
11. Does it preserve low-friction adoption?
12. Is a specialist package already better suited to the problem?

---

# 10. Sources

## `pdlog`

- https://pypi.org/project/pdlog/

## `pandas-log`

- https://github.com/eyaltrabelsi/pandas-log
- https://pypi.org/project/pandas-log/

## TracePipe

- https://github.com/gauthierpiarrette/tracepipe

## `dframe-trace`

- https://github.com/vimalnakrani08/dframe-trace
- https://pypi.org/project/dframe-trace/

## `whylogs`

- https://github.com/whylabs/whylogs
- https://whylogs.readthedocs.io/

---

# 11. Impact on Phase 0

The Phase 0 domain model remains unchanged.

This comparative review strengthens:

- event-first architecture;
- semantic operations;
- structured metrics;
- dataframe independence;
- serialization readiness;
- summary-over-raw-data defaults; and
- rendering as a downstream concern.

It adds the following explicit rule:

> **TRACE may automate observation of execution evidence, but semantic intent should remain explicit unless an integration can infer it unambiguously and transparently.**
