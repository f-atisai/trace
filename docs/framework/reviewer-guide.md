# Reviewing Statistical Programs with TRACE

TRACE is a review companion for statistical programs and their outputs. This guide explains how to read a TRACE log; no knowledge of the TRACE Python API is required.

A TRACE review asks:

> **Does the recorded analytical execution make sense, and is it consistent with the program and output being reviewed?**

TRACE does not establish statistical correctness. Use it alongside the program, specification, output, and applicable QC process.

## What TRACE contributes

A review normally has three perspectives:

```text
Intent / code  ──────►  Execution  ──────►  Result
                           │
                         TRACE
```

- **Intent and code** explain what the program was supposed to do and how it was implemented.
- **TRACE** records the important analytical activity and execution evidence from the run.
- **Result** is the dataset, table, listing, figure, or other artifact that must ultimately be reviewed.

TRACE is most useful as the bridge between the first and third perspectives.

## Workflow with Quarto

```text
analysis.qmd  ──────►  TRACE  ──────►  TLF
     │                   │              │
Intent + code         Execution        Result
```

Review the artifacts together:

| Artifact | What the reviewer obtains |
|---|---|
| `analysis.qmd` | Analytical intent, narrative, methods, source code, and surrounding rationale. |
| TRACE log | The important operations that actually executed, associated diagnostics, validations, and run/artifact provenance. |
| TLF | The resulting statistical presentation to reconcile with the intended analysis and recorded execution. |

Quarto remains the narrative and implementation document. TRACE should not duplicate its rationale or methods prose.

A practical review sequence is:

1. Read the relevant Quarto section to understand the intended analysis.
2. Follow the TRACE log to confirm that the expected analytical path was executed.
3. Investigate important diagnostics, validations, warnings, or unexpected transitions.
4. Review the TLF and reconcile it with both the intended analysis and the recorded execution.
5. Use provenance to confirm that the reviewed artifacts belong to the recorded run when that identity matters.

## Workflow without Quarto

```text
tlf.py  ───────────►  TRACE  ──────►  TLF
  │                    │              │
 Code                Execution        Result
```

The workflow is the same except that the Python source and associated specification provide the implementation context:

1. Review the specification and relevant source sections to understand the intended analysis.
2. Follow TRACE as a concise map of the important operations that executed.
3. Investigate important diagnostics, validations, warnings, or unexpected transitions.
4. Review the resulting TLF and reconcile it with the program and TRACE evidence.
5. Use provenance to confirm execution/artifact identity where needed.

TRACE does not remove the need to read source code. It reduces the amount of execution behavior a reviewer must reconstruct from source alone.

## Reading a TRACE log

A TRACE log has two reviewer-facing layers:

```text
TRACE EXECUTION
Program:  tlf_population.py
Run ID:   7eab...
Started:  2026-09-12T14:32:18Z
Ended:    2026-09-12T14:32:19Z
Inputs:   data/adsl.parquet
Outputs:  rtf/tlf_population.rtf

INFO [START]     [tlf_population.py] execution started
INFO [READ]      [ADSL] loaded – rows=254
INFO [FILTER]    [ADSL] SAFFL == 'Y' applied – rows=254 → 249
INFO [AGGREGATE] [ADSL] participant counts created – by=TRT01A
INFO [VALIDATE]  [Treatment groups] expected groups present – PASS
INFO [OUTPUT]    [T14_01] written – rtf/tlf_population.rtf
INFO [END]       [tlf_population.py] execution completed – 0.84s
```

The **execution block** identifies the program run and its physical input/output artifacts. The **event stream** records what happened analytically and the diagnostics associated with those operations.

Read the event stream in order. TRACE is intended to expose the analytical journey rather than merely provide a collection of isolated messages.

## Review questions

Use the following questions as a review lens rather than a mandatory checklist for every program.

