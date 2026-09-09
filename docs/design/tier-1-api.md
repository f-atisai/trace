# TRACE Phase 3 — Tier 1 API Specification

**Phase:** 3 — Define the Tier 1 API  
**Status:** Draft normative API specification  
**Scope:** Public Tier 1 operation methods and argument conventions

## Purpose

TRACE should expose a small, obvious public API that maps directly to the canonical vocabulary defined in Phase 1.

The Tier 1 API is:

```python
trace.read()
trace.check()
trace.filter()
trace.sort()
trace.derive()
trace.transform()
trace.merge()
trace.aggregate()
trace.analyze()
trace.validate()
trace.output()
```

> **Common calls require very few arguments; richer metadata is optional.**

## General Rules

- Positional arguments identify the core event.
- Richer metadata is keyword-only.
- Optional means truly optional.
- Avoid unrestricted `**kwargs`.
- Similar concepts use consistent names.
- Tier 1 methods do not expose Python logging configuration.

## `trace.read()`

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

Common:

```python
trace.read(adsl, "ADSL")
```

Richer:

```python
trace.read(
    adsl,
    "ADSL",
    source="analysis/adsl.parquet",
)
```

`data` exists so supported integrations can infer rows, columns, and object type. TRACE must not retain the full object.

## `trace.check()`

```python
trace.check(
    name,
    check,
    *,
    metrics=None,
    details=None,
)
```

Example:

```python
trace.check(
    "ADSL",
    "treatment groups inspected",
    metrics={"groups": 3},
)
```

`CHECK` is observational. It does not enforce a pass/fail contract.

## `trace.filter()`

```python
trace.filter(
    name,
    condition,
    *,
    before=None,
    after=None,
    removed=None,
    details=None,
)
```

Example:

```python
trace.filter(
    "ADSL",
    "SAFFL == 'Y'",
    before=len(adsl),
    after=len(safety),
)
```

If `before` and `after` are present and `removed` is omitted, TRACE may derive `removed = before - after`.

## `trace.sort()`

```python
trace.sort(
    name,
    *,
    by,
    ascending=None,
    details=None,
)
```

Example:

```python
trace.sort(
    "ADAE",
    by=["USUBJID", "AESTDTC"],
)
```

## `trace.derive()`

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

Example:

```python
trace.derive(
    "AGEGR1",
    dataset="ADSL",
    source="AGE",
)
```

`source` may later accept either a single source or multiple sources.

Use `DERIVE` whenever the result is a named analytical concept, including an analysis variable, parameter, flag, category, or endpoint-derived value. This remains true when the implementation uses recoding, mapping, concatenation, or formatting.

## `trace.transform()`

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

Example:

```python
trace.transform(
    "subject_listing",
    "selected and ordered display columns",
    source="ADSL",
    result="listing_display",
)
```

`TRANSFORM` changes representation or structure without creating a new analytical concept. It remains the controlled general-purpose operation and should not replace a more specific operation such as `DERIVE` or `MERGE`.

## `trace.merge()`

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

Common:

```python
trace.merge(
    "ADAE",
    "ADSL",
    on="USUBJID",
    how="left",
)
```

Richer:

```python
trace.merge(
    "ADAE",
    "ADSL",
    on="USUBJID",
    how="left",
    result="ADAE_ANALYSIS",
    left_rows=len(adae),
    right_rows=len(adsl),
    result_rows=len(analysis),
)
```

`*_rows` is preferred over `*_n` for clarity and consistency.

`left_rows`, `right_rows`, and `result_rows` are stable named parameters because their units are explicit. Matching diagnostics are workflow-dependent: "matched" may mean rows, keys, subjects, or another analytical unit. Record them through `metrics` using an explicit unit-bearing name:

```python
trace.merge(
    "ADAE",
    "ADSL",
    on="USUBJID",
    how="inner",
    result="TEAE_SAFETY",
    left_rows=len(teae),
    right_rows=len(safety),
    result_rows=len(merged),
    metrics={
        "matched_subjects": matched_subjects,
        "unmatched_subjects": unmatched_subjects,
    },
)
```

## `trace.aggregate()`

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

Example:

```python
trace.aggregate(
    "ADSL",
    by=["TRT01A", "AGEGR1"],
    result="summary",
)
```

`method` is optional for cases such as subject-incidence counts or descriptive statistics.

## `trace.analyze()`

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

Example:

```python
trace.analyze(
    "ADTTE",
    "Overall survival",
    method="Kaplan-Meier",
    population="ITT",
    result="km_curve",
)
```

`source` is the analytical input identity. `analysis` is the analysis, endpoint, or estimand identity. `method` names the statistical method or model, while `result` remains reserved for the produced result object or artifact. This reads as: analyze `ADTTE` for `Overall survival` using Kaplan–Meier.

The one-identity form is not used because it forces a choice between identifying the analytical input and identifying the analysis. Overloading `result` with the analysis identity is also rejected because a result is a distinct produced object.

`ANALYZE` is Tier 1 because statistical procedures are central to clinical statistical programming. Method-specific metadata remains in `details` until repeated use establishes a stable cross-method parameter.

## `trace.validate()`

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

Example:

```python
trace.validate(
    "ADSL",
    "USUBJID uniqueness",
    passed=True,
)
```

`passed` is required and keyword-only because the validation result is core semantic information.

## `trace.output()`

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

Example:

```python
trace.output(
    "T14_01",
    "T14_01.xlsx",
)
```

