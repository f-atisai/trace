# TRACE Reviewer Experience

**Phase:** 10 — Define the TRACE Reviewer Experience  
**Status:** Active design specification  
**Scope:** Reviewer model, diagnostic evidence, and Phase 10 validation goals

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
| Program-level provenance | Which execution and artifacts does this log belong to? | program, run ID, timestamps, input/output artifacts |

Semantic-event vocabulary is defined in [`../framework/core-operations-v0.1.md`](../framework/core-operations-v0.1.md). Program-level provenance is defined in [`provenance.md`](provenance.md).

### 3.1 Diagnostic evidence

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

the reviewer should be able to distinguish:

```text
Observed: TRACE inspected the runtime object and counted 249 rows.
Supplied: the program called TRACE with rows=249.
Derived:  TRACE calculated 249 from other recorded diagnostics.
```

TRACE must not present these cases as equivalent evidence.

Core may continue accepting supplied diagnostics. Future integrations can convert common diagnostics from supplied to observed evidence without changing operation semantics, consistent with [`object-vs-operation.md`](object-vs-operation.md).

#### Derivation rule

A derived value must identify its source diagnostics internally so its origin remains explainable:

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

without a row count. Missing optional diagnostics means only that TRACE did not record that evidence.

#### Operation-oriented diagnostic categories

The following categories describe high-value diagnostics rather than mandatory fields:

| Operation | Useful diagnostics | Notes |
|---|---|---|
| `READ` | `rows`, `columns` | Integrations can observe object dimensions; Core callers may supply them. |
| `CHECK` | check-specific metrics | Use explicit units where ambiguity is possible. |
| `FILTER` | `before_rows`, `after_rows`, `removed_rows` | `removed_rows` may be derived. |
| `SORT` | usually none | Sort keys are semantic/structural metadata. |
| `DERIVE` | derivation-specific metrics where useful | Do not add counts merely for consistency. |
| `TRANSFORM` | input/result dimensions where material | Useful for reshape or pivot operations. |
| `MERGE` | `left_rows`, `right_rows`, `result_rows`; explicit-unit match diagnostics | Prefer `matched_subjects` or `unmatched_keys` over ambiguous `matched`. |
| `AGGREGATE` | `input_rows`, `result_rows`; analysis-unit counts where useful | Distinguish rows from subjects or groups. |
| `ANALYZE` | method-specific diagnostics only when reviewer-relevant | Avoid reproducing statistical output in the log. |
| `VALIDATE` | comparison metric(s), expected criterion where needed, status | Diagnostic origin still matters. |
| `OUTPUT` | artifact properties where reviewer-relevant | Physical artifact identity and hashes belong to program-level provenance. |

Existing prototype names such as `before`, `after`, and `rows` may remain until API reconciliation. The conceptual model uses explicit units where an unqualified count could be mistaken for subjects, records, keys, or groups.

#### Validation evidence

`VALIDATE` combines an expectation with an outcome:

```text
VALIDATE [ADSL] USUBJID uniqueness – FAIL, duplicate_subjects=2
```

The failure status is semantic validation evidence. The diagnostic `duplicate_subjects=2` may independently be observed, supplied, or derived.

A validation does not become stronger merely because the programmer passes `passed=True`. Future integrations or validation helpers may observe the relevant metric and derive the outcome, but that is a later implementation decision.

## 4. Reviewer interpretation

A reviewer should be able to investigate expected inputs, population attrition, merge expansion or contraction, important derivations, analysis methods, validations, outputs, and whether reviewed artifacts belong to the recorded execution.

Diagnostic origin adds a second question:

> **Did TRACE observe this value, or did it record a value supplied by the program?**

For example:

```text
TRACE EXECUTION
Program: T14_01
Run ID:  7eab...
Started: 2026-09-12T10:42:18Z
Ended:   2026-09-12T10:42:19Z
Inputs:  data/adam/adsl.parquet
Outputs: outputs/t14_01.rtf

INFO [READ]     [ADSL] loaded – rows=254
INFO [FILTER]   [ADSL] SAFFL == 'Y' applied – rows=254 → 249
INFO [MERGE]    [ADSL + ADAE] merged – left_rows=249, right_rows=731, result_rows=814
WARN [VALIDATE] [ADSL] USUBJID uniqueness – FAIL, duplicate_subjects=17
INFO [OUTPUT]   [T14_01] written – outputs/t14_01.rtf
```

The provenance block identifies the run and artifacts once. Its detailed semantics are owned by [`provenance.md`](provenance.md).

A future structured representation must retain diagnostic origins even if concise text rendering does not label every value inline. Machine-readable output, reviewer tooling, or an expanded rendering should be able to expose the distinction.

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

## 9. Related design work

- [`domain-model.md`](domain-model.md) — event structure and core domain concepts.
- [`../framework/core-operations-v0.1.md`](../framework/core-operations-v0.1.md) — operation vocabulary and semantic boundaries.
- [`tier-1-api.md`](tier-1-api.md) — public Tier 1 API contract.
- [`object-vs-operation.md`](object-vs-operation.md) — Core-versus-integration boundary.
- [`provenance.md`](provenance.md) — program-level execution and artifact provenance.
- [`reference-prototype-findings.md`](reference-prototype-findings.md) — empirical prototype findings.