| Area | Reviewer question | TRACE evidence to inspect |
|---|---|---|
| **Inputs** | Were the expected analysis datasets or other inputs used? | `READ` events and input-artifact provenance. |
| **Populations** | Did analysis populations and subsets evolve plausibly? | `FILTER` conditions and before/after diagnostics. |
| **Merges** | Did cardinality behave as expected? | `MERGE` keys/method plus left, right, and result dimensions where recorded. |
| **Derivations** | Were important analytical concepts derived? | `DERIVE` events for analysis variables, flags, categories, or endpoint values. |
| **Analyses** | Was the intended statistical analysis executed? | `ANALYZE` identity, source, method, and population where recorded. |
| **Validations** | Did explicit expectations pass? | `VALIDATE` outcomes and supporting diagnostics. |
| **Outputs** | Were the expected artifacts generated? | `OUTPUT` events and output-artifact provenance. |
| **Order** | Does the execution sequence make analytical sense? | Event order and coarse `STEP` scopes where present. |
| **Provenance** | Does the reviewed output correspond to this execution? | Program, run ID, timestamps, artifact paths, and optional hashes. |

### Inputs

Look for the datasets expected by the analysis. A missing `READ` event is worth investigating only when the program is expected to instrument that input; TRACE does not infer uninstrumented operations.

Where artifact provenance is available, distinguish the semantic dataset identity from the physical file:

```text
READ [ADSL]
Input artifact: data/adsl.parquet
```

### Populations and filters

Review important population and subset transitions, for example:

```text
FILTER [ADSL] SAFFL == 'Y' applied – rows=754 → 720
```

Ask whether the condition is appropriate for the intended population and whether the change in size is plausible. TRACE records the execution evidence; correctness of the population definition still requires the specification and code.

### Merges

Look for unexpected expansion or contraction:

```text
MERGE [ADAE + ADSL] merged – left_rows=4127, right_rows=754, result_rows=4127
```

Cardinality diagnostics are particularly useful when the expected relationship should preserve rows or keys. TRACE does not infer that a cardinality change is erroneous unless an explicit `VALIDATE` event tests that expectation.

### Derivations and transformations

Use `DERIVE` to identify important analytical concepts created during execution. Use `TRANSFORM` to understand material representation or structural changes such as pivots or reporting preparation.

The absence of a TRACE event for every intermediate variable is intentional. Review should focus on analytically meaningful operations rather than line-by-line execution.

### Analyses

An analysis event should make the analytical identity and method understandable:

```text
ANALYZE [Overall survival] Kaplan-Meier fitted – source=ADTTE, population=ITT
```

Reconcile the analysis identity, source, population, and method with the specification or program. Statistical results themselves remain primarily the responsibility of the resulting output and statistical review.

### Validations

Treat a failed validation as an explicit review signal:

```text
WARNING [VALIDATE] [USUBJID uniqueness] FAIL – duplicate_subjects=2
```

A passed validation means only that the recorded criterion passed as implemented. It does not establish overall program correctness.

Diagnostic values may be **observed**, **supplied**, or **derived**. Reviewer tooling or structured TRACE output may expose that origin even when the concise text rendering does not label it inline.

### Outputs and provenance

An `OUTPUT` event says that output production occurred. Program-level provenance identifies the physical artifact associated with the run.

When a SHA-256 hash is recorded, it can be used to determine whether the artifact under review is byte-for-byte the same artifact recorded for the execution. A matching hash establishes artifact identity, not statistical correctness.

## What not to conclude from TRACE

A clean TRACE log does not mean:

- the specification was correct;
- the correct source data were supplied upstream;
- a derivation or statistical method was implemented correctly;
- every expected operation was instrumented;
- the TLF is statistically or clinically correct; or
- independent QC is unnecessary.

TRACE answers **what execution evidence was recorded for this run**. The reviewer remains responsible for interpreting that evidence with the program, specification, and output.

## A compact review pattern

For most programs, the reviewer can use this sequence:

```text
1. INTENT       What should this program do?
2. PROVENANCE   Which run and artifacts am I reviewing?
3. INPUTS       What entered the analysis?
4. FLOW         How did populations/data evolve?
5. ANALYSIS     What analytical method was executed?
6. VALIDATION   What explicit expectations passed or failed?
7. OUTPUT       What was produced?
8. RECONCILE    Does the execution make sense against code and result?
```

The goal is not to make the reviewer approve TRACE. The goal is to make the statistical execution easier to understand and interrogate.

## Related specifications

- [`core-operations-v0.1.md`](core-operations-v0.1.md) defines TRACE operation vocabulary.
- [`../design/reviewer-experience.md`](../design/reviewer-experience.md) defines the reviewer model and diagnostic-evidence semantics.
- [`../design/provenance.md`](../design/provenance.md) defines program-level execution provenance.
