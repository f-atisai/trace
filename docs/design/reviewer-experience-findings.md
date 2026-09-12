# TRACE Reviewer Experience Findings

**Phase:** 10.10 — Second API Friction Review  
**Status:** Design gate  
**Scope:** Findings from realistic statistical examples, reviewer-oriented logs, and Phase 10 reviewer/provenance design

## 1. Purpose

This sprint asks whether the current TRACE API and execution-evidence model remain natural after reviewing realistic statistical-programming workflows from a reviewer perspective.

The key questions are:

> **Could a reviewer reconstruct the analytical journey without reading every line of the source program?**

and:

> **Does anything in the TRACE output accidentally imply statistical correctness when TRACE has only observed execution?**

This document records findings only. It does **not** change the API or implementation.

## 2. Overall conclusion

The current TRACE design is broadly sound. The eleven-operation vocabulary continues to describe realistic workflows naturally, and the reviewer examples show that a reviewer can reconstruct the important analytical path without reading every line of source.

The strongest design pressure is not for new operations. It is for clearer evidence semantics around:

- source versus result identity for operations such as `FILTER`;
- observed versus supplied diagnostics;
- program-level provenance and artifact identity;
- explicit diagnostic units; and
- reconciliation of the stale `trace.read()` design documentation with the implemented API.

No broad API redesign is justified by the current examples.

## 3. Findings summary

| Area | Classification | Finding |
|---|---|---|
| Canonical vocabulary | **KEEP** | The eleven operations remain sufficient for the reviewed TLF, ADaM, survival, listing, and QC workflows. |
| Semantic object names | **KEEP** | Dataset, analysis, variable, and result identities are generally expressive when meaningful names are used. |
| FILTER result identity | **CHANGE** | Population/subset results may need an explicit result identity rather than overloading the source object or `details`. |
| Diagnostics in metrics | **KEEP** | Quantitative execution evidence belongs in metrics, provided units and origin remain explicit. |
| Diagnostic naming | **CHANGE** | Conceptual diagnostics should use explicit units such as `before_rows`, `after_rows`, `matched_subjects`, and `unmatched_keys`. |
| Evidence origin | **CHANGE** | Structured diagnostics need first-class observed/supplied/derived origin semantics. |
| `details` | **KEEP** | `details` remains useful as a structured escape hatch and is not yet overloaded enough to justify expansion. |
| `READ` artifact semantics | **KEEP** | `READ` should identify the semantic input object; physical artifact identity belongs to program-level provenance. |
| `OUTPUT` artifact semantics | **KEEP** | `OUTPUT` should record output production; physical artifact identity and hashes belong to program-level provenance. |
| `ANALYZE` API | **KEEP** | Distinct `source`, `analysis`, `method`, `population`, and `result` identities read naturally in statistical programs. |
| `CHECK` vs `VALIDATE` | **KEEP** | The observe-versus-test distinction remains clear and useful. |
| Provenance model | **KEEP** | Provenance belongs in a separate run-level model, not repeated in events or overloaded into ordinary event context. |
| Artifact hashes | **KEEP** | Optional SHA-256 hashes are useful for artifact identity, not correctness. |
| Step instrumentation | **KEEP** | Coarse steps improve navigation; line-level or heading-level instrumentation would become noise. |
| Automatic step inference | **REJECT** | TRACE should not infer steps from source structure or Quarto headings. |
| Per-event provenance | **REJECT** | Repeating program/run/artifact provenance on every semantic event would create noise without reviewer benefit. |
| Environment fingerprinting | **DEFER** | Git/package/OS/runtime capture remains outside the minimal provenance model until concrete use cases justify it. |
| Automatic file hashing policy | **DEFER** | Hashing mechanics, thresholds, and performance policy require implementation design. |
| Public-dataset examples | **DEFER** | Replace synthetic examples with public datasets before using them as final API evidence. |
| `trace.read()` specification mismatch | **CHANGE** | Governing documentation must be reconciled with the implemented semantic-first `trace.read(name, ...)` API. |

## 4. Vocabulary

### Finding 4.1 — Canonical vocabulary remains sufficient

**Classification: KEEP**

The reviewed workflows map naturally to the existing vocabulary:

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

Examples include:

- demographics: `READ → FILTER → DERIVE → AGGREGATE → VALIDATE → OUTPUT`;
- adverse events: `READ → FILTER → MERGE → AGGREGATE → VALIDATE → OUTPUT`;
- subject listing: `READ → FILTER → SORT → TRANSFORM → OUTPUT`;
- Kaplan-Meier: `READ → FILTER → SORT → ANALYZE → VALIDATE → OUTPUT`;
- ADLB derivation: `READ → SORT → FILTER → MERGE → DERIVE → VALIDATE → OUTPUT`;
- independent QC: `READ → MERGE → VALIDATE → OUTPUT`.

