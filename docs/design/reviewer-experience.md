# TRACE Reviewer Experience

**Phase:** 10 — Define the TRACE Reviewer Experience  
**Sprint:** 10.0 — Freeze the Phase 10 Design Charter  
**Status:** Active design charter  
**Scope:** Reviewer experience, terminology, boundaries, and Phase 10 validation goals  
**Repository location:** `docs/design/reviewer-experience.md`

## 1. Purpose

This document defines the design charter for Phase 10 of TRACE.

Phases 0–8 established the TRACE domain model, canonical statistical-programming vocabulary, public API direction, configuration, lifecycle, and step instrumentation. The reference prototype then tested those decisions against six statistical-programming workflows and reconciled the resulting API friction.

Phase 10 changes the primary design viewpoint.

Earlier phases asked:

> Does TRACE feel natural, concise, and semantically useful to a statistical programmer?

Phase 10 additionally asks:

> **Does the recorded analytical execution make sense, and is it consistent with the program and output being reviewed?**

The purpose of Phase 10 is to define how TRACE serves as a **review companion** to a statistical program and its outputs.

This phase does not assume that the existing API must change. It establishes the reviewer experience first, then uses realistic statistical-programming examples to determine whether the existing TRACE design provides the right execution evidence.

---

## 2. TRACE's Role in Statistical Review

TRACE records evidence about the execution of a statistical program.

The reviewer model is:

```text
Program intent
     │
     ▼
Source / Quarto
     │
     ▼
Actual execution
     │
     ▼
TRACE
     │
     ▼
Statistical output
```

These artifacts answer complementary questions.

| Artifact | Primary review question |
|---|---|
| Specification, source, or Quarto | What was intended, why was it done, and how was it coded? |
| TRACE | What actually happened during this execution? |
| Statistical output | What resulted, and is the result correct? |

TRACE occupies the execution layer between implementation and result.

It should allow a reviewer to reconstruct the important analytical path without requiring the reviewer to infer the entire runtime sequence from source code alone.

---

## 3. Reviewable Execution Evidence

For Phase 10, TRACE's reviewer-facing role is described by three complementary forms of evidence:

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

Semantic events answer:

> What happened?

Examples include:

```text
READ
FILTER
DERIVE
MERGE
AGGREGATE
ANALYZE
CHECK
VALIDATE
OUTPUT
```

A semantic event describes statistical-programming activity rather than a generic runtime message.

For example:

```text
FILTER Safety Population
```

is more useful to analytical review than a generic message saying that a function completed.

Phase 10 does not introduce a new operation vocabulary. The existing canonical vocabulary remains the starting point and will be pressure-tested against realistic statistical-programming examples.

### 3.2 Observed diagnostics

Observed diagnostics answer:

> What evidence describes what happened to the data or result?

Examples include:

```text
rows=254
rows=254 → 249
left_rows=249
right_rows=731
result_rows=814
duplicates=17
result_rows=3
```

Diagnostics make semantic events reviewable.

A reviewer should be able to distinguish the fact that a FILTER occurred from the evidence that the filter changed 254 records or subjects to 249.

Phase 10 will further define what it means for a diagnostic to be observed by TRACE rather than merely asserted by the programmer. That distinction is important to the evidentiary value of a TRACE log.

### 3.3 Execution provenance

Execution provenance answers:

> What execution and artifacts does this evidence belong to?

Phase 10 intentionally begins with a narrow provenance scope:

```text
execution timestamp
input artifacts
output artifacts
artifact hashes, where useful and safe
```

Existing execution identity such as `program` and `run_id` remains relevant.

Phase 10 does **not** initially require broader environment fingerprinting such as Git state, Python version, package inventories, operating-system details, hostname, or user identity.

Provenance should be expanded only when a concrete review or reproducibility requirement justifies the additional information.

---

## 4. Reviewer Persona

The primary reviewer for Phase 10 is a statistical programmer or other qualified reviewer validating a statistical program and its output.

The reviewer may be working with:

