# TRACE Core Operations v0.1

**Phase:** 1 — Define the Canonical TRACE Vocabulary  
**Status:** Draft normative specification  
**Version:** 0.1  
**Scope:** Core operation vocabulary only; no public method signatures or implementation details

## 1. Purpose

TRACE deliberately imposes a controlled execution vocabulary for statistical programming.

The purpose is consistency.

A statistical program should not describe equivalent operations using competing terms such as:

```text
SUBSET
FILTER
WHERE
SELECT
```

or:

```text
JOIN
MERGE
COMBINE
```

unless those words represent genuinely different semantics.

TRACE therefore classifies meaningful execution events using a small canonical vocabulary.

The Phase 1 core vocabulary is:

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

Lifecycle operations:

```text
START
END
```

are reserved for TRACE-managed program and step lifecycle events.

`SUMMARY` is not part of TRACE Core Operations v0.1 because its meaning overlaps too heavily with `AGGREGATE` and `ANALYZE`.

---

## 2. Vocabulary Design Principles

### 2.1 Represent intent, not syntax

TRACE classifies statistical-programming meaning rather than the Python method used.

For example:

```python
adsl.query("SAFFL == 'Y'")
adsl.loc[adsl["SAFFL"] == "Y"]
```

both represent:

```text
FILTER
```

### 2.2 One primary term per concept

TRACE should prefer one term and reject unnecessary synonyms.

Examples:

```text
FILTER    not SUBSET / WHERE / SELECT
MERGE     not JOIN / COMBINE
AGGREGATE not SUMMARY / GROUP-SUMMARIZE
OUTPUT    not WRITE / EXPORT / SAVE
```

Alternative wording may appear naturally in an event's `action`, but not as competing operation names.

### 2.3 Operations describe meaningful execution events

Not every line of Python deserves a TRACE event.

TRACE operations should represent steps that materially explain data provenance, population changes, variable creation, dataset structure, analytical processing, validation, generated outputs, or execution lifecycle.

### 2.4 Operations are backend-independent

An operation must remain meaningful across pandas, Polars, PyArrow, SQL, DuckDB, NumPy, and custom Python.

### 2.5 Operations are semantically stable

Once an operation becomes part of the stable TRACE vocabulary, its meaning must not drift casually. Structured downstream consumers may depend on it.

---

## 3. Core Operations

### 3.1 READ

**Definition:** `READ` records the acquisition or loading of an input object into the current statistical-program execution.

**Intent:** Use `READ` when data, metadata, configuration, or another externally persisted analytical object becomes available to the program.

Typical objects include `ADSL`, `ADAE`, `DM`, metadata workbooks, shell specifications, and configuration files.

Example:

```json
{
  "operation": "READ",
  "object": "ADSL",
  "action": "loaded",
  "metrics": {
    "rows": 754,
    "columns": 16
  }
}
```

Possible rendering:

```text
INFO [READ] [ADSL] loaded – N=754, Vars=16
```

**Includes:** reading datasets, loading files, importing persisted metadata, obtaining input tables from supported data sources.

**Does not include:** creating a derived dataset in memory, generating output, or merely referencing an already-loaded object.

**Avoid as operation synonyms:** `LOAD`, `IMPORT`, `INGEST`, `OPEN`.

---

### 3.2 CHECK

**Definition:** `CHECK` records an observational or diagnostic inspection whose primary purpose is to understand execution state rather than assert a required outcome.

**Intent:** Use `CHECK` when the program examines something and records what it found, but a pass/fail contract is not being enforced.

Examples:

```text
INFO [CHECK] [ADSL] treatment groups inspected – groups=3
INFO [CHECK] [ADAE] missing AEDECOD reviewed – N=12
```

**Typical uses:** diagnostic counts, exploratory checks, informational existence checks, temporary QC instrumentation, runtime inspection.

**CHECK versus VALIDATE:**

`CHECK` asks:

> What do we observe?

`VALIDATE` asks:

> Did the data or result satisfy an expected rule?