No repeated realistic need emerged for `POPULATION`, `SUMMARY`, `JOIN`, `MODEL`, `REPORT`, or other additional operations.

Population selection remains naturally represented as `FILTER`; the resulting population identity is a result concept, not a new operation.

### Finding 4.2 — Do not add aliases as first-class operations

**Classification: REJECT**

Terms such as `SUBSET`, `WHERE`, `JOIN`, `COMBINE`, `LOAD`, and `EXPORT` may be familiar implementation verbs, but adding them would weaken the controlled vocabulary without adding reviewer value.

The existing semantic normalization remains preferable.

## 5. Semantic object and result identity

### Finding 5.1 — Semantic object names are sufficient when meaningful

**Classification: KEEP**

The examples work best when objects are named for their analytical meaning:

```text
ADSL
ADAE
ADTTE
TEAE_SAFETY
Safety Population
Overall Survival
km_curve
T14_01
```

The reviewer does not need Python variable names such as `df`, `tmp`, or `merged_df`.

TRACE should continue to prefer semantic names over runtime variable introspection.

### Finding 5.2 — FILTER has a source/result identity gap

**Classification: CHANGE**

Population selection exposes a recurring distinction:

```text
source/object: ADSL
condition:     SAFFL == 'Y'
result:        Safety Population
```

The event object should remain `ADSL`, because that identifies what was filtered. However, the reviewer also benefits from knowing that the resulting analytical concept is the `Safety Population`.

The current `FILTER` API has no dedicated `result` parameter. Using the object name `Safety Population` would lose source identity; hiding the result in unrestricted descriptive metadata would weaken consistency.

Recommendation for the governing API reconciliation:

- preserve the event object as the filtered source;
- consider a dedicated optional `result` identity for `FILTER` if public-dataset examples confirm repeated value;
- do not create a `POPULATION` operation.

This is a targeted API refinement, not a vocabulary change.

## 6. Diagnostics and metrics

### Finding 6.1 — Quantitative diagnostics belong in metrics

**Classification: KEEP**

The reviewer examples confirm that metrics are the correct location for measurable execution evidence such as:

```text
row counts
subject counts
merge dimensions
unmatched keys
duplicate subjects
validation comparison values
```

This keeps semantic identity and action separate from quantitative evidence.

### Finding 6.2 — Diagnostic units must be explicit

**Classification: CHANGE**

The realistic examples reinforce that ambiguous counts reduce reviewer confidence.

Prefer:

```text
before_rows
after_rows
result_rows
matched_subjects
unmatched_subjects
unmatched_keys
duplicate_subjects
```

Avoid when the unit is not obvious:

```text
before
after
matched
failed
count
N
```

The current prototype may retain historical field names temporarily, but the governing design should explicitly favor unit-bearing diagnostic names.

### Finding 6.3 — Evidence origin needs a first-class structured representation

**Classification: CHANGE**

This is the most important evidence-quality finding from the reviewer perspective.

Current Tier 1 examples commonly pass values such as:

```python
rows=len(adsl)
```

TRACE records the value, but Core did not independently inspect the DataFrame. A reviewer should not have to assume that `rows=249` was observed by TRACE merely because it appears in a TRACE event.

The structured model therefore needs to preserve whether a diagnostic is:

```text
OBSERVED
SUPPLIED
DERIVED
```

This does not require Tier 1 calls to become verbose. Core can continue accepting simple scalar arguments while internally marking them as supplied. Integrations can later produce observed diagnostics.

The concise text log does not need to annotate every metric with origin, but structured output must retain it.

### Finding 6.4 — Do not force diagnostics for symmetry

**Classification: KEEP**

The examples confirm that operations such as `DERIVE` and `SORT` are often useful without row counts.

TRACE should continue to record diagnostics only when they add reviewer value.

## 7. `details` pressure

### Finding 7.1 — `details` remains a useful escape hatch

**Classification: KEEP**

The examples use `details` for uncommon structured metadata such as:

```text
time variable
censor variable
analysis strata
selected reporting columns
```

This is appropriate because these fields are not yet universal enough to justify permanent Tier 1 parameters.

No reviewed workflow required arbitrary free-form key expansion across the main API.

### Finding 7.2 — Method-specific details should remain secondary

**Classification: KEEP**

For example, Kaplan-Meier may record:

```text
time=AVAL
censor=CNSR
strata=TRT01A
```

These are useful reviewer details but should not force method-specific parameters into `trace.analyze()` until repeated cross-method use justifies them.

## 8. READ and OUTPUT artifact semantics

### Finding 8.1 — READ should remain semantic, not become the provenance container

**Classification: KEEP**

`READ` answers:

> What analytical input object became available to the program?

Program-level provenance answers:

> Which physical artifact participated in this execution?

These are related but distinct.

Example:

```text
READ object:      ADSL
input artifact:   analysis/adsl.parquet
```

The same physical artifact may produce more than one semantic object, and some semantic reads may come from non-file sources in future integrations. Physical artifact identity therefore should not redefine `READ` semantics.

### Finding 8.2 — OUTPUT should remain semantic, not become the artifact registry

**Classification: KEEP**

`OUTPUT` records that a named analytical result was written. Program-level provenance identifies the resulting physical artifact and optional hash.

Example:

```text
OUTPUT object:     T14_01
output artifact:   outputs/T14_01.rtf
sha256:            ...
```

Hashes should not be repeated as ordinary OUTPUT event metrics solely because the artifact was written there.

## 9. ANALYZE

### Finding 9.1 — ANALYZE reads naturally

**Classification: KEEP**

The current form:

```python
trace.analyze(
    "ADTTE",
    "Overall Survival",
    method="Kaplan-Meier",
    population="ITT",
    result="km_curve",
)
```

preserves five useful concepts:

```text
source       ADTTE
analysis     Overall Survival
method       Kaplan-Meier
population   ITT
result       km_curve
```

Collapsing these identities would make the log less precise.

No current example justifies method-specific `ANALYZE` subclasses or separate operations such as `MODEL`, `ESTIMATE`, or `SURVIVAL`.

## 10. CHECK and VALIDATE

### Finding 10.1 — The semantic boundary remains clear

**Classification: KEEP**

The reviewed distinction is still useful:

```text
CHECK      observe something
VALIDATE   test an expectation and record an outcome
```

Examples:

```text
CHECK [ADSL] treatment groups inspected
VALIDATE [T14_01] production and QC statistics match – PASS
```

A `CHECK` should not imply success. A `VALIDATE` must have an explicit result.

### Finding 10.2 — VALIDATE wording can imply more certainty than the evidence supports

**Classification: CHANGE**

A line such as:

```text
INFO [VALIDATE] [ADSL] USUBJID uniqueness – PASS
```

can be read too strongly if the outcome was supplied as `passed=True` rather than derived by TRACE from an observed diagnostic.

The operation itself should remain. The correction belongs in evidence-origin semantics and reviewer documentation, not in renaming `VALIDATE`.

Structured output should preserve how the validation outcome and supporting diagnostics were obtained.

## 11. Provenance

### Finding 11.1 — Provenance belongs in a separate run-level model

**Classification: KEEP**

Program, run ID, timestamps, input artifacts, output artifacts, and optional hashes describe the execution as a whole.

They do not belong:

- repeated on each semantic event;
- overloaded into event `details`; or
- mixed into the ordinary semantic context merely because they are globally available.

The preferred conceptual structure remains:

```text
TraceRun
├── program
├── run_id
├── started_at
├── ended_at
├── input_artifacts
└── output_artifacts
```

Individual events can remain linked to the run through the existing run identity without carrying the full provenance payload.

### Finding 11.2 — Per-event provenance would reduce readability

**Classification: REJECT**

Repeating artifact paths, hashes, timestamps, or environment metadata on ordinary `FILTER`, `DERIVE`, `MERGE`, or `ANALYZE` events would obscure the analytical journey.

Program-level provenance is sufficient for the current review use cases.

### Finding 11.3 — Broad environment fingerprinting remains unnecessary

**Classification: DEFER**

No reviewed example demonstrated an immediate need for automatically recording:

```text
Git commit and dirty state
Python version
package lock state
OS
hostname
username
CPU or memory
container identity
environment variables
```

These may become useful for reproducibility or validation workflows, but they should not expand the minimal provenance model without evidence.

## 12. Hashes

### Finding 12.1 — Optional SHA-256 hashes are useful

**Classification: KEEP**

Hashes provide a precise answer to:

> Is the file being reviewed byte-for-byte the artifact associated with this TRACE execution?

That is meaningful reviewer evidence for inputs and outputs.

Hashes must remain clearly scoped to artifact identity. A matching hash does not imply that the file is statistically correct, complete, or appropriate.

### Finding 12.2 — Automatic hashing policy requires later implementation design

**Classification: DEFER**

The current design should not yet decide:

- which artifacts are automatically hashed;
- file-size thresholds;
- streaming/chunking policy;
- whether remote artifacts can be hashed;
- when hashes are finalized relative to output closure.

The only design decision currently needed is that SHA-256 is the preferred optional algorithm for physical artifact bytes.

## 13. Steps

### Finding 13.1 — Coarse steps improve reviewer navigation

**Classification: KEEP**

Steps are useful when they correspond to major program phases such as:

```text
Read analysis data
Safety Population
Derive analysis variables
Generate statistics
Write output
```

They help a reviewer navigate larger logs without changing the semantic meaning of the enclosed operations.

### Finding 13.2 — Step overuse creates noise

**Classification: KEEP**

