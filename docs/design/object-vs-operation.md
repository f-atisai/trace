# TRACE Phase 4 — Object vs Operation

**Phase:** 4 — Resolve the Object-versus-Operation API Boundary  
**Status:** Draft normative architecture specification  
**Scope:** Core API ownership boundary, object identity, and integration responsibilities

## 1. Decision

TRACE Core will use a semantic, object-independent API.

The canonical style is:

```python
trace.filter(
    "ADSL",
    "SAFFL == 'Y'",
    before=754,
    after=720,
)
```

not:

```python
trace.filter(
    adsl,
    "SAFFL == 'Y'",
    name="ADSL",
)
```

The core library records what the statistical program did.

It does not require ownership of, or direct access to, the underlying dataframe or dataset object.

> **TRACE Core records semantic execution events. Integrations may inspect runtime objects to enrich those events.**

---

## 2. Why This Boundary Matters

TRACE is intended to work across statistical-programming backends.

The core API must therefore remain independent from:

```text
pandas
Polars
PyArrow
DuckDB
SQL engines
custom dataset classes
future statistical-programming runtimes
```

If the core methods require concrete dataframe objects, backend assumptions begin leaking into the event model and public API.

That creates several long-term problems:

- backend-specific type handling;
- optional dependency complexity;
- lifecycle and serialization issues;
- difficult testing;
- hidden object retention risks;
- ambiguous object naming;
- temptation to perform transformations inside TRACE;
- pressure to infer semantics from implementation methods.

The canonical API should avoid those problems entirely.

---

# 3. Canonical Core Style

The core API receives semantic identifiers and structured evidence.

Examples:

```python
trace.read(
    "ADSL",
    rows=754,
    columns=16,
    source="analysis/adsl.parquet",
)
```

```python
trace.filter(
    "ADSL",
    "SAFFL == 'Y'",
    before=754,
    after=720,
)
```

```python
trace.sort(
    "ADAE",
    by=["USUBJID", "AESTDTC"],
)
```

```python
trace.derive(
    "AGEGR1",
    dataset="ADSL",
    source="AGE",
)
```

```python
trace.merge(
    "ADAE",
    "ADSL",
    on="USUBJID",
    how="left",
    result="ADAE_ANALYSIS",
    left_rows=4127,
    right_rows=754,
    result_rows=4127,
)
```

```python
trace.aggregate(
    "ADSL",
    by=["TRT01A", "AGEGR1"],
    result="summary",
)
```

```python
trace.output(
    "T14_01",
    "T14_01.xlsx",
    rows=42,
)
```

The core API therefore describes:

```text
semantic object identity
operation intent
structured execution evidence
context
```

rather than concrete runtime objects.

---

# 4. Reversal of the Phase 3 `read()` Candidate

Phase 3 left this candidate:

```python
trace.read(adsl, "ADSL")
```

because it offered convenient automatic dataframe inspection.

Phase 4 intentionally changes that recommendation.

The canonical core form is now:

```python
trace.read(
    "ADSL",
    rows=754,
    columns=16,
)
```

or:

```python
trace.read(
    "ADSL",
    source="adsl.csv",
    rows=754,
    columns=16,
)
```

This creates stronger consistency across Tier 1 methods:

```python
trace.read("ADSL", ...)
trace.filter("ADSL", ...)
trace.sort("ADSL", ...)
trace.aggregate("ADSL", ...)
trace.validate("ADSL", ...)
```

It also resolves the only major argument-order inconsistency identified in Phase 3.

---

# 5. Revised Core `read()` Signature

## Recommended signature

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

Example:

```python
adsl = pd.read_csv("adsl.csv")

trace.read(
    "ADSL",
    source="adsl.csv",
    rows=len(adsl),
    columns=len(adsl.columns),
)
```

This is more explicit than object inspection, but it is backend-independent.

The integration layer may later remove this manual metric friction.

---

# 6. Integration Style

Object-aware behavior belongs outside TRACE Core.

Conceptually:

```python
trace.pandas.read(adsl, "ADSL")
```

could produce the same core event as:

```python
trace.read(
    "ADSL",
    rows=754,
    columns=16,
)
```

The integration exists to collect evidence.

The core operation exists to define meaning.

That distinction is fundamental.

---

# 7. Integration Responsibilities

An integration may safely inspect a supported runtime object to collect objective metadata.

Examples for a pandas integration:

```text
row count
column count
column names
dtypes
memory usage
index characteristics
null counts
before/after dimensions
merge result dimensions
```

