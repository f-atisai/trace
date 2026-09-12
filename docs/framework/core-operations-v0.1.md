# TRACE Core Operations v0.1

**Phase:** 1 — Define the Canonical TRACE Vocabulary  
**Status:** Draft normative specification  
**Version:** 0.1  
**Scope:** Core operation vocabulary only; no public method signatures or implementation details

## 1. Purpose

TRACE uses a controlled vocabulary to describe meaningful statistical-programming execution consistently across Python backends.

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

`START` and `END` are reserved TRACE-managed lifecycle operations. `STEP` belongs to the system/lifecycle layer. `SUMMARY` is excluded because it overlaps with both `AGGREGATE` and `ANALYZE`.

## 2. Selection principles

TRACE classifies statistical intent, not Python syntax. Equivalent pandas, Polars, SQL, NumPy, or custom implementations should map to the same operation.

Use one primary term per concept:

```text
FILTER    not SUBSET / WHERE / SELECT
MERGE     not JOIN / COMBINE / CONCAT
AGGREGATE not SUMMARY
OUTPUT    not WRITE / EXPORT / SAVE
```

Not every line of code deserves a TRACE event. Record operations that materially explain inputs, population changes, derivations, data structure, statistical analysis, validation, outputs, or execution flow.

### Semantic identities

TRACE names stable statistical-programming concepts rather than Python variables. Prefer `ADSL`, `ADAE`, `AGEGR1`, `Overall Survival`, `TEAE_SAFETY`, and `T14_01` over `df`, `tmp`, or `merged_df`.

When an operation acts on one object and produces a separately meaningful analytical concept, preserve both identities rather than replacing the source identity.

For example, selecting the Safety Population from ADSL is still a `FILTER` on `ADSL`; `Safety Population` is the resulting analytical concept:

```text
source/object: ADSL
condition:     SAFFL == 'Y'
result:        Safety Population
```

`ANALYZE` is intentionally different: the analysis or endpoint is the semantic subject of the event, while the source dataset is recorded separately.

## 3. Core operations

### 3.1 READ

**Means:** Acquire an external input for the current execution.

```text
INFO [READ] [ADSL] loaded – rows=254, columns=16
```

Typical inputs include `ADSL`, `ADAE`, `ADTTE`, metadata workbooks, specifications, and configuration files.

**Does not mean:** create an in-memory result, derive a dataset, or write an output.

`READ` identifies the semantic input object. Program-level provenance separately identifies the physical input artifact that participated in the run.

### 3.2 CHECK

**Means:** Observe or inspect execution state without enforcing an expected outcome.

```text
INFO [CHECK] [ADSL] treatment groups inspected – treatment_groups=2
```

Typical uses include diagnostic counts, data availability inspection, missingness observation, and temporary QC diagnostics.

**Does not mean:** test a required rule.

`CHECK` asks *what do we observe?*; `VALIDATE` asks *did an expectation hold?*

### 3.3 FILTER

**Means:** Retain or exclude observations according to a condition, including selection of an analysis population or analysis subset.

```text
INFO [FILTER] [ADSL] SAFFL == 'Y' applied – N=254 → 249
INFO [FILTER] [ADAE] TRTEMFL == 'Y' applied – N=4127 → 2964
```

Typical uses include Safety/ITT/FAS/PP selection, treatment-emergent AE selection, parameter filtering, visit windows, and analysis windows.

For a named population, keep the source dataset identity and record the resulting concept separately:

```text
ADSL + SAFFL == 'Y' → Safety Population
ADSL + ITTFL == 'Y' → ITT Population
```

**Does not mean:** select columns, order rows, group observations, or reshape data.

Creating a named population does not require a `POPULATION` operation; it remains `FILTER`.

### 3.4 SORT

**Means:** Intentionally order observations by one or more keys where order matters to subsequent processing, derivation, reporting, or reproducibility.

```text
INFO [SORT] [ADAE] ordered – by=USUBJID,AESTDTC
INFO [SORT] [ADLBC] ordered – by=USUBJID,AVISITN
```

Typical uses include chronological AE processing, LOCF preparation, lag/lead logic, and deterministic listing order.

### 3.5 DERIVE

**Means:** Create a named analytical concept that did not previously exist, such as a variable, flag, category, parameter, endpoint-derived value, or analysis value.

```text
INFO [DERIVE] [AGEGR1] created – dataset=ADSL, source=AGE
INFO [DERIVE] [TRTEMFL] created – dataset=ADAE
INFO [DERIVE] [CHG] created – dataset=ADLBC, source=AVAL,BASE
```

A new named analysis variable is normally `DERIVE` even when implemented by recoding, mapping, concatenation, or formatting. Use `TRANSFORM` when no new analytical concept is created.