Prefer `name` over `object` in Python signatures to avoid shadowing the built-in `object`.

## Cross-Method Consistency

The first argument generally names the primary object:

```python
trace.filter("ADSL", ...)
trace.sort("ADAE", ...)
trace.aggregate("ADAE", ...)
trace.validate("ADSL", ...)
trace.output("T14_01", ...)
```

Exceptions follow natural semantics:

```python
trace.read(data, "ADSL")
trace.merge("ADAE", "ADSL", ...)
trace.derive("AGEGR1", ...)
trace.analyze("ADTTE", "Overall survival", method="Kaplan-Meier")
```

Descriptions central to the event may be positional:

```python
trace.filter("ADSL", "SAFFL == 'Y'")
trace.check("ADSL", "treatment groups inspected")
trace.transform("AESTDTC", "parsed to analysis date")
trace.validate("ADSL", "USUBJID uniqueness", passed=True)
```

Structural metadata remains keyword-only:

```text
by
on
how
source
dataset
result
method
population
rows
before
after
```

`details` is the controlled structured escape hatch for uncommon metadata.

## Named Metrics vs Generic `metrics`

Named metrics are preferred where the operation has stable measurements:

```python
trace.filter(..., before=754, after=720)

trace.merge(
    ...,
    left_rows=4127,
    right_rows=754,
    result_rows=4127,
)
```

Generic `metrics` is reserved for operations whose measurements vary widely:

```python
trace.check(
    "ADSL",
    "treatment groups inspected",
    metrics={"groups": 3},
)
```

```python
trace.validate(
    "ADSL",
    "USUBJID uniqueness",
    passed=False,
    metrics={"checked": 754, "failed": 3},
)
```

## What Is Not Tier 1

The following should not define the primary user experience:

```python
trace.log(...)
trace.event(...)
trace.emit(...)
trace.bind(...)
trace.step(...)
trace.debug(...)
trace.info(...)
trace.warning(...)
```

Some may exist later as advanced APIs.

## Recommended Tier 1 Surface

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
    metrics=None,
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
    source,
    analysis,
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

## Design Concerns Before Implementation

### `read(data, name)` argument order

Current:

```python
trace.read(adsl, "ADSL")
```

Alternative:

```python
trace.read("ADSL", data=adsl)
```

The current form matches Phase 2 and is concise, but most methods place the semantic name first. This should be paper-tested before implementation freeze.

### `details` typing

Prefer a structured mapping rather than arbitrary text:

```python
details: Mapping[str, object] | None
```

Free text can be represented as:

```python
details={"message": "..."}
```

This keeps events serialization-friendly.

### `passed` and internal status

The ergonomic public API may use:

```python
passed=True
```

while mapping internally to canonical TRACE Status.

Users should not need to know the internal status representation for common validation calls.

## API Friction Test

The Phase 2 benchmark should remain essentially unchanged:

```python
from trace_tlf import Trace

trace = Trace("T14_01")

adsl = pd.read_csv("adsl.csv")
trace.read(adsl, "ADSL")

safety = adsl.loc[adsl["SAFFL"] == "Y"].copy()
trace.filter(
    "ADSL",
    "SAFFL == 'Y'",
    before=len(adsl),
    after=len(safety),
)

safety["AGEGR1"] = ...
trace.derive(
    "AGEGR1",
    dataset="ADSL",
    source="AGE",
)

summary = ...
trace.aggregate(
    "ADSL",
    by=["TRT01A", "AGEGR1"],
    result="summary",
)

summary.to_excel("T14_01.xlsx")
trace.output(
    "T14_01",
    "T14_01.xlsx",
)
```

## Phase 3 Decisions

**P3-01** — Tier 1 contains eleven methods: `read`, `check`, `filter`, `sort`, `derive`, `transform`, `merge`, `aggregate`, `analyze`, `validate`, `output`.

**P3-02** — Tier 1 method names map directly to Phase 1 vocabulary.

**P3-03** — Core semantic identifiers may be positional; rich metadata is keyword-only.

**P3-04** — Common calls should usually require no more than one or two positional arguments.

**P3-05** — Stable operation-specific metrics with unambiguous units get named parameters.

**P3-06** — Generic `metrics` is reserved for inherently variable measurements, including merge diagnostics whose analytical unit varies by workflow.

**P3-07** — `details` is the structured escape hatch for uncommon metadata.

**P3-08** — Logging infrastructure is not exposed through Tier 1 methods.

**P3-09** — `ANALYZE` is included in Tier 1 and takes distinct `source` and `analysis` identities.

**P3-10** — Tier 1 must continue to satisfy the Phase 2 friction budget.

## Acceptance Criteria

Phase 3 is complete when:

1. every Phase 1 core operation has a clear Tier 1 method;
2. naming is obvious and predictable;
3. common calls stay concise;
4. rich metadata is optional;
5. secondary metadata is keyword-only;
6. realistic clinical workflows fit without ceremony;
7. statistical procedures have a first-class `analyze()` method;
8. Python logging internals remain hidden;
9. structured metadata is supported without unrestricted `**kwargs`;
10. the Phase 2 TLF remains recognizably unchanged.

## Outcome

TRACE's Tier 1 surface is intentionally small:

```python
trace.read()
trace.check()
trace.filter()
trace.sort()
trace.derive()
trace.transform()
trace.merge()
trace.aggregate()
trace.analyze()
trace.validate()
trace.output()
```

> **Common calls require very few arguments; richer metadata is optional.**
