# Reviewing Statistical Programs with TRACE

TRACE is a review companion for statistical programs and their outputs. This guide explains how to read a TRACE log; no knowledge of the TRACE Python API is required.

A TRACE review asks:

> **Does the recorded execution make sense, and is it consistent with the program and output being reviewed?**

TRACE does not establish statistical correctness. Use it alongside the specification, source code, output, and applicable QC process.

## What TRACE contributes

A statistical-program review usually has three perspectives:

```text
Intent / code  ──────►  Execution  ──────►  Result
                           │
                      TRACE log
```

- **Intent and code** explain what the program should do and how it is implemented.
- **TRACE** records important statistical operations, diagnostics, validations, and run context.
- **Result** is the dataset, table, listing, figure, or other artifact that must ultimately be reviewed.

TRACE helps connect the implementation to the resulting artifact without replacing either.

## Review workflow

Whether the program is a Python script, Quarto document, notebook, or batch job, the review pattern is the same:

1. Read the specification and relevant source to understand the intended analysis.
2. Follow the TRACE log to see the important operations recorded during the run.
3. Investigate unexpected counts, merge behavior, validations, warnings, or execution transitions.
4. Review the resulting output and reconcile it with both the program and TRACE log.
5. When a finalized review log is available, use its program-level provenance to confirm the run and registered input/output artifacts.

TRACE does not remove the need to read source code. It reduces how much execution flow a reviewer must reconstruct from source alone.

## Reading a finalized TRACE log

A managed run with `log_file` can produce two reviewer-facing layers:

```text
TRACE EXECUTION

Program:  TLF_POPULATION
Run ID:   7eab...
Executed: 2026-09-30T09:15:22Z

Input artifacts:
  data/adsl.xpt

Output artifacts:
  example-output/tlf_population.rtf

INFO [START]     [TLF_POPULATION] execution started
INFO [READ]      [ADSL] loaded – N=254, Vars=48
INFO [FILTER]    [ADSL] SAFFL == 'Y' applied – N=254 → 249
INFO [AGGREGATE] [ADSL] summarized – N=12
INFO [VALIDATE]  [population_table] expected rows present – PASS
INFO [OUTPUT]    [TLF_POPULATION] written – example-output/tlf_population.rtf
INFO [END]       [TLF_POPULATION] execution completed – 0.84s
```

The **provenance block** identifies the program, run ID, execution timestamp, and registered physical artifacts. The **event stream** records the statistical operations and diagnostics reported by the program.

During execution, TRACE events are visible immediately on the console. The finalized file places the run-level provenance before the complete event stream.

## What to look for

Use these questions as a review lens rather than a mandatory checklist for every program.

| Area | Reviewer question | TRACE information to inspect |
|---|---|---|
| **Inputs** | Were the expected analysis inputs recorded? | `READ` events and input artifacts. |
| **Populations** | Did analysis populations and subsets evolve plausibly? | `FILTER` conditions and before/after counts. |
| **Merges** | Did the combination of datasets behave as expected? | `MERGE` keys, method, and row diagnostics where recorded. |
| **Derivations** | Were important analytical concepts created? | `DERIVE` events. |
| **Summaries** | Were grouped summaries produced as expected? | `AGGREGATE` events and grouping information. |
| **Analyses** | Was the intended statistical method recorded? | `ANALYZE` source, method, population, and result. |
| **Validations** | Did explicit implemented checks pass? | `VALIDATE` outcomes and diagnostics. |
| **Outputs** | Were the expected artifacts produced? | `OUTPUT` events and output artifacts. |
| **Order** | Does the execution sequence make analytical sense? | Event order and `STEP` scopes. |
| **Run identity** | Does this log correspond to the run and artifacts under review? | Program, run ID, execution timestamp, and artifact paths. |

### Inputs

Look for the datasets expected by the analysis:

```text
INFO [READ] [ADSL] loaded – N=254, Vars=48
```

A missing `READ` event matters only when the program is expected to instrument that input. TRACE does not infer operations that were never recorded.

The semantic object and physical artifact are related but distinct:

```text
READ object:      ADSL
Input artifact:   data/adsl.xpt
```

### Populations and filters

Population selection should normally remain visible as a `FILTER`:

```text
INFO [FILTER] [ADSL] SAFFL == 'Y' applied – N=254 → 249
```

Check whether the condition matches the intended population and whether the count change is plausible. The specification and source code remain authoritative for deciding whether the population definition is correct.