### 3.6 TRANSFORM

**Means:** Materially change representation, structure, normalization, reshaping, or reporting preparation when no more specific TRACE operation expresses the intent.

```text
INFO [TRANSFORM] [AESTDTC] parsed to analysis date
INFO [TRANSFORM] [disposition_summary] pivoted to treatment columns
INFO [TRANSFORM] [subject_listing] prepared display columns
```

`TRANSFORM` is a controlled fallback, not a catch-all. Prefer a more specific operation when one fits.

### 3.7 MERGE

**Means:** Combine two or more analytical objects when the contributing sources matter.

```text
INFO [MERGE] [ADAE + ADSL] merged – on=USUBJID, how=inner
INFO [MERGE] [AE counts + denominators] merged – on=TRT01A
```

Typical uses include adding subject-level attributes, joining denominators to summaries, and combining independently prepared analytical components.

When cardinality evidence matters, use explicit units such as `left_rows`, `right_rows`, `result_rows`, `matched_subjects`, or `unmatched_keys` rather than ambiguous counts.

### 3.8 AGGREGATE

**Means:** Reduce or group detailed observations into summary-level values using counts, percentages, sums, descriptive statistics, or similar reductions.

```text
INFO [AGGREGATE] [ADSL] participant counts created – by=TRT01A
INFO [AGGREGATE] [ADAE] subject incidence created – by=TRT01A,AEBODSYS,AEDECOD
INFO [AGGREGATE] [ADLBC] descriptive statistics created – by=TRTP,AVISIT
```

Counts, means, SDs, and percentages are `AGGREGATE`; ANCOVA, MMRM, Kaplan–Meier, and Cox regression are `ANALYZE`.

### 3.9 ANALYZE

**Means:** Apply a statistical analytical method, model, estimator, inferential procedure, or analysis algorithm beyond simple grouping/reduction.

The source dataset and analysis identity remain distinct:

```text
source:     ADTTE
analysis:   Overall Survival
method:     Kaplan-Meier
population: ITT
result:     km_curve
```

Examples:

```text
INFO [ANALYZE] [Overall Survival] Kaplan-Meier fitted – source=ADTTE, population=ITT
INFO [ANALYZE] [Week 24 glucose change] ANCOVA fitted – source=ADLBC, population=Efficacy
INFO [ANALYZE] [Change from baseline] MMRM fitted – source=ADVS, population=ITT
```

If the primary act is grouped summarization, use `AGGREGATE`; if a statistical method/model/estimator is applied, use `ANALYZE`.

### 3.10 VALIDATE

**Means:** Evaluate an explicit expectation, requirement, rule, tolerance, or acceptance criterion.

```text
INFO    [VALIDATE] [ADSL] USUBJID uniqueness – PASS
WARNING [VALIDATE] [T14_01] expected treatment groups present – FAIL
INFO    [VALIDATE] [QC comparison] production and QC results agree – PASS
```

Typical uses include uniqueness, required values, expected treatment arms, shell conformity, tolerance checks, cross-dataset consistency, and independent production/QC comparisons.

A `PASS` means that the implemented validation criterion evaluated successfully. It does **not** establish overall statistical correctness. Supporting diagnostics may be observed, supplied, or derived; their origin determines how strongly TRACE itself can claim to have observed the evidence.

`CHECK` observes; `VALIDATE` evaluates an expectation. `QC` is a workflow/context, not an operation.

### 3.11 OUTPUT

**Means:** Produce an externally consumable artifact.

```text
INFO [OUTPUT] [T14_01] written – outputs/T14_01.rtf
INFO [OUTPUT] [ADAE] written – adam/adae.xpt
```

Typical outputs include tables, listings, figures, derived datasets, RTF/PDF/Excel/CSV/JSON files, and QC reports.

`OUTPUT` records the production action. Physical artifact identity and optional hashes belong to program-level execution provenance rather than being repeated as event metrics.

## 4. Boundary rules

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
Require exactly two treatment groups          VALIDATE

AGE → AGEGR1                                  DERIVE
Pivot disposition rows to treatment columns   TRANSFORM

