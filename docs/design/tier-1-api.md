# TRACE Phase 3 — Tier 1 API Specification

**Phase:** 3 — Define the Tier 1 API  
**Status:** Draft normative API specification  
**Scope:** Public Tier 1 operation methods and argument conventions

## Purpose

TRACE exposes a small public API that maps directly to the canonical statistical-programming vocabulary.

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

TRACE Core is semantic and object-independent. Core calls identify analytical objects and accept structured evidence; optional integrations may inspect runtime objects to collect observed diagnostics.

## General rules

- Positional arguments identify the core semantic event.
- Richer metadata is keyword-only.
- Optional means truly optional.
- Avoid unrestricted `**kwargs`.
- Similar concepts use consistent names.
- Tier 1 methods do not expose Python logging configuration.
- Semantic identifiers should be reviewer-meaningful names such as `ADSL`, `AGEGR1`, `Overall Survival`, or `T14_01`, not implementation names such as `df` or `tmp`.
- Quantitative diagnostics belong in metrics; descriptive metadata belongs in details.
- Diagnostic units should be explicit where a count could mean rows, subjects, keys, groups, or another analytical unit.
- Core-supplied diagnostic values are not equivalent to values observed by an integration. The evidence-origin model is defined in [`reviewer-experience.md`](reviewer-experience.md).

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

Common:

```python
trace.read("ADSL")
```

Richer:

```python
trace.read(
    "ADSL",
    source="analysis/adsl.parquet",
    rows=254,
    columns=16,
)
```

`name` is the semantic identity of the acquired input. TRACE Core does not require or retain the runtime DataFrame.

A future integration may inspect a runtime object and emit the equivalent semantic event, for example conceptually:

```python
trace.pandas.read(adsl, "ADSL", source="analysis/adsl.parquet")
```

The integration may observe dimensions directly; Core callers may supply them.

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
    metrics={"treatment_groups": 2},
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

`name` identifies the object being filtered. For population selection, the source identity remains important:

```text
source/object: ADSL
condition:     SAFFL == 'Y'
conceptual result: Safety Population
```

The current Tier 1 API does not add a dedicated `result` parameter to `FILTER`. The reviewer pressure test showed that a named result can be useful, but final API evidence should come from the planned public-dataset examples before expanding the signature. Until then, population selection remains a `FILTER`; TRACE does not introduce a `POPULATION` operation.

If `before` and `after` are present and `removed` is omitted, TRACE may derive `removed = before - after`. The current prototype field names are retained for compatibility; conceptually they represent row counts and should not be mistaken for subjects or another analytical unit.

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
trace.sort("ADAE", by=["USUBJID", "AESTDTC"])
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
trace.derive("AGEGR1", dataset="ADSL", source="AGE")
```

Use `DERIVE` when the result is a named analytical concept, including an analysis variable, parameter, flag, category, or endpoint-derived value. This remains true when the implementation uses recoding, mapping, concatenation, or formatting.

`source` may identify one or multiple source variables.

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
    "Safety Population",
    "reporting columns selected",
    result="subject_listing",
)
```

`TRANSFORM` changes representation or structure without creating a new analytical concept. It is a controlled general-purpose operation and should not replace a more specific operation.

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

Example:

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

`left_rows`, `right_rows`, and `result_rows` have explicit units and are therefore stable named parameters. Matching diagnostics are workflow-dependent, so use unit-bearing metric names such as `matched_subjects` or `unmatched_keys`.

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
    "Safety Population",
    by=["TRT01A", "SEX", "AGEGR1"],
    result="demographics_summary",
    method="distinct subjects",
)
```

`AGGREGATE` covers grouping and reduction such as participant counts, incidence summaries, means, standard deviations, and percentages.

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
    "Overall Survival",
    method="Kaplan-Meier",
    population="ITT",
    result="km_curve",
)
```

`source` identifies the analytical input. `analysis` identifies the endpoint, estimand, or analysis. `method` names the method or model. `population` optionally identifies the analysis population, while `result` identifies the produced analytical result.

These identities remain separate because collapsing them would make the execution evidence less precise. Method-specific metadata such as time variable, censoring variable, or strata belongs in `details` until repeated use establishes stable cross-method parameters.

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
    "T14_01",
    "production and QC statistics match",
    passed=statistics_match,
    metrics={"mismatched_rows": mismatched_rows},
)
```

`passed` is required and keyword-only because the validation outcome is core semantic information.

A `PASS` means only that the implemented validation criterion evaluated successfully. It does not establish that the program, analysis, or output is statistically correct. The evidentiary strength of supporting diagnostics depends on whether they were observed, supplied, or derived.

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
trace.output("T14_01", "outputs/T14_01.rtf")
```

