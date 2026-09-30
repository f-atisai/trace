# TRACE operations

TRACE uses a small, controlled vocabulary to describe meaningful statistical-programming activity consistently across Python backends.

```text
READ  CHECK  FILTER  SORT  DERIVE  TRANSFORM
MERGE  AGGREGATE  ANALYZE  VALIDATE  OUTPUT
```

These operations describe **what happened in the statistical workflow**. Python logging levels such as `INFO`, `WARNING`, and `ERROR` describe severity.

## Quick selection guide

```text
External input acquired?                     → READ
Observation without an enforced rule?        → CHECK
Rows or observations selected/excluded?      → FILTER
Order intentionally changed?                 → SORT
New named analytical concept created?        → DERIVE
Representation or structure changed?         → TRANSFORM
Multiple analytical sources combined?        → MERGE
Detailed data reduced or grouped?             → AGGREGATE
Statistical method/model/estimator applied?  → ANALYZE
Explicit expectation tested?                 → VALIDATE
External artifact produced?                  → OUTPUT
```

If none fits cleanly, the action may be too low-level to record, `TRANSFORM` may be the appropriate controlled fallback, or the vocabulary may have a genuine gap.

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

`READ` identifies the semantic input object. In a managed run, the physical source path can also be registered in program-level provenance.

Do not use `READ` for an in-memory result created by the program.

## CHECK

Use `CHECK` to record an observation or diagnostic without enforcing a pass/fail expectation.

```python
trace.check(
    "ADSL",
    "treatment groups observed",
    metrics={"treatment_groups": 3},
)
```

Typical uses include diagnostic counts, missingness observations, data-availability checks, and temporary QC diagnostics.

Use `VALIDATE` instead when the program is testing a specific expectation.

## FILTER

Use `FILTER` when records are retained or excluded according to a condition, including analysis-population selection.

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

Population selection remains a `FILTER`. TRACE does not use a separate `POPULATION` operation.

Do not use `FILTER` for column selection, sorting, grouping, or reshaping.

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

Do not record incidental ordering that has no analytical or reporting significance.

## DERIVE

Use `DERIVE` when the program creates a new named analytical concept such as a variable, flag, category, parameter, endpoint value, or analysis value.

```python
adsl["AGEGR1"] = pd.cut(adsl["AGE"], bins=[0, 64, 200])

trace.derive(
    "AGEGR1",
    dataset="ADSL",
    source="AGE",
    method="age category",
)
```

A new named analysis variable is normally `DERIVE` even when implemented by recoding, mapping, concatenation, or formatting.

Use `TRANSFORM` when representation or structure changes but no new analytical concept is created.

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

Typical examples include pivots, normalization, parsing, or display preparation.

`TRANSFORM` is a controlled fallback, not a general replacement for `FILTER`, `MERGE`, `AGGREGATE`, or other more specific operations.

## MERGE

Use `MERGE` when two or more analytical sources are combined and the contributing sources matter.

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

When cardinality matters, prefer explicit diagnostics such as `left_rows`, `right_rows`, `result_rows`, `matched_subjects`, or `unmatched_keys` over ambiguous generic counts.

## AGGREGATE

Use `AGGREGATE` when detailed observations are grouped or reduced into summary-level values such as counts, percentages, sums, means, or standard deviations.

```python
trace.aggregate(
    "Safety ADAE",
    by=["AESOC", "AEDECOD", "TRT01A"],
    result="AE incidence",
    method="unique participant count",
    rows=len(ae_summary),
)
```

Counts, means, standard deviations, and percentages are `AGGREGATE` operations.

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

Typical examples include Kaplan-Meier estimation, Cox regression, ANCOVA, and MMRM.

The analysis identity is the semantic subject of the event while the source dataset is recorded separately.

## VALIDATE

Use `VALIDATE` when the program explicitly tests an expectation, requirement, rule, tolerance, or acceptance criterion.

```python
trace.validate(
    "Safety Population",
    "participant count equals treatment totals",
    passed=safety_total == treatment_total,
    metrics={"participants": safety_total},
)
```