- a conventional Python TLF program;
- a literate Quarto analysis containing narrative and code;
- an ADaM derivation program;
- a table, listing, or figure program;
- an independent QC program; or
- another statistical-programming workflow represented by the TRACE vocabulary.

The reviewer understands the study, analysis requirements, and statistical-programming context. TRACE is not intended to replace that expertise.

The reviewer uses TRACE to understand the **observed execution path**, reconcile important diagnostics, identify places that deserve investigation, and connect the execution to its input and output artifacts.

---

## 5. Core Reviewer Questions

TRACE should help a reviewer answer questions such as:

### Inputs

- Were the expected input artifacts read?
- Are the observed dimensions plausible?
- Can the input artifact be identified unambiguously when provenance is available?

### Population changes

- Did population or row counts change as expected?
- Did a filter remove substantially more or fewer observations than expected?

### Merges

- Are left, right, and result row counts reasonable?
- Did a merge unexpectedly expand or contract the data?
- Are additional diagnostics available when merge cardinality deserves investigation?

### Derivations and transformations

- Were important analytical concepts derived?
- Did the recorded operation sequence correspond to the intended analytical workflow?

### Analyses

- Was the expected statistical method executed for the intended analysis and population?
- Is the analysis positioned at the expected point in the execution sequence?

### Checks and validations

- What diagnostics were observed?
- Which explicit expectations passed or failed?
- Did execution continue after a potentially important failed validation or warning?

### Outputs

- Were the expected statistical outputs produced?
- Can the produced artifact be connected to this execution?

### Execution order

- Did the major operations occur in a sensible analytical sequence?
- Did the observed execution follow the expected path?

### Provenance

- Which input and output artifacts belong to this run?
- When did the execution occur?
- Where hashes are recorded, do the artifacts being reviewed correspond to the artifacts associated with the execution?

The reviewer is not expected to give every TRACE event equal attention. TRACE should make the analytical journey easy to reconstruct and make unusual evidence easier to identify for deeper inspection in the source program, specification, data, or output.

---

## 6. With Quarto

When a statistical analysis is implemented in Quarto, the reviewer has three complementary artifacts:

```text
analysis.qmd  ──────►  TRACE log  ──────►  TLF
     │                    │                 │
     │                    │                 │
 What was intended?   What happened?    What resulted?
 How was it coded?    With what data?    Is it correct?
 Why was it done?     In what order?
```

Quarto provides narrative, rationale, methods, and implementation context.

TRACE provides evidence of the actual execution path.

The output provides the analytical result to be reviewed.

TRACE must not duplicate the role of the Quarto document. In particular, TRACE should not become a second narrative specification or require programmers to restate analysis rationale in log calls.

---

## 7. Without Quarto

For a conventional Python statistical program, the source program provides the implementation context:

```text
tlf_population.py  ──────► TRACE log ──────► tlf_population.rtf
       │                        │                       │
     Code                  Execution                 Result
```

The reviewer reads the source to understand implementation and uses TRACE as a concise execution map.

A useful TRACE view might expose a path such as:

```text
READ ADSL
   ↓
FILTER ITT population       254 → 250
   ↓
FILTER efficacy population  254 → 243
   ↓
FILTER safety population    254 → 249
   ↓
ANALYZE population counts
   ↓
OUTPUT population.rtf
```

The log helps the reviewer decide where closer source-code or output inspection is warranted. It does not eliminate that inspection.

---

## 8. TRACE and Statistical Correctness

TRACE records execution evidence. It does not establish statistical correctness.

A program can execute exactly as coded and still implement the wrong analysis.

Therefore a clean TRACE log does **not** prove that:

- the statistical method is appropriate;
- the analysis specification is correct;
- the program correctly implements the specification;
- a derivation has the correct clinical or statistical meaning;
- the source data are correct;
- the TLF is correct;
- the interpretation of the result is correct; or
- independent QC is unnecessary.

TRACE does not replace:

```text
specification review
code review
independent programming / QC
source-data review
analysis-dataset validation
TLF review
statistical review
clinical interpretation
```

TRACE complements these activities by making actual execution easier to inspect and reconcile.

