# TRACE operations

TRACE uses a small, controlled statistical-programming vocabulary instead of arbitrary log messages.

```text
READ  CHECK  FILTER  SORT  DERIVE  TRANSFORM
MERGE  AGGREGATE  ANALYZE  VALIDATE  OUTPUT
```

These operations describe **what happened in the statistical workflow**. Python logging levels such as `INFO`, `WARNING`, and `ERROR` still describe severity.

Use TRACE to record operations that materially help another programmer or reviewer understand the run. You do not need to trace every line of code.

## Quick selection guide

```text
External input acquired?                    → READ
Observation without an enforced rule?       → CHECK
Rows or observations selected/excluded?      → FILTER
Order intentionally changed?                 → SORT
New named analytical concept created?        → DERIVE
Representation or structure changed?         → TRANSFORM
Multiple analytical sources combined?        → MERGE
Detailed data reduced or grouped?             → AGGREGATE
Statistical method/model/estimator applied?   → ANALYZE
Explicit expectation tested?                  → VALIDATE
External artifact produced?                   → OUTPUT
```

If none fits, the action may be too low-level to record, `TRANSFORM` may be the correct fallback, or the vocabulary may need deliberate extension.

## READ

Use `READ` when the program acquires an external input such as an ADaM dataset, metadata file, specification, or configuration.

```python
adsl = pd.read_sas("data/adsl.xpt", format="xport")

trace.read(
    "ADSL",
    source="data/adsl.xpt",
    rows=len(adsl),
    columns=len(adsl.columns),
)
```

Example output:

```text
INFO [READ] [ADSL] loaded – source=data/adsl.xpt, N=254, Vars=48
```

Use the semantic identity of the input, such as `ADSL` or `ADAE`, rather than a temporary Python variable name such as `df`.

## CHECK

Use `CHECK` to record an observation without enforcing a pass/fail expectation.

```python
trace.check(
    "ADSL",
    "treatment groups observed",
    metrics={"treatment_groups": 3},
)
```

Example output:

```text
INFO [CHECK] [ADSL] treatment groups observed – treatment_groups=3
```

Use `VALIDATE` instead when the program is testing a specific requirement.

## FILTER

Use `FILTER` when records are retained or excluded, including analysis-population selection.

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

Example output:

```text
INFO [FILTER] [ADSL] SAFFL == 'Y' applied – N=754 → 720
```

Population selection is still a `FILTER`; TRACE does not use a separate `POPULATION` operation.

## SORT

Use `SORT` when observation order matters to later derivation, analysis, reporting, or reproducibility.

```python
adae = adae.sort_values(["USUBJID", "AESTDTC"])

trace.sort(
    "ADAE",
    by=["USUBJID", "AESTDTC"],
    ascending=True,
)
```

Example output:

```text
INFO [SORT] [ADAE] ordered – by=USUBJID,AESTDTC
```

Do not record incidental ordering that has no analytical or reporting significance.

## DERIVE

Use `DERIVE` when the program creates a new named analytical concept such as a variable, flag, category, parameter, or analysis value.

```python
adsl["AGEGR1"] = pd.cut(adsl["AGE"], bins=[0, 64, 200])

trace.derive(
    "AGEGR1",
    dataset="ADSL",
    source="AGE",
    method="age category",
)
```

Example output:

```text
INFO [DERIVE] [AGEGR1] created – dataset=ADSL, source=AGE, method=age category
```

Use `TRANSFORM` when the representation changes but no new analytical concept is created.

## TRANSFORM

Use `TRANSFORM` for a material representation or structural change when a more specific operation does not fit.

```python
trace.transform(
    "AE summary",
    "pivoted to reporting layout",
    source="ae_counts",
    result="ae_display",
)
```

Example output:

```text
INFO [TRANSFORM] [AE summary] pivoted to reporting layout – source=ae_counts, result=ae_display
```

`TRANSFORM` is a controlled fallback, not a general replacement for more specific operations such as `FILTER`, `MERGE`, or `AGGREGATE`.

## MERGE

Use `MERGE` when two analytical sources are combined and the contributing sources matter.

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

Example output:

```text
INFO [MERGE] [ADAE + Safety Population] merged – on=USUBJID, how=inner
```

Prefer explicit diagnostics such as `left_rows`, `right_rows`, and `result_rows` over an ambiguous generic count.

## AGGREGATE

Use `AGGREGATE` when detailed observations are grouped or reduced into summary values such as counts, percentages, means, or standard deviations.

```python
trace.aggregate(
    "Safety ADAE",
    by=["AESOC", "AEDECOD", "TRT01A"],
    result="AE incidence",
    method="unique participant count",
    rows=len(ae_summary),
)
```