Typical uses include uniqueness, required values, expected treatment arms, tolerance checks, cross-dataset consistency, shell conformity, and production/QC comparisons.

A passing validation means only that the implemented criterion evaluated successfully. It does not prove that the overall statistical result is correct.

`CHECK` observes; `VALIDATE` tests an expectation. `QC` is a workflow or context, not an operation.

## OUTPUT

Use `OUTPUT` when the program creates an externally consumable artifact such as a table, listing, figure, derived dataset, CSV, RTF, PDF, Excel workbook, JSON file, or QC report.

```python
write_rtf(table, "outputs/T14_01.rtf")

trace.output(
    "T14_01",
    "outputs/T14_01.rtf",
    format="RTF",
)
```

In a managed run with `log_file`, the physical output path is also registered in program-level provenance.

## Important boundaries

The most important distinctions are:

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

## Use one term per concept

TRACE deliberately avoids multiple synonyms for the same operation:

| Instead of | Use |
|---|---|
| `SUBSET`, `WHERE`, row `SELECT` | `FILTER` |
| `JOIN`, `COMBINE`, `APPEND`, `CONCAT` | `MERGE` |
| `LOAD`, `IMPORT`, `INGEST` | `READ` |
| `WRITE`, `EXPORT`, `SAVE` | `OUTPUT` |
| `SUMMARY` | `AGGREGATE` or `ANALYZE`, depending on intent |
| `POPULATION` | `FILTER` with a named result |
| `QC` | the relevant operation within the QC workflow |
| `ERROR`, `WARNING` | severity, not an operation |

Generic terms such as `CALCULATE`, `COMPUTE`, or `CREATE` should be replaced by the operation that expresses the statistical intent, usually `DERIVE`, `AGGREGATE`, or `ANALYZE`.

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

Avoid implementation-only names when they do not help another programmer or reviewer:

```text
df
tmp
merged_df
result2
```

When both the source and result matter, preserve both identities. For example, selecting the Safety Population is a `FILTER` on `ADSL` whose result is `Safety Population`.

## Typical workflows

TRACE operations can be read as a compact description of a program's statistical workflow.

| Workflow | Typical sequence |
|---|---|
| Analysis population | `READ → FILTER → CHECK/VALIDATE` |
| Demographics table | `READ → FILTER → DERIVE → AGGREGATE → VALIDATE → OUTPUT` |
| Disposition table | `READ → FILTER → AGGREGATE → MERGE → TRANSFORM → OUTPUT` |
| Adverse-event table | `READ → FILTER → MERGE → AGGREGATE → VALIDATE → OUTPUT` |
| Laboratory summary | `READ → FILTER → DERIVE → AGGREGATE → TRANSFORM → OUTPUT` |
| Kaplan-Meier analysis | `READ → FILTER → SORT → ANALYZE → VALIDATE → OUTPUT` |
| Cox regression | `READ → FILTER → ANALYZE → VALIDATE → OUTPUT` |
| ANCOVA | `READ → FILTER → MERGE → DERIVE → ANALYZE → TRANSFORM → OUTPUT` |
| Subject listing | `READ → FILTER → SORT → TRANSFORM → OUTPUT` |
| ADaM derivation | `READ → SORT → FILTER → MERGE → DERIVE → VALIDATE → OUTPUT` |
| Independent QC | `READ → MERGE → VALIDATE → OUTPUT` |

These sequences are illustrative rather than prescriptive. Record only operations that materially improve understanding of the run.

## Lifecycle operations

`START`, `END`, and `STEP` are TRACE-managed lifecycle operations rather than statistical operations.

```python
with Trace("T14_01") as trace:
    with trace.step("Analysis population"):
        ...
```

Use steps for meaningful analytical stages, not around every individual line. See [Logging with TRACE](logging-with-trace.md) for lifecycle, steps, file logs, and provenance.

## Vocabulary changes

The vocabulary should grow slowly. A new operation should be added only when realistic programs repeatedly require it, existing operations would distort the meaning, and the proposed term has stable backend-independent semantics.

A library method name or desire for a more convenient synonym is not enough reason to add another operation.
