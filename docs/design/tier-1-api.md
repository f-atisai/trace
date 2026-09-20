# TRACE Tier 1 API Specification

**Status:** Alpha governing design  
**Scope:** Public semantic-operation API and argument conventions

## Purpose

TRACE exposes eleven semantic helpers that map directly to the canonical statistical-programming vocabulary:

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

The vocabulary itself is defined in [TRACE Core Operations v0.1](../framework/core-operations-v0.1.md). The user-facing alpha contract is defined in the [TRACE API](../api/README.md).

> **Common calls require very few arguments; richer metadata is optional.**

TRACE Core is semantic and object-independent. Core calls identify analytical objects and accept structured evidence; optional integrations may later inspect runtime objects to collect observed diagnostics.

## General rules

- Positional arguments identify the core semantic event.
- Richer metadata is keyword-only.
- Optional means truly optional.
- Avoid unrestricted `**kwargs`.
- Tier 1 methods do not expose Python logging configuration.
- Use reviewer-meaningful semantic identities such as `ADSL`, `AGEGR1`, `Overall Survival`, `Safety Population`, or `T14_01`.
- Quantitative diagnostics belong in metrics; descriptive metadata belongs in details.
- Diagnostic units should be explicit where a count could mean rows, subjects, keys, groups, or another analytical unit.
- Core-supplied diagnostic values are not equivalent to values directly observed by an integration. Evidence origin is defined in [TRACE Reviewer Experience](reviewer-experience.md).

## Primary alpha workflow

The introductory TRACE experience emphasizes:

```text
READ
FILTER
DERIVE
MERGE
AGGREGATE
ANALYZE
VALIDATE
OUTPUT
```

`CHECK`, `SORT`, and `TRANSFORM` remain fully public Tier 1 operations but are secondary in introductory documentation. This is a documentation distinction, not a difference in support.

## `trace.read()`

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

`name` is the semantic identity of the acquired input. TRACE Core does not require or retain a runtime DataFrame.

```python
trace.read(
    "ADSL",
    source="analysis/adsl.parquet",
    rows=len(adsl),
    columns=len(adsl.columns),
)
```

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

`CHECK` records an observation; it does not enforce a pass/fail expectation.

## `trace.filter()`

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

`name` identifies the source object being filtered. `result` optionally names the semantic result without replacing source identity.

```python
trace.filter(
    "ADSL",
    "SAFFL == 'Y'",
    result="Safety Population",
    before=len(adsl),
    after=len(safety),
)
```

Conceptually:

```text
source/object: ADSL
condition:     SAFFL == 'Y'
result:        Safety Population
```

`result` is a semantic identity; it does not imply that a Python variable with that name exists. Population selection remains `FILTER`; TRACE does not introduce a `POPULATION` operation.

If `before` and `after` are supplied and `removed` is omitted, TRACE derives `removed = before - after`.

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

Use `SORT` only when ordering materially matters to later analysis, derivation, reporting, or reproducibility.

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

`variable` identifies the named analytical concept created.

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

Use `TRANSFORM` for material representation or structure changes when no more specific operation fits.

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

Operation-specific row dimensions use named parameters. Domain-specific diagnostics such as `matched_subjects` or `unmatched_keys` belong in `metrics`.

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

`AGGREGATE` describes grouping or reduction such as counts, percentages, means, or descriptive statistics.

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

The source dataset and analysis identity are intentionally separate.

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

`passed=True` means only that the implemented validation criterion evaluated successfully. It does not establish broader statistical correctness. Diagnostic evidence origin remains independent of validation status.

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

`OUTPUT` records semantic output production. Program-level provenance separately records the physical artifact identity and optional hash.

## `details`

`details` is a controlled structured escape hatch for uncommon descriptive metadata. Repeated metadata should become a named API parameter only when realistic programs show stable cross-use value.

## Return value

Tier 1 helpers currently return the structured event created internally. The event model is an implementation detail in the alpha compatibility contract; users should not need to construct or import event classes directly to use TRACE.

## Alpha decision

For `v0.1.0-alpha`, all eleven helpers are public. The alpha intentionally does not add runtime-object integrations, provenance constructor arguments, custom handlers, renderers, sinks, automatic hashing, or environment capture to this surface.
