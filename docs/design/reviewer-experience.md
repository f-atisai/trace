# TRACE Reviewer Experience

**Phase:** 10 — Define the TRACE Reviewer Experience  
**Status:** Active design specification  
**Scope:** Reviewer model, execution evidence, provenance, and Phase 10 validation goals

## 1. Purpose

Phase 10 asks:

> **Does the recorded analytical execution make sense, and is it consistent with the program and output being reviewed?**

TRACE is a review companion. It should help a qualified reviewer reconstruct important analytical execution without implying that a clean log establishes statistical correctness.

## 2. Reviewer model

```text
Specification / source / Quarto
              │
              ▼
        actual execution
              │
              ▼
            TRACE
              │
              ▼
      statistical output
```

| Artifact | Primary review question |
|---|---|
| Specification, source, or Quarto | What was intended, why, and how was it coded? |
| TRACE | What happened during this execution? |
| Statistical output | What resulted, and is it correct? |

## 3. Reviewable execution evidence

TRACE reviewer value comes from three complementary forms of evidence:

```text
semantic events
      +
observed diagnostics
      +
program-level provenance
      =
reviewable execution evidence
```

| Evidence | Answers | Typical examples |
|---|---|---|
| Semantic event | What analytical activity occurred? | `READ`, `FILTER`, `MERGE`, `ANALYZE`, `OUTPUT` |
| Diagnostic | What measurable evidence describes that activity? | row counts, subject counts, duplicates, result dimensions |
| Program-level provenance | Which execution and artifacts does this log belong to? | program, run ID, timestamp, input/output artifacts |

### 3.1 Semantic events

Semantic events describe what kind of statistical-programming activity occurred. Their vocabulary and boundaries are defined in [`../framework/core-operations-v0.1.md`](../framework/core-operations-v0.1.md).

### 3.2 Diagnostic evidence

A diagnostic is a measurable fact or value associated with an operation. Examples include row counts, column counts, subject counts, duplicate counts, merge dimensions, validation measurements, and artifact properties.

Diagnostics are not automatically observations merely because they appear in a TRACE event. Their evidentiary value depends on how TRACE obtained them.

#### Evidence origin

TRACE uses three origins for diagnostic values:

| Origin | Meaning | Reviewer interpretation |
|---|---|---|
| **Observed** | TRACE or a supported integration inspected runtime state or an artifact and collected the value directly. | Strongest execution evidence available from TRACE. |
| **Supplied** | The programmer or calling code passed the value to TRACE. TRACE recorded it but did not independently inspect the underlying object. | Useful execution context, but not independently observed by TRACE. |
| **Derived** | TRACE calculated the value from other diagnostic values whose origins are known. | Confidence follows the source diagnostics and the deterministic derivation. |

`asserted` is not used as a general diagnostic origin. An assertion implies an expectation or claim about correctness; that semantic role belongs to `VALIDATE`. A supplied row count is therefore **supplied**, not asserted.

Semantic fields such as operation, object, condition, method, and result identity are declarations of what the program is doing and are not diagnostic origins.

#### The confidence rule

When TRACE reports:

```text
rows=249
```

the reviewer should be able to distinguish these cases:

```text
Observed: TRACE inspected the runtime object and counted 249 rows.
Supplied: the program called TRACE with rows=249.
Derived:  TRACE calculated 249 from other recorded diagnostics.
```

TRACE must not present these cases as equivalent evidence.

The initial Core API may continue accepting supplied diagnostics. This sprint does not require runtime-object inspection or change Tier 1 signatures. Future integrations can convert common diagnostics from supplied to observed evidence without changing operation semantics, consistent with [`object-vs-operation.md`](object-vs-operation.md).

#### Derivation rule

A derived value must identify its source diagnostics internally so its origin remains explainable. For example:

```text
before_rows=254  observed
after_rows=249   observed
removed_rows=5   derived from before_rows - after_rows
```

If either source count was supplied, the derived value must not be represented as independently observed.

#### Diagnostics are optional

TRACE does not require every possible diagnostic for every operation. Instrumentation should remain proportionate to reviewer value and collection cost.

A useful event may therefore be:

```text
INFO [DERIVE] [AGEGR1] created – dataset=ADSL, source=AGE
```

without a row count. Missing optional diagnostics should mean only that TRACE did not record that evidence; it should not imply zero, failure, or an incomplete execution.

#### Operation-oriented diagnostic categories

The following categories describe high-value diagnostics rather than mandatory fields:

| Operation | Useful diagnostics | Notes |
|---|---|---|
| `READ` | `rows`, `columns` | Integrations can observe object dimensions; Core callers may supply them. |
| `CHECK` | check-specific metrics | Units should be explicit where ambiguity is possible, e.g. `missing_subjects` rather than `missing`. |
| `FILTER` | `before_rows`, `after_rows`, `removed_rows` | `removed_rows` may be derived when before/after counts are available. |
| `SORT` | usually none | Sort keys are semantic/structural metadata, not diagnostics. |
| `DERIVE` | derivation-specific metrics where useful | Do not add counts merely for consistency. |
| `TRANSFORM` | input/result dimensions where material | Especially useful for reshape or pivot operations. |
| `MERGE` | `left_rows`, `right_rows`, `result_rows`; explicit-unit match diagnostics | Prefer `matched_subjects` or `unmatched_keys` over ambiguous `matched`. |
| `AGGREGATE` | `input_rows`, `result_rows`; analysis-unit counts where useful | Distinguish rows from subjects or groups. |
| `ANALYZE` | method-specific diagnostics only when reviewer-relevant | Model results are not automatically TRACE diagnostics; avoid reproducing statistical output in the log. |
| `VALIDATE` | observed comparison metric(s), expected criterion where needed, status | `PASS`/`FAIL` records the validation outcome; diagnostic origin still matters. |
| `OUTPUT` | artifact size and optional hash where available | Artifact identity belongs to output/provenance semantics; hashes are addressed by the provenance design. |

Existing prototype names such as `before`, `after`, and `rows` may remain until API reconciliation. The conceptual model uses explicit units (`before_rows`, `after_rows`, `input_rows`, `result_rows`) to prevent a reviewer from assuming that an unqualified count represents subjects rather than records.

#### Validation evidence

`VALIDATE` combines an expectation with an outcome. For example:

```text
VALIDATE [ADSL] USUBJID uniqueness – FAIL, duplicate_subjects=2
```

The failure status is semantic validation evidence. The diagnostic `duplicate_subjects=2` may independently be observed, supplied, or derived.

A validation does not become stronger merely because the programmer passes `passed=True`. Future integrations or validation helpers may be able to observe the relevant metric and derive the outcome, but that is an implementation decision for a later phase.

### 3.3 Program-level provenance

Execution provenance is recorded once at program level rather than repeated across semantic events.

Initial Phase 10 provenance consists of:

```text
program
run_id
executed_at
input_artifacts
output_artifacts
optional artifact hashes
```

Its purpose is to answer:

> Which execution and physical artifacts does this TRACE log belong to?

A reviewer-facing provenance block may look like:

```text
TRACE EXECUTION

Program:  T14_01
Run ID:   7eab...
Executed: 2026-09-12T10:42:18Z

Input artifacts:
  data/adam/adsl.parquet
  sha256: 8f31...

Output artifacts:
  outputs/tlf_population.rtf
  sha256: a791...
```

Hashes are optional artifact identifiers. Broader environment fingerprinting—Git state, Python/package versions, operating system, hostname, or user identity—remains out of scope until a concrete need justifies it.

The exact API and storage model for provenance are deferred to the provenance design sprint.

## 4. Reviewer interpretation

A reviewer should be able to investigate expected inputs, population attrition, merge expansion or contraction, important derivations, analysis methods, validations, outputs, and whether reviewed artifacts belong to the recorded execution.

Diagnostic origin adds a second question:

> **Did TRACE observe this value, or did it record a value supplied by the program?**

For example:

```text
TRACE EXECUTION
Program: T14_01
Run ID:  7eab...
Executed: 2026-09-12T10:42:18Z
Inputs:  data/adam/adsl.parquet
Outputs: outputs/t14_01.rtf

INFO [READ]     [ADSL] loaded – rows=254
INFO [FILTER]   [ADSL] SAFFL == 'Y' applied – rows=254 → 249
INFO [MERGE]    [ADSL + ADAE] merged – left_rows=249, right_rows=731, result_rows=814
WARN [VALIDATE] [ADSL] USUBJID uniqueness – FAIL, duplicate_subjects=17
INFO [OUTPUT]   [T14_01] written – outputs/t14_01.rtf
```

A future structured representation must retain diagnostic origins even if the concise text rendering does not label every value inline. Machine-readable output, reviewer tooling, or an expanded rendering should be able to expose the distinction. TRACE must not discard origin metadata merely to keep the text log compact.

## 5. Quarto and conventional Python

With Quarto, the document owns narrative, rationale, methods, and implementation context while TRACE records execution evidence. Without Quarto, source code provides that context. TRACE does not require a Quarto-specific extension.

```text
analysis.qmd       ──────► TRACE log ──────► TLF
intent + code               execution         result

tlf_population.py ──────► TRACE log ──────► tlf_population.rtf
code                         execution         result
```

## 6. Boundaries

TRACE records execution evidence. It does not establish statistical correctness.

A program can execute exactly as coded and still implement the wrong analysis. TRACE complements rather than replaces specification review, code review, independent programming/QC, dataset validation, TLF review, statistical review, and clinical interpretation.

TRACE must preserve these distinctions:

```text
what the programmer intended
what the program did
what TRACE observed
what the programmer supplied
what TRACE derived
what the reviewer concluded
```

The governing principle is:

> **TRACE provides execution evidence and reviewability; independent review remains responsible for establishing statistical correctness.**

## 7. Phase 10 scope and validation

Phase 10 should validate whether a reviewer can answer:

1. What important statistical-programming operations occurred, and in what order?
2. How did important data or result dimensions evolve?
3. Which diagnostics were observed, supplied, or derived?
4. Which diagnostics deserve investigation?
5. Which explicit validations passed or failed?
6. Which analysis method was executed for which analysis?
7. Which input and output artifacts belong to the execution?
8. Can the reviewer reconcile TRACE evidence with the source or Quarto document and resulting output?
9. Does TRACE expose this evidence without implying that execution evidence proves statistical correctness?

Phase 10 does not require runtime DataFrames in Core, infer Python variable names, capture subject-level clinical data by default, or expand provenance without a demonstrated requirement.

When completeness and readability conflict, TRACE should optimize for **accurate, proportionate, reviewable evidence**. More logging is not automatically better evidence.

## 8. Phase 10.4 decisions

- Diagnostic values have an explicit evidence origin: **observed**, **supplied**, or **derived**.
- `asserted` is reserved conceptually for expectations/validation rather than used as a generic diagnostic origin.
- Core may continue accepting supplied diagnostics; supplied values must not be represented as TRACE-observed evidence.
- Integrations may inspect runtime objects to produce observed diagnostics without redefining operation semantics.
- Derived diagnostics inherit the evidentiary limitations of their source diagnostics.
- Diagnostic units should be explicit whenever a count could mean rows, subjects, keys, groups, or another analytical unit.
- Diagnostics are optional and operation-specific; TRACE should not collect metrics solely for uniformity.
- Structured TRACE representations must preserve diagnostic origin even when concise text rendering omits origin labels.
- Phase 10.4 defines semantics only. No pandas, Polars, PyArrow, or other runtime inspection is implemented in this sprint.

## 9. Relationship to earlier design work

- [`domain-model.md`](domain-model.md) owns event structure and core domain concepts.
- [`../framework/core-operations-v0.1.md`](../framework/core-operations-v0.1.md) owns operation vocabulary and semantic boundaries.
- [`tier-1-api.md`](tier-1-api.md) owns the public Tier 1 API contract.
- [`object-vs-operation.md`](object-vs-operation.md) owns the Core-versus-integration boundary.
- [`reference-prototype-findings.md`](reference-prototype-findings.md) preserves empirical prototype findings.

Phase 10.4 refines the reviewer-facing meaning of diagnostic evidence without changing those contracts or implementing runtime integrations.