If an operation has a defined expected outcome such as uniqueness, completeness, expected treatment groups, or acceptable tolerance, prefer `VALIDATE`.

**Avoid as operation synonyms:** `INSPECT`, `REVIEW`, `VERIFY`, `TEST`.

---

### 3.3 FILTER

**Definition:** `FILTER` records a row- or observation-selection operation that changes or defines an analysis population or subset.

**Intent:** Use `FILTER` whenever observations are retained or excluded according to a condition.

Example:

```text
INFO [FILTER] [ADSL] SAFFL == 'Y' applied – N=754 → 720
```

Structured concept:

```json
{
  "operation": "FILTER",
  "object": "ADSL",
  "action": "SAFFL == 'Y' applied",
  "metrics": {
    "before": 754,
    "after": 720,
    "removed": 34
  }
}
```

Typical clinical uses include safety/FAS/ITT/PP population selection, treatment-emergent AE filtering, visit-window filtering, randomized-subject selection, and analysis-window filtering.

**Does not include:** selecting columns, sorting, grouping without row removal, or generic structural transformations.

**Canonical synonym policy:** `SUBSET`, `WHERE`, `SELECT`, and `SCREEN` are not separate TRACE operations.

---

### 3.4 SORT

**Definition:** `SORT` records an intentional ordering of observations according to one or more keys.

**Intent:** Use `SORT` when observation order matters to subsequent statistical processing, reporting, derivation, or reproducibility.

Examples:

```text
INFO [SORT] [ADAE] ordered – by=USUBJID,AESTDTC
INFO [SORT] [ADSL] ordered – by=TRT01AN,USUBJID
```

Typical clinical uses include chronological AE processing, by-subject derivations, deterministic listing order, treatment-group table preparation, and lag/lead logic.

**Does not include:** statistical ranking, grouping, or purely cosmetic display ordering with no execution significance.

**Avoid as operation synonyms:** `ORDER`, `ORDER_BY`, `ARRANGE`.

---

### 3.5 DERIVE

**Definition:** `DERIVE` records creation of a new analytical variable, flag, parameter, or value from existing information.

**Intent:** Use `DERIVE` when the key semantic event is creation of a new analytical concept.

Examples:

```text
INFO [DERIVE] [AGEGR1] created – dataset=ADSL, source=AGE
INFO [DERIVE] [TRTEMFL] created – dataset=ADAE
INFO [DERIVE] [AVAL] created – parameter=CHG
```

Typical clinical uses include analysis flags, age groups, baseline flags, treatment-emergent flags, change-from-baseline values, analysis dates/days, and parameter derivations.

**DERIVE versus TRANSFORM:**

Use `DERIVE` when a new analytical concept is created.

Use `TRANSFORM` when an existing representation is materially changed while its primary semantic identity remains the same.

```text
AGE → AGEGR1                              DERIVE
AESTDTC text → parsed date representation TRANSFORM
```

The distinction follows statistical intent, not merely whether a new physical Python column is assigned.

**Avoid as operation synonyms:** `CALCULATE`, `COMPUTE`, `CREATE`, `GENERATE`.

---

### 3.6 TRANSFORM

**Definition:** `TRANSFORM` records a material change in representation, structure, normalization, recoding, reshaping, or preparation of an existing analytical object when no more specific TRACE operation better expresses the intent.

**Intent:** `TRANSFORM` is the controlled general-purpose transformation operation. It should not become a catch-all.

Examples:

```text
INFO [TRANSFORM] [AESTDTC] parsed to analysis date
INFO [TRANSFORM] [LB] reshaped – long to wide
INFO [TRANSFORM] [SEX] recoded – M/F to Male/Female
```

Typical uses include parsing date/time values, recoding representations, reshaping, normalization, standardizing categories, and analytically meaningful type conversion.

Use a more specific operation when possible:

```text
row selection        → FILTER
ordering             → SORT
new analytical value → DERIVE
combining datasets   → MERGE
group summarization  → AGGREGATE
statistical method   → ANALYZE
```