Example output:

```text
INFO [AGGREGATE] [Safety ADAE] unique participant count – by=AESOC,AEDECOD,TRT01A
```

Use `ANALYZE` when a statistical method, model, estimator, or inferential procedure is applied.

## ANALYZE

Use `ANALYZE` for statistical methods beyond simple grouping or reduction.

```python
trace.analyze(
    "ADTTE",
    "Overall Survival",
    method="Kaplan-Meier",
    population="ITT",
    result="km_curve",
)
```

Example output:

```text
INFO [ANALYZE] [Overall Survival] Kaplan-Meier fitted – source=ADTTE, population=ITT
```

Typical examples include Kaplan-Meier estimation, Cox regression, ANCOVA, and MMRM.

## VALIDATE

Use `VALIDATE` when the program explicitly tests an expectation, requirement, rule, or tolerance.

```python
trace.validate(
    "Safety Population",
    "participant count equals treatment totals",
    passed=safety_total == treatment_total,
    metrics={"participants": safety_total},
)
```

Example output:

```text
INFO [VALIDATE] [Safety Population] participant count equals treatment totals – PASS
```

A passing validation means only that the implemented criterion evaluated successfully. It does not prove that the overall statistical result is correct.

## OUTPUT

Use `OUTPUT` when the program creates an externally consumable artifact such as a TLF, dataset, CSV, PDF, or QC report.

```python
write_rtf(table, "outputs/T14_01.rtf")

trace.output(
    "T14_01",
    "outputs/T14_01.rtf",
    format="RTF",
)
```

Example output:

```text
INFO [OUTPUT] [T14_01] written – outputs/T14_01.rtf, format=RTF
```

In a managed run with `log_file`, the output path is also registered in program-level provenance.

## Common boundaries

The operations are intentionally narrow. These distinctions matter most:

```text
CHECK      observe
VALIDATE   test an expectation

DERIVE     create a named analytical concept
TRANSFORM  change representation or structure

AGGREGATE  group, reduce, or summarize
ANALYZE    apply a statistical method, model, or estimator
```

Examples:

```text
Inspect treatment-group count                 CHECK
Require exactly three treatment groups        VALIDATE

AGE → AGEGR1                                  DERIVE
Pivot AE summary rows to treatment columns    TRANSFORM

Count subjects by treatment                   AGGREGATE
Mean and SD by treatment                      AGGREGATE
Kaplan-Meier estimation                       ANALYZE
ANCOVA                                        ANALYZE
```

## Typical statistical workflows

TRACE operations can be read as a compact description of the program's statistical workflow.

| Workflow | Typical sequence |
|---|---|
| Analysis population | `READ → FILTER → CHECK/VALIDATE` |
| Demographics table | `READ → FILTER → DERIVE → AGGREGATE → VALIDATE → OUTPUT` |
| Adverse-event table | `READ → FILTER → MERGE → AGGREGATE → VALIDATE → OUTPUT` |
| Laboratory summary | `READ → FILTER → DERIVE → AGGREGATE → TRANSFORM → OUTPUT` |
| Kaplan-Meier analysis | `READ → FILTER → SORT → ANALYZE → VALIDATE → OUTPUT` |
| Subject listing | `READ → FILTER → SORT → TRANSFORM → OUTPUT` |
| ADaM derivation | `READ → SORT → FILTER → MERGE → DERIVE → VALIDATE → OUTPUT` |
| Independent QC | `READ → MERGE → VALIDATE → OUTPUT` |

These sequences are illustrative rather than prescriptive. Record only operations that materially improve understanding of the run.

## Naming conventions

Prefer stable statistical identities:

```text
ADSL
ADAE
AGEGR1
Safety Population
Overall Survival
T14_01
```

Avoid implementation-only names when they do not help the reviewer:

```text
df
tmp
merged_df
result2
```

When both the source and result matter, preserve both. For example, `ADSL` remains the source of a safety-population `FILTER`, while `Safety Population` identifies the result.

## Lifecycle operations

`START`, `END`, and `STEP` are TRACE-managed lifecycle operations rather than statistical operations.

```python
with Trace("T14_01") as trace:
    with trace.step("Analysis population"):
        ...
```

Use steps for meaningful analytical stages, not around every individual line.

## Deeper reference

This guide is the practical operation-selection reference. For exact method signatures and parameters, see the [TRACE API](../api/README.md).

For the normative vocabulary rules and boundary decisions, see [TRACE Core Operations v0.1](../framework/core-operations-v0.1.md).