An integration may then call, construct, or enrich the equivalent core TRACE event.

Conceptually:

```text
pandas object
     ↓
pandas integration
     ↓
extract objective metadata
     ↓
TRACE semantic operation
     ↓
TraceEvent
```

The integration should not redefine the meaning of the operation.

---

# 8. Core vs Integration Example — READ

## Core

```python
trace.read(
    "ADSL",
    source="adsl.csv",
    rows=754,
    columns=16,
)
```

## Possible pandas convenience layer

```python
trace.pandas.read(
    adsl,
    "ADSL",
    source="adsl.csv",
)
```

The pandas layer may determine:

```python
rows = len(adsl)
columns = len(adsl.columns)
```

and emit the same semantic `READ` event.

The resulting event should be equivalent in meaning.

---

# 9. Core vs Integration Example — FILTER

## Core

```python
trace.filter(
    "ADSL",
    "SAFFL == 'Y'",
    before=754,
    after=720,
)
```

## Possible pandas convenience layer

```python
trace.pandas.filter(
    source=adsl,
    result=safety,
    name="ADSL",
    condition="SAFFL == 'Y'",
)
```

The integration may derive:

```text
before = len(adsl)
after = len(safety)
removed = before - after
```

But the semantic operation remains explicitly:

```text
FILTER
```

The integration should not infer `FILTER` merely because a pandas `.loc[]` or `.query()` call occurred unless a future optional instrumentation feature can do so transparently and unambiguously.

---

# 10. Core vs Integration Example — MERGE

## Core

```python
trace.merge(
    "ADAE",
    "ADSL",
    on="USUBJID",
    how="left",
    result="ADAE_ANALYSIS",
    left_rows=4127,
    right_rows=754,
    result_rows=4127,
)
```

## Possible pandas convenience layer

```python
trace.pandas.merge(
    left=adae,
    right=adsl,
    result=analysis,
    left_name="ADAE",
    right_name="ADSL",
    result_name="ADAE_ANALYSIS",
    on="USUBJID",
    how="left",
)
```

The integration may inspect all three objects and populate structural metrics.

The core does not need pandas.

---

# 11. Object Identity Is Semantic

In TRACE Core, `"ADSL"` is not a Python variable reference.

It is a semantic object identifier.

That identifier may refer to:

```text
an ADaM dataset
an SDTM domain
an intermediate analysis dataset
a table result
a listing
a figure
a model result
a metadata source
a validation target
```

For example:

```python
trace.filter(
    "Safety Population",
    "SAFFL == 'Y'",
    before=754,
    after=720,
)
```

could also be valid if the programmer chooses a semantic object name rather than a physical dataset name.

TRACE should not assume that object identity equals a Python variable name.

---

# 12. No Variable-Name Introspection

TRACE Core should never attempt to determine that:

```python
adsl
```

is called `"adsl"` in Python.

Variable-name introspection is fragile and semantically weak.

The programmer supplies the meaningful identifier:

```python
trace.read("ADSL", ...)
```

This ensures that logs use the terminology appropriate for statistical review.

---

# 13. No Runtime Object Retention

Core events must not retain:

```text
DataFrames
LazyFrames
Arrow Tables
database relations
model objects
file handles
logger objects
```

An integration may inspect these objects during event creation.

After metadata extraction, the TraceEvent should contain only serializable semantic information and safe structured metadata.

This supports the Phase 0 serialization rule.

---

# 14. Integration Data-Minimization Rule

Even integrations should default to metadata rather than raw data.

Good:

```text
rows=754
columns=16
missing=3
memory_bytes=98321
```

Avoid by default:

```text
entire dataframe
row values
subject-level records
cell-level changes
```

This preserves TRACE's privacy and performance model.

---

# 15. Semantic Intent vs Object Inspection

Phase 4 formalizes two independent concepts:

## Semantic declaration

The programmer says:

```python
trace.filter(...)
```

This establishes the meaning of the event.

## Evidence collection

An integration may inspect:

```python
source_dataframe
result_dataframe
```

to populate:

```text
before
after
removed
```

This establishes supporting execution evidence.

Therefore:

> **Object inspection may enrich an operation. It does not define the operation.**

---

# 16. Architecture Boundary

The recommended architecture becomes:

```text
┌───────────────────────────────────┐
│ Statistical program               │
│                                   │
│ pandas / Polars / SQL / custom    │
└─────────────────┬─────────────────┘
                  │
                  │ explicit semantic event
                  ▼
┌───────────────────────────────────┐
│ TRACE Core                        │
│                                   │
│ read("ADSL", ...)                 │
│ filter("ADSL", ...)               │
│ derive("AGEGR1", ...)             │
│ merge("ADAE", "ADSL", ...)        │
│ validate("ADSL", ...)             │
└─────────────────┬─────────────────┘
                  │
                  ▼
             TraceEvent
                  │
         ┌────────┼─────────┐
         ▼        ▼         ▼
       .log      JSON    summaries
```

Optional integrations sit beside the core:

```text
runtime object
     │
     ▼
pandas / Polars / PyArrow integration
     │
     │ extract metadata
     ▼
TRACE Core semantic event
```

---

# 17. Proposed Package Boundary

A future implementation could use a structure such as:

```text
src/trace_tlf/
├── core/
│   ├── trace.py
│   ├── event.py
│   ├── operation.py
│   ├── severity.py
│   ├── status.py
│   └── context.py
├── rendering/
│   └── text.py
└── integrations/
    ├── pandas.py
    ├── polars.py
    └── pyarrow.py
```

The key dependency direction is:

```text
integrations → core
```

never:

```text
core → pandas
core → polars
core → pyarrow
```

Core must remain importable and usable with no dataframe dependency installed.

---

# 18. Dependency Rule

TRACE Core should have no mandatory dependency on a dataframe library.

A user should be able to install:

```text
trace-tlf
```

and use:

```python
trace.read("ADSL", rows=754, columns=16)
```

without pandas being installed.

Optional integrations may later be distributed through extras, for example conceptually:

```text
trace-tlf[pandas]
trace-tlf[polars]
```

Exact packaging is deferred.

---

# 19. Impact on Tier 1 API

Phase 4 updates the Phase 3 API in one material way.

## Before Phase 4

```python
trace.read(
    data,
    name,
    *,
    source=None,
    rows=None,
    columns=None,
    details=None,
)
```

## After Phase 4

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

The rest of the Tier 1 API was already primarily semantic and object-independent.

The revised Tier 1 API is therefore:

```python
trace.read(
    name,
    *,
    source=None,
    rows=None,
    columns=None,
    details=None,
)

trace.check(
    name,
    check,
    *,
    metrics=None,
    details=None,
)

trace.filter(
    name,
    condition,
    *,
    before=None,
    after=None,
    removed=None,
    details=None,
)

trace.sort(
    name,
    *,
    by,
    ascending=None,
    details=None,
)

trace.derive(
    variable,
    *,
    dataset=None,
    source=None,
    method=None,
    details=None,
)

trace.transform(
    name,
    transformation,
    *,
    source=None,
    result=None,
    details=None,
)

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
    matched=None,
    unmatched_left=None,
    unmatched_right=None,
    details=None,
)

trace.aggregate(
    name,
    *,
    by=None,
    result=None,
    method=None,
    rows=None,
    details=None,
)

trace.analyze(
    name,
    *,
    method,
    population=None,
    result=None,
    details=None,
)

trace.validate(
    name,
    check,
    *,
    passed,
    metrics=None,
    details=None,
)

trace.output(
    name,
    path,
    *,
    format=None,
    rows=None,
    details=None,
)
```

---

# 20. Revised Benchmark TLF

The Phase 2 benchmark now becomes:

```python
from trace_tlf import Trace

trace = Trace("T14_01")

adsl = pd.read_csv("adsl.csv")
trace.read(
    "ADSL",
    source="adsl.csv",
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

summary.to_excel("T14_01.xlsx")
trace.output(
    "T14_01",
    "T14_01.xlsx",
    rows=len(summary),
)
```

The READ call is somewhat more verbose than the earlier object-aware form.

That is an intentional tradeoff in the core API.

An optional pandas integration can later restore low-friction automatic metadata collection.

---

# 21. Convenience APIs Must Preserve Core Equivalence

Any integration convenience call should map cleanly to an equivalent Core event.

For example:

```python
trace.pandas.read(adsl, "ADSL")
```

must conceptually correspond to:

```python
trace.read(
    "ADSL",
    rows=len(adsl),
    columns=len(adsl.columns),
)
```

This gives TRACE one semantic model instead of separate pandas, Polars, and Arrow event models.

---

# 22. Integrations Are Adapters, Not Alternate Frameworks

A pandas integration should not evolve into:

```python
trace.pandas.filter(...)
trace.pandas.merge(...)
trace.pandas.derive(...)
```