**Avoid as top-level synonyms:** `MODIFY`, `CONVERT`, `RESHAPE`, `RECODE`, `NORMALIZE`.

---

### 3.7 MERGE

**Definition:** `MERGE` records combination of two or more analytical objects where provenance of the contributing sources matters.

**Intent:** Use `MERGE` when multiple input datasets or table-like objects are combined into one analytical result.

Example:

```text
INFO [MERGE] [ADAE + ADSL] merged – on=USUBJID, how=left
```

Structured concept:

```json
{
  "operation": "MERGE",
  "object": "ADAE + ADSL",
  "action": "merged",
  "details": {
    "on": ["USUBJID"],
    "how": "left",
    "result": "ADAE_ANALYSIS"
  },
  "metrics": {
    "left_rows": 4127,
    "right_rows": 754,
    "result_rows": 4127
  }
}
```

Typical clinical uses include adding ADSL treatment information to BDS/OCCDS data, subject-level enrichment, bringing denominators into event data, and combining independently prepared analytical components.

**JOIN versus MERGE:** TRACE v0.1 uses `MERGE` as the umbrella term. Join type belongs in structured details such as `how="left"`.

For v0.1, row concatenation may also be represented as `MERGE` with a structured mode such as `concat_rows`. If real use shows materially different semantics, a future dedicated operation can be proposed deliberately.

**Avoid as operation synonyms:** `JOIN`, `COMBINE`, `APPEND`, `CONCAT`, `LINK`.

---

### 3.8 AGGREGATE

**Definition:** `AGGREGATE` records reduction or grouping of detailed observations into summary-level values.

**Intent:** Use `AGGREGATE` when rows are summarized by groups or across an analysis population using counts, sums, descriptive statistics, or similar reductions.

Examples:

```text
INFO [AGGREGATE] [ADSL] summarized – by=TRT01A,SEX
INFO [AGGREGATE] [ADAE] incidence counts created – by=TRT01A,AEDECOD
```

Typical uses include counts and percentages, treatment-group summaries, descriptive statistics, subject counts by category, AE incidence tabulation, and visit-level summary preparation.

**AGGREGATE versus ANALYZE:**

Use `AGGREGATE` when the primary operation is grouping/reduction.

Use `ANALYZE` when applying a statistical analytical procedure, model, or estimator.

```text
count subjects by treatment       → AGGREGATE
mean and SD by treatment          → AGGREGATE
Kaplan-Meier estimation           → ANALYZE
Cox proportional hazards model    → ANALYZE
ANCOVA                             → ANALYZE
```

**Why not SUMMARY:** `SUMMARY` is ambiguous between data aggregation, statistical analysis, execution summary, and report output. `AGGREGATE` is more precise.

---

### 3.9 ANALYZE

**Definition:** `ANALYZE` records application of a statistical analytical method, estimator, model, inferential procedure, or analysis algorithm whose primary purpose extends beyond simple grouping and reduction.

**Intent:** Use `ANALYZE` for statistical methodology.

Examples:

```text
INFO [ANALYZE] [OS] Kaplan-Meier estimate computed – population=ITT
INFO [ANALYZE] [AVAL] ANCOVA fitted – parameter=CHANGE
INFO [ANALYZE] [ORR] exact confidence interval computed
```

Typical uses include Kaplan-Meier estimation, Cox regression, logistic regression, ANCOVA, MMRM, hypothesis tests, confidence intervals, statistical estimators, and clinically meaningful analysis algorithms.

**Does not include:** simple counts/group summaries (`AGGREGATE`), variable creation (`DERIVE`), result checking (`VALIDATE`), or artifact generation (`OUTPUT`).

---

### 3.10 VALIDATE

**Definition:** `VALIDATE` records evaluation of an explicit expectation, rule, requirement, tolerance, or acceptance criterion.

**Intent:** Use `VALIDATE` when an outcome can meaningfully be expressed as success/failure or equivalent.

Examples:

```text
INFO [VALIDATE] [ADSL] USUBJID uniqueness – PASS
WARNING [VALIDATE] [T14_01] expected treatment groups present – FAIL
INFO [VALIDATE] [QC] production and QC results agree – PASS
```