### Merges

Where row diagnostics are recorded, look for unexpected expansion or contraction:

```text
INFO [MERGE] [ADAE + Safety Population] merged – left_rows=1191, right_rows=254, result_rows=1184
```

TRACE records the merge and supplied diagnostics. It does not decide whether a cardinality change is wrong unless the program explicitly records a validation for that expectation.

### Derivations and transformations

Use `DERIVE` to identify important analytical variables, flags, categories, or endpoints. Use `TRANSFORM` for material structural or representation changes such as pivots or reporting preparation.

TRACE is intentionally not a line-by-line execution trace. Intermediate implementation details do not need an event unless they improve reviewability.

### Aggregations and analyses

`AGGREGATE` covers grouped reductions such as counts, percentages, means, and descriptive statistics. `ANALYZE` records a statistical method, model, estimator, or analysis algorithm.

For example:

```text
INFO [ANALYZE] [Overall Survival] analyzed – source=ADTTE, method=Kaplan-Meier, population=ITT
```

Reconcile the analysis identity, source, population, and method with the specification and program. Statistical interpretation remains outside TRACE.

### Validations

Treat a failed validation as an explicit review signal:

```text
WARNING [VALIDATE] [ADSL] USUBJID uniqueness – FAIL
```

A passing validation means only that the implemented criterion evaluated successfully. It does not establish broader program or statistical correctness.

### Outputs and provenance

An `OUTPUT` event records that the program reported production of an artifact:

```text
INFO [OUTPUT] [TLF_POPULATION] written – example-output/tlf_population.rtf
```

In a finalized managed run, the path can also appear once in program-level provenance. TRACE's current Developer Preview provenance records artifact paths; artifact hashing and environment fingerprinting are not part of the public alpha behavior.

## Review the repository examples

The executable examples provide a useful progression:

| Program | Reviewer focus |
|---|---|
| [`basic_analysis_workflow.py`](../../examples/basic_analysis_workflow.py) | Basic `READ → FILTER → DERIVE → OUTPUT` flow and finalized provenance. |
| [`population_summary.py`](../../examples/population_summary.py) | Analysis-population selection, treatment summaries, validation, steps, and RTF output. |
| [`specific_adverse_events.py`](../../examples/specific_adverse_events.py) | Multiple inputs, Safety Population selection, ADSL/ADAE merge behavior, participant incidence, validation, and output. |

The two TLF examples use original public CDISC Pilot Study XPORT datasets. See [TRACE Statistical Programming Examples](../../examples/README.md) for data sources, workflow references, and run instructions.

A reviewer can read the example logs as compact maps of their workflows:

```text
Population summary
READ ADSL
  → FILTER analysis populations
  → AGGREGATE treatment summaries
  → TRANSFORM reporting layout
  → VALIDATE
  → OUTPUT RTF

Specific adverse events
READ ADSL + ADAE
  → FILTER Safety Population
  → AGGREGATE population counts
  → MERGE ADAE with Safety Population
  → AGGREGATE participant incidence
  → VALIDATE
  → OUTPUT RTF
```

## What not to conclude from TRACE

A clean TRACE log does not mean:

- the specification was correct;
- the correct source data were supplied upstream;
- a derivation or statistical method was implemented correctly;
- every expected operation was instrumented;
- the output is statistically or clinically correct; or
- independent QC is unnecessary.

TRACE records what the program reports through its TRACE calls. The reviewer remains responsible for interpreting that information against the specification, source code, output, and QC process.

## Compact review pattern

```text
1. INTENT       What should this program do?
2. RUN          Which TRACE run and artifacts am I reviewing?
3. INPUTS       What entered the analysis?
4. FLOW         How did populations and data evolve?
5. ANALYSIS     What summaries or methods were executed?
6. VALIDATION   What explicit expectations passed or failed?
7. OUTPUT       What was produced?
8. RECONCILE    Does the recorded execution make sense against code and result?
```

The goal is to make statistical execution easier to understand and interrogate, not to replace statistical review.

## Related documentation

- [TRACE operations](../guides/operations.md) explains when to use each statistical operation.
- [TRACE Core Operations v0.1](core-operations-v0.1.md) defines the canonical vocabulary and boundaries.
- [Program-level provenance](../concepts/provenance.md) explains the public provenance model.
- [TRACE API](../api/README.md) documents the supported Python interface.