Successful steps add two lifecycle lines. They therefore should remain coarse.

A step for every operation, function, cell, or Quarto section would duplicate structure rather than clarify it.

### Finding 13.3 — Automatic step inference should not be introduced

**Classification: REJECT**

TRACE should not automatically turn:

- Python functions;
- source-code blocks;
- notebook cells; or
- Quarto headings

into steps.

The programmer should decide which execution scopes are meaningful enough to expose.

## 14. Reviewer reconstruction test

### Question

> **Could a reviewer reconstruct the analytical journey without reading every line of the source program?**

### Finding

**Classification: KEEP**

For the reviewed examples, yes—at the level TRACE is intended to provide.

A reviewer can identify:

1. which analytical inputs were used;
2. how important populations or records were filtered;
3. where merge cardinality changed;
4. which important variables were derived;
5. which aggregations or analyses were performed;
6. which validations passed or failed;
7. which output was produced; and
8. the order in which those activities occurred.

The reviewer still needs the specification and source to establish whether those operations were the correct ones and whether they were implemented correctly.

This is the desired boundary: TRACE reduces the need to reconstruct execution from every source line without replacing source review.

## 15. Correctness-impression safeguard

### Question

> **Does anything in the TRACE output accidentally imply statistical correctness when TRACE has only observed execution?**

### Finding

**Classification: CHANGE**

The principal risk is not operation vocabulary. It is presentation of supplied diagnostics and validation outcomes without visible evidence origin.

Potentially misleading examples include:

```text
rows=249
PASS
matched_subjects=249
```

when those values were supplied by calling code rather than independently observed by TRACE.

Required design safeguard:

- structured TRACE output must preserve diagnostic origin;
- documentation must distinguish execution evidence from correctness evidence;
- `PASS` must mean only that the implemented validation criterion evaluated successfully;
- concise text output may remain compact but must not be described as independently observed unless it was.

No additional severity level, operation, or correctness badge is justified.

## 16. Documentation/API reconciliation findings

### Finding 16.1 — `trace.read()` documentation is stale

**Classification: CHANGE**

The Tier 1 design document still describes:

```python
trace.read(data, "ADSL")
```

while the implemented Core API and current examples use:

```python
trace.read("ADSL", source=..., rows=..., columns=...)
```

The implemented form is more consistent with the Phase 4 Core boundary: Core receives semantic identifiers and structured evidence rather than runtime DataFrames.

The governing specification should therefore be reconciled to the semantic-first form during Phase 10.11.

Runtime object inspection belongs in optional integrations, for example conceptually:

```python
trace.pandas.read(adsl, "ADSL")
```

rather than in Core `trace.read()`.

### Finding 16.2 — Public-dataset examples should be the next empirical test

**Classification: DEFER**

The current examples are adequate for this design gate but remain synthetic.

Before treating example ergonomics as final evidence, TRACE should revisit them using publicly available datasets and actual file reads. That work may expose additional friction around:

- artifact registration;
- observed diagnostics;
- larger data volumes;
- real merge cardinality;
- realistic output formats; and
- provenance/hashing.

This should not block the current Phase 10.11 specification reconciliation.

## 17. Proposed Phase 10.11 changes

The following findings are accepted candidates for specification reconciliation, not implementation in this sprint:

```text
CHANGE  Reconcile trace.read() documentation with implemented Core API.
CHANGE  Add/clarify diagnostic evidence-origin semantics in the governing model.
CHANGE  Prefer explicit unit-bearing diagnostic names conceptually.
CHANGE  Consider optional FILTER result identity, without adding POPULATION.
CHANGE  Clarify that VALIDATE PASS records only the implemented criterion outcome.
```

The following should remain unchanged:

```text
KEEP    eleven-operation vocabulary
KEEP    semantic object naming
KEEP    metrics/details separation
KEEP    ANALYZE source + analysis model
KEEP    CHECK vs VALIDATE distinction
KEEP    program-level provenance
KEEP    optional SHA-256 artifact hashes
KEEP    coarse step instrumentation
```

The following are explicitly rejected:

```text
REJECT  new POPULATION operation
REJECT  per-event provenance payloads
REJECT  alias operations such as JOIN or EXPORT
REJECT  automatic Quarto/function/cell step inference
```

The following remain deferred:

```text
DEFER   broad environment fingerprinting
DEFER   automatic hashing mechanics and thresholds
DEFER   final example ergonomics until public datasets are used
```

## 18. Design-gate outcome

The second API friction review does **not** justify a broad redesign.

TRACE's current direction remains valid:

```text
semantic operations
      +
structured diagnostics with evidence origin
      +
separate program-level provenance
      +
coarse lifecycle/step structure
      =
reviewable execution evidence
```

The next phase should reconcile the accepted findings into the governing specifications surgically, preserving the existing vocabulary and low-friction programmer experience.