Count subjects by treatment                   AGGREGATE
Mean and SD by treatment                      AGGREGATE
Kaplan-Meier estimation                       ANALYZE
ANCOVA                                        ANALYZE
```

## 5. Statistical pressure test

The vocabulary has been pressure-tested against demographics, disposition, adverse-event, laboratory, vital-sign, exposure, survival, regression, longitudinal-model, listing, ADaM-derivation, and independent-QC workflows. No additional operation is currently required.

| Scenario | Typical TRACE sequence |
|---|---|
| Analysis population | `READ → FILTER → CHECK/VALIDATE` |
| Demographics | `READ → FILTER → DERIVE → AGGREGATE → VALIDATE → OUTPUT` |
| Disposition | `READ → FILTER → AGGREGATE → MERGE → TRANSFORM → OUTPUT` |
| Adverse events | `READ → FILTER → MERGE → AGGREGATE → VALIDATE → OUTPUT` |
| Laboratory summaries | `READ → FILTER → DERIVE → AGGREGATE → TRANSFORM → OUTPUT` |
| Vital-sign summaries | `READ → FILTER → DERIVE → AGGREGATE → TRANSFORM → OUTPUT` |
| Exposure | `READ → FILTER → DERIVE → AGGREGATE → OUTPUT` |
| Kaplan–Meier | `READ → FILTER → SORT → ANALYZE → VALIDATE → OUTPUT` |
| Cox regression | `READ → FILTER → ANALYZE → VALIDATE → OUTPUT` |
| MMRM | `READ → FILTER → DERIVE → ANALYZE → VALIDATE → OUTPUT` |
| ANCOVA | `READ → FILTER → MERGE → SORT → DERIVE → AGGREGATE → ANALYZE → TRANSFORM → OUTPUT` |
| Subject listing | `READ → FILTER → SORT → TRANSFORM → OUTPUT` |
| ADaM derivation | `READ → SORT → FILTER → MERGE → DERIVE → VALIDATE → OUTPUT` |
| Independent QC | `READ → MERGE → VALIDATE → OUTPUT` |

The table is illustrative rather than prescriptive. Record only operations that materially improve execution reviewability.

## 6. Selection guide

```text
External input acquired?                    → READ
Observation without an enforced rule?       → CHECK
Rows/observations selected or excluded?      → FILTER
Order intentionally changed?                 → SORT
New named analytical concept created?        → DERIVE
Representation or structure changed?         → TRANSFORM
Multiple analytical sources combined?        → MERGE
Detailed data reduced/grouped?                → AGGREGATE
Statistical method/model/estimator applied?   → ANALYZE
Explicit expectation tested?                  → VALIDATE
External artifact produced?                   → OUTPUT
```

If none fits cleanly, either the action is too low-level to deserve TRACE, `TRANSFORM` is the correct controlled operation, or a genuine vocabulary gap should be proposed deliberately.

## 7. Excluded terms

| Excluded term | Use instead | Reason |
|---|---|---|
| `POPULATION` | `FILTER` result | Population selection is row/observation selection, not a distinct execution operation |
| `SUMMARY` | `AGGREGATE` or `ANALYZE` | Ambiguous between summary calculation and statistical analysis |
| `SUBSET`, `WHERE`, `SELECT` | `FILTER` | Row-selection synonyms |
| `JOIN`, `COMBINE`, `APPEND`, `CONCAT` | `MERGE` | Multi-source combination synonyms in v0.1 |
| `LOAD`, `IMPORT`, `INGEST` | `READ` | Input-acquisition synonyms |
| `WRITE`, `EXPORT`, `SAVE` | `OUTPUT` | Artifact-production synonyms |
| `CALCULATE`, `COMPUTE`, `CREATE` | Depends on intent | Usually `DERIVE`, `AGGREGATE`, or `ANALYZE` |
| `QC` | Workflow/context | Not one execution operation |
| `ERROR`, `WARNING` | Severity | Not operations |

## 8. Lifecycle operations

`START`, `END`, and `STEP` belong to TRACE system vocabulary and should normally be generated by lifecycle/step mechanisms rather than emitted manually.

```text
INFO  [START] [T14_01] execution started
INFO  [END]   [T14_01] execution completed – duration=1.18s
ERROR [END]   [T14_01] execution failed – ValueError
```

## 9. Governance

The vocabulary should grow slowly. Add an operation only when realistic programs repeatedly require it, existing operations would distort the meaning, the proposed term has stable backend-independent semantics, and it improves both human and machine interpretation.

A library method name or a desire for prettier examples is not sufficient justification.

## 10. v0.1 decisions

- The canonical statistical vocabulary remains the eleven operations listed in Section 1.
- `START`, `END`, and `STEP` remain TRACE-managed system/lifecycle operations.
- `CHECK` and `VALIDATE` remain separate: observation versus explicit expectation.
- `DERIVE` and `TRANSFORM` remain separate: new analytical concept versus representation/structure change.
- `AGGREGATE` and `ANALYZE` remain separate: grouping/reduction versus statistical methodology.
- Analysis populations remain `FILTER` results; no `POPULATION` operation is introduced.
- Source identity and resulting analytical identity should both be preserved when both matter.
- `READ` and `OUTPUT` remain semantic events; physical artifact identity belongs to program-level provenance.
- Validation outcomes describe implemented criteria and must not be presented as proof of statistical correctness.
- Vocabulary extensions require explicit design review.
