# TRACE Reviewer Experience

**Phase:** 10 — Define the TRACE Reviewer Experience  
**Status:** Active design charter  
**Scope:** Reviewer model, execution evidence, provenance, and Phase 10 validation goals

## 1. Purpose

Phase 10 asks a new question of TRACE:

> **Does the recorded analytical execution make sense, and is it consistent with the program and output being reviewed?**

Earlier phases focused primarily on whether TRACE was natural and useful for the statistical programmer. Phase 10 evaluates TRACE as a **review companion**.

It does not begin by assuming that the API must change. Realistic statistical-programming examples should determine whether the existing design captures sufficient execution evidence.

## 2. Reviewer model

TRACE sits between implementation and analytical result:

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

The artifacts answer different questions:

| Artifact | Primary review question |
|---|---|
| Specification, source, or Quarto | What was intended, why, and how was it coded? |
| TRACE | What happened during this execution? |
| Statistical output | What resulted, and is it correct? |

TRACE should help a qualified reviewer reconstruct the important analytical path without requiring the entire runtime sequence to be inferred from source code alone.

## 3. Reviewable execution evidence

TRACE reviewer value comes from three complementary forms of evidence:

```text
semantic events
      +
observed diagnostics
      +
execution provenance
      =
reviewable execution evidence
```

### 3.1 Semantic events

Semantic events describe **what kind of statistical-programming activity occurred**.

TRACE uses the canonical vocabulary defined in [`../framework/core-operations-v0.1.md`](../framework/core-operations-v0.1.md). Phase 10 tests that vocabulary from the reviewer's perspective; it does not redefine operation semantics.

### 3.2 Observed diagnostics

Diagnostics describe measurable evidence about an operation, for example:

```text
rows=254
rows=254 → 249
left_rows=249
right_rows=731
result_rows=814
duplicates=17
```

Phase 10 must preserve the distinction between diagnostics TRACE actually observes and values merely asserted by the programmer. That distinction affects how much evidentiary weight a reviewer should place on the log.

The Core-versus-integration architecture for collecting runtime evidence is defined in [`object-vs-operation.md`](object-vs-operation.md).

### 3.3 Execution provenance

Initial Phase 10 provenance is deliberately narrow:

```text
execution timestamp
input artifacts
output artifacts
artifact hashes, where useful and safe
```

Existing execution identity such as `program` and `run_id` remains relevant.

Broader environment fingerprinting—Git state, Python/package versions, operating system, hostname, or user identity—remains out of scope until a concrete review or reproducibility need justifies it.

## 4. What reviewers should look for

A reviewer should be able to use TRACE to investigate:

- whether the expected input artifacts were read;
- whether row, subject, or result dimensions changed plausibly;
- unexpected attrition after filters;
- unexpected expansion or contraction after merges;
- important derivations and transformations occurring in the expected sequence;
- whether the intended analysis method was executed for the expected analysis or population;
- diagnostics from checks and validations, including failures that did not stop execution;
- whether the expected outputs were produced; and
- whether the reviewed input/output artifacts belong to the recorded execution.

Not every event deserves equal attention. TRACE should make the analytical journey easy to reconstruct and make unusual evidence easy to spot.

Example:

```text
INFO [READ]     [ADSL] rows=254
INFO [FILTER]   [Safety Population] rows=254 → 249
INFO [MERGE]    [Safety AEs] left_rows=249 right_rows=731 result_rows=814
WARN [VALIDATE] [USUBJID uniqueness] FAIL duplicates=17
INFO [OUTPUT]   [AE Summary] t14-2-01.rtf
```

The reviewer can immediately see a population reduction, later merge expansion, a failed uniqueness expectation, continued execution, and production of an output. TRACE should make that story visible without forcing the reviewer to search a long runtime log for isolated messages.

## 5. Quarto and conventional Python

### With Quarto

When the analysis is implemented in Quarto:

```text
analysis.qmd  ──────►  TRACE log  ──────►  TLF
     │                    │                 │
 intent + code         execution         result
```

Quarto owns narrative, rationale, methods, and implementation context. TRACE should not become a second narrative specification or require programmers to restate analytical rationale in log calls.

### Without Quarto

For a conventional Python program:

```text
tlf_population.py  ──────► TRACE log ──────► tlf_population.rtf
       │                        │                       │
     code                  execution                 result
```

The reviewer uses the source for implementation context and TRACE as a concise execution map.

In either workflow, TRACE remains execution-format agnostic. Quarto is supported naturally because it executes Python code; TRACE does not require a Quarto-specific extension.

## 6. Boundaries

TRACE records execution evidence. It does not establish statistical correctness.

A program can execute exactly as coded and still implement the wrong analysis. A clean TRACE log therefore does not prove that the specification, method, derivation, source data, TLF, or clinical interpretation is correct.

TRACE complements rather than replaces specification review, code review, independent programming/QC, dataset validation, TLF review, statistical review, and clinical interpretation.

The governing principle is:

> **TRACE provides execution evidence and reviewability; independent review remains responsible for establishing statistical correctness.**

TRACE must also preserve these distinctions:

```text
what the programmer intended
what the program did
what TRACE observed
what the programmer asserted
what the reviewer concluded
```

These concepts must not collapse into one another.

## 7. Phase 10 scope and validation

Phase 10 should validate whether TRACE allows a reviewer to answer:

1. What important statistical-programming operations occurred, and in what order?
2. How did important data or result dimensions evolve?
3. Which diagnostics deserve investigation?
4. Which explicit validations passed or failed?
5. Which analysis method was executed for which analysis?
6. Which input and output artifacts belong to the execution?
7. Can the reviewer reconcile the TRACE evidence with the source or Quarto document and the resulting output?
8. Does TRACE expose this evidence without implying that execution evidence proves statistical correctness?

Phase 10 includes realistic statistical-programming examples, observed-diagnostic semantics, minimal provenance, reviewer-oriented log examples, and a second API-friction review.

It does not introduce new operations merely to make examples more descriptive, redesign the event model without evidence, require runtime DataFrames in Core, infer Python variable names, capture subject-level clinical data by default, or expand provenance without a demonstrated requirement.

When completeness and readability conflict, TRACE should optimize for **accurate, proportionate, reviewable evidence**. More logging is not automatically better evidence.

## 8. Relationship to earlier design work

Phase 10 builds on established decisions rather than restating them:

- [`domain-model.md`](domain-model.md) owns the event structure and core domain concepts.
- [`../framework/core-operations-v0.1.md`](../framework/core-operations-v0.1.md) owns operation vocabulary and semantic boundaries.
- [`tier-1-api.md`](tier-1-api.md) owns the public Tier 1 API contract.
- [`object-vs-operation.md`](object-vs-operation.md) owns the Core-versus-integration boundary.
- [`reference-prototype-findings.md`](reference-prototype-findings.md) preserves empirical prototype findings.

If Phase 10 reveals a problem in one of those areas, the authoritative specification should be updated and the Phase 10 evidence recorded here rather than duplicating a competing definition.