Typical clinical uses include uniqueness, required-value checks, expected population counts, expected treatment arms, shell conformity, production/QC comparison, tolerance checks, output presence, and cross-dataset consistency.

**VALIDATE versus CHECK:**

```text
Inspect number of treatment groups       → CHECK
Require exactly three treatment groups   → VALIDATE
```

**Avoid as operation synonyms:** `VERIFY`, `ASSERT`, `TEST`, `QC`.

`QC` is a workflow/context, not one operation type.

---

### 3.11 OUTPUT

**Definition:** `OUTPUT` records successful or attempted production of an externally consumable artifact.

**Intent:** Use `OUTPUT` when TRACE needs to record what the program produced.

Typical objects include tables, listings, figures, datasets, RTF/PDF/Excel/CSV/JSON files, QC reports, and execution manifests.

Example:

```text
INFO [OUTPUT] [T14_01] written – outputs/T14_01.rtf
```

Structured concept:

```json
{
  "operation": "OUTPUT",
  "object": "T14_01",
  "action": "written",
  "details": {
    "path": "outputs/T14_01.rtf",
    "format": "RTF",
    "type": "TABLE"
  }
}
```

**Includes:** externally meaningful tables, listings, figures, derived datasets, manifests, and downstream files.

**Does not include:** temporary in-memory objects, incidental cache files, or debug-only `print()` statements.

**Avoid as operation synonyms:** `WRITE`, `EXPORT`, `SAVE`, `EMIT`, `PUBLISH`.

---

## 4. Lifecycle Operations

Lifecycle operations belong to the TRACE system vocabulary but are not ordinary statistical-programmer domain actions.

### 4.1 START

**Definition:** `START` records the beginning of a bounded execution scope.

Examples:

```text
INFO [START] [T14_01] execution started
INFO [START] [Analysis population] step started
```

Potential scopes include program, step, analysis, and output generation.

`START` should normally be generated by TRACE lifecycle mechanisms rather than manually emitted throughout user code.

### 4.2 END

**Definition:** `END` records the termination of a bounded execution scope.

Examples:

```text
INFO [END] [T14_01] execution completed – duration=1.18s
ERROR [END] [T14_01] execution failed – ValueError
```

`END` may carry status, duration, and exception details and should normally be generated automatically by TRACE lifecycle handling.

---

## 5. Operations Explicitly Excluded from v0.1

### SUMMARY

Excluded because it overlaps with `AGGREGATE`, `ANALYZE`, execution summaries, and report summaries. Use the more precise operation.

### SUBSET / WHERE / SELECT

Use `FILTER` when row selection is the semantic intent.

### JOIN / COMBINE / APPEND / CONCAT

Use `MERGE` in v0.1 and capture the combination mode in structured details. Reconsider only if real programs demonstrate a distinct semantic need.

### LOAD / IMPORT / INGEST

Use `READ`.

### WRITE / EXPORT / SAVE

Use `OUTPUT`.

### CALCULATE / COMPUTE / CREATE

These are action verbs, not canonical top-level operations. Use `DERIVE`, `AGGREGATE`, or `ANALYZE` according to intent.

### QC

QC is a workflow or execution context, not an operation.

### ERROR / WARNING

These are severities, not operations.

---

## 6. Operation Selection Guide

```text
Did I acquire an external input?
    → READ

Am I observing something without enforcing a rule?
    → CHECK

Did I select/exclude observations?
    → FILTER

Did I intentionally reorder observations?
    → SORT

Did I create a new analytical variable/value/concept?
    → DERIVE

Did I materially change representation or structure?
    → TRANSFORM

Did I combine multiple analytical sources?
    → MERGE

Did I reduce/group detailed data into summary values?
    → AGGREGATE

Did I apply a statistical method/model/estimator?
    → ANALYZE

Did I test an explicit requirement or expectation?
    → VALIDATE

Did I produce an external artifact?
    → OUTPUT
```