The governing principle is:

> **TRACE provides execution evidence and reviewability; independent review remains responsible for establishing statistical correctness.**

---

## 9. Relationship to Traditional Log Review

Traditional log review often asks:

> Did the program execute without suspicious runtime messages?

Errors, warnings, and unusual runtime messages remain important, but Phase 10 broadens the reviewer-facing question:

> **Does the recorded analytical execution make sense, and is it consistent with the program and output being reviewed?**

For example:

```text
INFO [READ]   [ADSL] rows=254
INFO [FILTER] [Safety Population] rows=254 → 249
INFO [MERGE]  [Safety AEs] left_rows=249 right_rows=731 result_rows=814
WARN [VALIDATE] [USUBJID uniqueness] FAIL duplicates=17
INFO [OUTPUT] [AE Summary] t14-2-01.rtf
```

The important evidence is not merely that five events were recorded.

The reviewer can see that the safety population contained 249 subjects or records, a later merge expanded the data, a uniqueness expectation failed with 17 duplicates, execution continued, and an AE output was still produced.

TRACE should help the reviewer locate that story quickly.

---

## 10. Phase 10 Scope

Phase 10 will define and validate the reviewer-facing model for TRACE.

The phase includes:

1. TRACE positioning as reviewable execution evidence;
2. the relationship between semantic events, diagnostics, and provenance;
3. reviewer-facing interpretation of the canonical vocabulary;
4. realistic statistical-programming examples;
5. observed-diagnostic semantics;
6. minimal execution provenance;
7. conventional Python and Quarto review workflows;
8. reviewer-oriented TRACE log examples;
9. a second API friction review after realistic examples; and
10. reconciliation of accepted findings into the governing TRACE specification.

Phase 10 may reveal API changes, but it does not begin by assuming that changes are required.

---

## 11. Phase 10 Non-Goals

Phase 10 does not attempt to:

- replace independent QC;
- prove statistical correctness;
- infer programmer intent from code;
- infer clinical meaning that the program has not expressed;
- turn TRACE into a workflow orchestrator;
- turn TRACE into a statistical validation engine;
- create a Quarto plugin or extension;
- require Quarto for TRACE usage;
- add operations merely to make examples more descriptive;
- redesign the Phase 0 event model without evidence;
- pass runtime DataFrames into TRACE Core;
- introduce Python variable-name introspection;
- capture subject-level clinical data by default;
- capture broad environment fingerprints without a demonstrated requirement;
- add Git provenance in the initial provenance design;
- add package inventories, operating-system information, hostname, or user identity in the initial provenance design; or
- promote prototype internals into production architecture merely because they already exist.

Existing boundaries remain in force unless Phase 10 produces evidence sufficient to reopen them.

---

## 12. Vocabulary Guardrail

The current canonical statistical-operation vocabulary remains the Phase 10 starting point:

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

Lifecycle/system categories remain separate:

```text
START
END
STEP
```

Phase 10 should pressure-test this vocabulary against realistic statistical-programming workflows rather than inventing new operations in advance.

The reconciled semantic boundaries remain:

```text
CHECK      observe
VALIDATE   test an expectation

DERIVE     create a named analytical concept
TRANSFORM  change representation or structure

AGGREGATE  group, reduce, or summarize
ANALYZE    apply a statistical method or model
```

If a realistic example does not fit naturally, record that as design evidence. Do not immediately solve the problem by adding another operation.

---

## 13. Evidence Guardrail

TRACE should record observed execution rather than imply more assurance than it possesses.

The design must preserve distinctions between:

```text
what the programmer intended
what the program did
what TRACE observed
what the programmer asserted
what the reviewer concluded
```

These concepts must not collapse into one another.

In particular:

- semantic instrumentation expresses the meaning of an operation;
- diagnostics provide evidence about the observed execution;
- validations express explicit expectations and outcomes;
- provenance connects evidence to an execution and its artifacts; and
- reviewer conclusions remain outside TRACE.

This guardrail is central to Phase 10.

---

## 14. Provenance Guardrail