with different semantic rules from Core.

It is an adapter.

Its purpose is to:

```text
inspect supported objects
extract safe metrics
normalize metadata
delegate to TRACE semantic events
```

The canonical vocabulary and event semantics remain owned by Core.

---

# 23. Should Both Styles Eventually Be Supported?

Potentially, yes.

Style A:

```python
trace.filter(
    "ADSL",
    "SAFFL == 'Y'",
    before=754,
    after=720,
)
```

should remain canonical.

A future object-aware convenience API could support something like:

```python
trace.pandas.filter(
    source=adsl,
    result=safety,
    name="ADSL",
    condition="SAFFL == 'Y'",
)
```

But TRACE Core itself should not overload `trace.filter()` so aggressively that the method has to guess whether the first argument is:

```text
a semantic object identifier
a dataframe
a custom dataset object
a lazy query
```

Keeping these surfaces separate preserves type clarity.

---

# 24. Why Not Overload Core Methods?

A tempting design is:

```python
trace.filter(
    "ADSL",
    "SAFFL == 'Y'",
    before=754,
    after=720,
)
```

and also:

```python
trace.filter(
    adsl,
    "SAFFL == 'Y'",
    name="ADSL",
)
```

in the same method.

Phase 4 recommends against making this the initial implementation.

It introduces:

- union-heavy typing;
- runtime dispatch;
- backend detection;
- optional dependency questions;
- ambiguous custom-object behavior;
- harder documentation;
- more test permutations;
- temptation for Core to know about dataframe types.

Both user experiences may eventually exist.

They should initially exist through separate layers.

---

# 25. Core Purity Test

A proposed Core feature should pass this question:

> Could this operation be used meaningfully if the statistical program were implemented with no pandas, Polars, or PyArrow objects at all?

If yes, it likely belongs in Core.

If it requires inspecting a particular dataframe implementation, it belongs in an integration.

Examples:

```text
FILTER semantic event         → Core
before/after row values       → Core metadata
extract len(DataFrame)        → Integration

READ semantic event           → Core
rows/columns values           → Core metadata
inspect DataFrame.shape       → Integration

MERGE semantic event          → Core
left/right/result row metrics → Core metadata
inspect pandas merge result   → Integration
```

---

# 26. Phase 4 Decisions

**P4-01** — Style A is the canonical TRACE Core API.

```python
trace.filter(
    "ADSL",
    "SAFFL == 'Y'",
    before=754,
    after=720,
)
```

**P4-02** — Core Tier 1 methods do not require runtime dataframe objects.

**P4-03** — Object identity in TRACE Core is semantic, not tied to Python variable identity.

**P4-04** — Core does not introspect Python variable names.

**P4-05** — Core does not retain dataframe or other analytical runtime objects.

**P4-06** — Object-aware metadata extraction belongs to optional integrations.

**P4-07** — Integrations may automatically collect objective evidence but must preserve explicit semantic intent.

**P4-08** — The dependency direction is `integrations → core`.

**P4-09** — TRACE Core has no mandatory pandas, Polars, or PyArrow dependency.

**P4-10** — `trace.read()` changes from object-aware to semantic:

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

**P4-11** — Supporting both styles later is acceptable, but they should not initially be overloaded into the same Core method.

**P4-12** — Convenience integration calls must map to semantically equivalent Core events.

---

# 27. Acceptance Criteria

Phase 4 is complete when:

1. Core Tier 1 operations can be used without any dataframe library.
2. no Core method requires a DataFrame or equivalent runtime object;
3. object names are explicitly semantic identifiers;
4. integrations can enrich Core events without changing their meaning;
5. the event model remains serializable and free of live analytical objects;
6. pandas/Polars/PyArrow dependencies remain optional;
7. `read()` is aligned with the same object-first semantic convention as other Tier 1 operations;
8. automatic metric extraction is clearly separated from semantic classification;
9. integration dependency direction is one-way toward Core;
10. the canonical API remains usable in real TLF programs.

---

# 28. Phase 4 Outcome

TRACE now has a clear architectural boundary:

```text
TRACE Core
    = semantic execution events

Integrations
    = runtime-object inspection and metadata enrichment
```

The canonical style is:

```python
trace.filter(
    "ADSL",
    "SAFFL == 'Y'",
    before=754,
    after=720,
)
```

The core principle is:

> **TRACE records what the program did. It does not need ownership of the object the program operated on.**

This decision establishes the dependency boundary needed for a backend-independent TRACE implementation.