If none fits cleanly, that suggests either the event is too low-level to deserve TRACE, `TRANSFORM` is the correct controlled general operation, or a genuine vocabulary gap should be proposed deliberately.

---

## 7. Clinical Programming Examples

### 7.1 Demographics table

```text
READ       ADSL
FILTER     Safety population
DERIVE     AGEGR1
AGGREGATE  treatment × age group counts
VALIDATE   treatment groups present
OUTPUT     T14_01
```

### 7.2 Adverse event summary

```text
READ       ADAE
READ       ADSL
FILTER     treatment-emergent AEs
MERGE      ADAE + ADSL
AGGREGATE  subjects by SOC/PT/treatment
VALIDATE   denominator groups
OUTPUT     T14_03
```

### 7.3 Kaplan-Meier figure

```text
READ       ADTTE
FILTER     ITT population / parameter
SORT       subject/time ordering if required
ANALYZE    Kaplan-Meier estimation
VALIDATE   expected treatment strata
OUTPUT     F14_01
```

### 7.4 ADaM derivation

```text
READ       SDTM inputs
SORT       source records
FILTER     relevant source observations
MERGE      subject-level attributes
DERIVE     analysis variables
VALIDATE   key ADaM expectations
OUTPUT     ADaM dataset
```

### 7.5 Independent QC program

```text
READ       production result
READ       independently generated QC result
CHECK      dimensions / labels / metadata
VALIDATE   production vs QC equality
OUTPUT     comparison report
```

---

## 8. Relationship to Phase 0 Event Model

The operation vocabulary occupies one field in the TRACE Event:

```text
TRACE Event
├── severity
├── operation  ← Phase 1 vocabulary
├── object
├── action
├── metrics
├── details
├── status
└── context
```

An operation is not a complete message. It supplies the canonical event category; the other fields supply the specific execution meaning.

---

## 9. Vocabulary Governance

The TRACE vocabulary should grow slowly.

A new operation should be added only when:

1. realistic statistical programs repeatedly require it;
2. existing operations cannot express it without semantic distortion;
3. the proposed operation has a stable definition;
4. it is meaningfully distinct from existing operations;
5. it remains backend-independent; and
6. it is useful for both human logs and machine consumers.

A Python library method name is not sufficient justification for a new TRACE operation.

---

## 10. Phase 1 Decisions

**P1-01** — TRACE Core Operations v0.1 are:

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

**P1-02** — `START` and `END` are reserved lifecycle operations.

**P1-03** — `SUMMARY` is excluded from v0.1.

**P1-04** — `FILTER` is the canonical row-selection term.

**P1-05** — `MERGE` is the canonical multi-source combination term for v0.1.

**P1-06** — `AGGREGATE` and `ANALYZE` remain separate: grouping/reduction versus statistical methodology.

**P1-07** — `CHECK` and `VALIDATE` remain separate: observation versus explicit expectation.

**P1-08** — `DERIVE` and `TRANSFORM` remain separate: new analytical concept versus changed representation/structure.

**P1-09** — Operations represent statistical-programming intent, not backend method names.

**P1-10** — Vocabulary extensions require explicit design review rather than ad hoc new operation strings.

---

## 11. Phase 1 Acceptance Criteria

Phase 1 is complete when:

1. every core operation has a distinct definition;
2. common clinical-programming actions map predictably to the vocabulary;
3. competing synonyms have an explicit canonical replacement;
4. `CHECK` versus `VALIDATE` is clear;
5. `DERIVE` versus `TRANSFORM` is clear;
6. `AGGREGATE` versus `ANALYZE` is clear;
7. `SUMMARY` is intentionally excluded;
8. lifecycle operations are separated from ordinary domain operations;
9. the vocabulary remains dataframe-library independent; and
10. the vocabulary can classify realistic table, listing, figure, ADaM, and QC workflows.

---

## 12. TRACE Core Operations v0.1

The resulting canonical vocabulary is:

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

with TRACE-managed lifecycle operations:

```text
START
END
```

This vocabulary becomes the semantic foundation for the next API-design phase.