Initial Phase 10 provenance is intentionally minimal.

In scope:

```text
execution timestamp
input artifacts
output artifacts
optional artifact hashes
```

Existing `program` and `run_id` continue to identify execution context.

Hashes may be used where they provide useful artifact identity without creating unreasonable cost or operational problems. Hash policy, calculation timing, supported artifacts, and default behavior must be designed before hashing becomes required behavior.

Out of scope for the initial provenance model:

```text
Git commit
Git status
Python version
package versions
operating system
hostname
username
machine identity
broad environment snapshots
```

The provenance model should remain extensible so these can be considered later if review requirements justify them.

---

## 15. Phase 10 Decision Rule

When implementation convenience, log completeness, and reviewer usefulness conflict, Phase 10 should optimize for **accurate, proportionate, reviewable evidence**.

More logging is not automatically better evidence.

Before adding information, ask:

> Does this materially help a reviewer understand, investigate, or identify this execution?

Before omitting information, ask:

> Would its absence make an important analytical change or artifact relationship difficult to review?

TRACE should remain concise enough that important events and diagnostics are visible rather than buried in instrumentation noise.

---

## 16. Relationship to the Reference Prototype

The reference prototype remains evidence for Phase 10, not production architecture.

Its findings established that:

- the eleven-operation vocabulary covered the six prototype workflows;
- semantic identifiers were sufficient without runtime DataFrames in Core;
- CHECK and VALIDATE remained distinguishable;
- DERIVE and TRANSFORM required stronger guidance but not replacement;
- AGGREGATE and ANALYZE remained distinct;
- merge row counts were useful reviewer evidence;
- coarse steps were useful while granular steps created noise; and
- realistic statistical scalar values required normalization.

Phase 10 builds on these findings by testing TRACE from the reviewer's perspective rather than reopening them without evidence.

---

## 17. Phase 10 Validation Questions

Phase 10 should ultimately determine whether TRACE allows a reviewer to answer:

1. What important statistical-programming operations actually occurred?
2. In what analytical order did they occur?
3. How did important data or result dimensions evolve?
4. Which diagnostics deserve investigation?
5. Which explicit checks or validations passed or failed?
6. Which analysis method was executed for which analysis?
7. Which statistical outputs were actually produced?
8. Which input and output artifacts belong to the execution?
9. Can the reviewer reconcile the TRACE evidence with the program or Quarto document and the resulting output?
10. Does TRACE expose this evidence without implying that execution evidence proves statistical correctness?

---

## 18. Sprint 10.0 Output

Sprint 10.0 produces this design charter only:

```text
docs/design/reviewer-experience.md
```

No TRACE API, event model, renderer, provenance implementation, example program, or test should be changed during this sprint.

Later Phase 10 sprints may propose changes, but those changes must be justified by the reviewer model and realistic statistical-programming evidence.

---

## 19. Sprint 10.0 Acceptance Criteria

Sprint 10.0 is complete when:

1. the Phase 10 reviewer persona is defined;
2. TRACE's role as a review companion is explicit;
3. the relationship between source/Quarto, TRACE, and statistical output is documented;
4. semantic events, observed diagnostics, and execution provenance are established as the three components of reviewable execution evidence;
5. the central reviewer question is documented;
6. TRACE is explicitly distinguished from statistical correctness and independent QC;
7. the canonical vocabulary is preserved as the starting point;
8. the distinction between observed evidence, assertions, intent, and reviewer conclusions is protected;
9. initial provenance is constrained to execution timestamp, input artifacts, output artifacts, and optional hashes;
10. Phase 10 scope and non-goals are explicit; and
11. no API or implementation changes have been made.

---

## 20. Phase 10 Charter

Phase 10 proceeds under the following charter:

> **TRACE is a review companion to the statistical program and its outputs. It records semantic events, observed diagnostics, and execution provenance so that a reviewer can understand what actually happened during an execution and reconcile that evidence with the intended analysis and resulting output. TRACE does not establish statistical correctness and does not replace specification review, code review, output review, or independent QC.**