`OUTPUT` records that a named analytical artifact was produced. Physical artifact identity and optional hashes belong to program-level provenance rather than being repeated as event metrics.

## Cross-method consistency

The first argument generally identifies the primary semantic object:

```python
trace.read("ADSL")
trace.filter("ADSL", "SAFFL == 'Y'")
trace.sort("ADAE", by=["USUBJID", "AESTDTC"])
trace.aggregate("ADAE", by=["TRT01A", "AEBODSYS"])
trace.validate("ADSL", "USUBJID uniqueness", passed=True)
trace.output("T14_01", "outputs/T14_01.rtf")
```

Exceptions follow natural semantics:

```python
trace.merge("ADAE", "ADSL", on="USUBJID")
trace.derive("AGEGR1", dataset="ADSL", source="AGE")
trace.analyze("ADTTE", "Overall Survival", method="Kaplan-Meier")
```

`details` is the controlled structured escape hatch for uncommon metadata.

## Named metrics versus generic `metrics`

Named metrics are preferred where an operation has stable measurements with clear units:

```python
trace.filter("ADSL", "SAFFL == 'Y'", before=254, after=249)

trace.merge(
    "ADAE",
    "ADSL",
    left_rows=4127,
    right_rows=754,
    result_rows=4127,
)
```

Generic `metrics` is reserved for measurements whose semantics vary by workflow:

```python
trace.validate(
    "ADSL",
    "USUBJID uniqueness",
    passed=False,
    metrics={"duplicate_subjects": 3},
)
```

The structured evidence model must preserve diagnostic origin even when the concise text renderer omits origin labels.

## What is not Tier 1

`trace.step()` is a supported system/lifecycle API, not a Tier 1 statistical operation. `trace.log()` is the secondary generic structured-event API. Severity-first logging helpers do not define the primary TRACE experience.

## Recommended Tier 1 surface

```python
trace.read(name, *, source=None, rows=None, columns=None, details=None)
trace.check(name, check, *, metrics=None, details=None)
trace.filter(name, condition, *, before=None, after=None, removed=None, details=None)
trace.sort(name, *, by, ascending=None, details=None)
trace.derive(variable, *, dataset=None, source=None, method=None, details=None)
trace.transform(name, transformation, *, source=None, result=None, details=None)
trace.merge(left, right, *, on=None, how=None, result=None, left_rows=None, right_rows=None, result_rows=None, metrics=None, details=None)
trace.aggregate(name, *, by=None, result=None, method=None, rows=None, details=None)
trace.analyze(source, analysis, *, method, population=None, result=None, details=None)
trace.validate(name, check, *, passed, metrics=None, details=None)
trace.output(name, path, *, format=None, rows=None, details=None)
```

## API friction test

A routine TLF program should remain recognizably ordinary Python:

```python
from trace_tlf import Trace

with Trace("T14_01") as trace:
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

    safety["AGEGR1"] = ...
    trace.derive("AGEGR1", dataset="ADSL", source="AGE")

    summary = ...
    trace.aggregate(
        "Safety Population",
        by=["TRT01A", "SEX", "AGEGR1"],
        result="demographics_summary",
    )

    summary.to_excel("outputs/T14_01.xlsx")
    trace.output("T14_01", "outputs/T14_01.xlsx")
```

TRACE records the analytical execution after the underlying operation; it does not own the transformation itself.

## Decisions

- Tier 1 contains eleven methods: `read`, `check`, `filter`, `sort`, `derive`, `transform`, `merge`, `aggregate`, `analyze`, `validate`, `output`.
- Core semantic identifiers may be positional; rich metadata is keyword-only.
- Stable operation-specific metrics with unambiguous units get named parameters.
- Generic `metrics` is reserved for inherently variable measurements.
- `details` is the structured escape hatch for uncommon metadata.
- `ANALYZE` retains distinct source and analysis identities.
- Core `READ` is semantic-first: `trace.read(name, ...)`; runtime-object inspection belongs to optional integrations.
- Named populations remain `FILTER` results; no `POPULATION` operation is introduced.
- A dedicated FILTER `result` parameter remains deferred until realistic public-dataset examples justify expanding the API.
- A `VALIDATE` result records the outcome of the implemented criterion, not proof of overall statistical correctness.
- Tier 1 must continue to satisfy the minimum programmer-experience friction budget.

## Acceptance criteria

The Tier 1 design is successful when every canonical operation has a clear method, common calls remain concise, runtime-object inspection remains optional, statistical procedures remain first-class, and reviewer-facing evidence does not imply more certainty than its diagnostic origin supports.
