# Getting Started with TRACE

This guide shows the normal TRACE workflow for a Python statistical program: perform the analysis with your existing tools, then record concise execution evidence at meaningful analytical boundaries.

For exact method signatures, use the [TRACE API](../api/README.md) reference.

## 1. Install the Developer Preview

TRACE currently targets Python 3.10+ and is being developed directly from the repository:

```bash
git clone https://github.com/f-atisai/trace.git
cd trace
python -m pip install -e .
```

The supported import is:

```python
from trace_tlf import Trace
```

## 2. Create a managed TRACE run

Use the context-manager form when the statistical program has a clear execution boundary:

```python
from trace_tlf import Trace

with Trace("T14_01", log_file="logs/T14_01.log") as trace:
    ...
```

TRACE emits START when the run begins and END when it finishes. Console events stream while the program executes. With `log_file` configured, the completed managed run is also published as a provenance-first review log.

Use a new `Trace` instance for each execution.

## 3. Record input acquisition

Your normal library reads the data. TRACE records the semantic evidence afterward:

```python
adsl = pd.read_sas("data/adsl.xpt", format="xport", encoding="utf-8")

trace.read(
    "ADSL",
    source="data/adsl.xpt",
    rows=len(adsl),
    columns=len(adsl.columns),
)
```

The `source` identifies the physical input artifact. In a managed run with `log_file`, it also contributes to the program-level provenance summary.

TRACE Core does not own or retain the DataFrame.

## 4. Instrument meaningful analytical stages

Use `trace.step()` for coarse stages that help a reviewer follow the program:

```python
with trace.step("Analysis population"):
    safety = adsl.loc[adsl["SAFFL"] == "Y"].copy()

    trace.filter(
        "ADSL",
        "SAFFL == 'Y'",
        result="Safety Population",
        before=len(adsl),
        after=len(safety),
    )
```

The statistical code still performs the filtering. TRACE records what happened and the supplied diagnostics.

Do not create a step for every individual statement. A step should represent a reviewer-meaningful stage such as population selection, derivations, analysis, or output preparation.

## 5. Record the operations that matter

TRACE provides eleven semantic helpers:

```text
READ  CHECK  FILTER  SORT  DERIVE  TRANSFORM
MERGE  AGGREGATE  ANALYZE  VALIDATE  OUTPUT
```

For example, after combining AE records with the Safety Population:

```python
adae_safety = adae.merge(safety[["USUBJID"]], on="USUBJID", how="inner")

trace.merge(
    "ADAE",
    "Safety Population",
    on="USUBJID",
    how="inner",
    result="Safety ADAE",
    left_rows=len(adae),
    right_rows=len(safety),
    result_rows=len(adae_safety),
)
```

After producing a summary:

```python
trace.aggregate(
    "Safety ADAE",
    by=["AESOC", "AEDECOD", "TRT01A"],
    result="AE incidence",
    method="unique participant count",
    rows=len(ae_summary),
)
```

The goal is not to log every line. Record the operations that explain the analytical execution path.

## 6. Record explicit validation separately

Use `VALIDATE` only when the program has implemented an expectation that can pass or fail:

```python
trace.validate(
    "Safety Population",
    "participant count equals treatment totals",
    passed=safety_total == treatment_total,
    metrics={"participants": safety_total},
)
```

`passed=True` means that criterion passed. It does not prove that the broader analysis, specification, or output is statistically correct.

Use `CHECK` instead when you are recording an observation without a pass/fail expectation.

## 7. Record the output artifact

Write the artifact with the reporting library, then record it:

```python
write_rtf(table, "outputs/T14_01.rtf")

trace.output(
    "T14_01",
    "outputs/T14_01.rtf",
    format="RTF",
)
```

In a managed run with `log_file`, the path is also registered as an output artifact in program-level provenance.

## 8. Read the live execution evidence

A run might stream:

```text
INFO [START]     [T14_01] execution started
INFO [READ]      [ADSL] loaded – N=254, Vars=48
INFO [STEP]      [Analysis population] started
INFO [FILTER]    [ADSL] SAFFL == 'Y' applied – N=254 → 249
INFO [STEP]      [Analysis population] completed – 0.031s
INFO [AGGREGATE] [Safety ADAE] summarized
INFO [VALIDATE]  [Safety Population] participant count equals treatment totals – PASS
INFO [OUTPUT]    [T14_01] written – outputs/T14_01.rtf
INFO [END]       [T14_01] execution completed – 0.84s
```

The console answers **what is happening now**.

## 9. Review the finalized log

When `log_file` is configured on a managed run, the persistent review artifact begins with program-level provenance:

```text
TRACE EXECUTION

Program:  T14_01
Run ID:   7eab...
Executed: 2026-09-14T14:32:18Z

Input artifacts:
  data/adsl.xpt

Output artifacts:
  outputs/T14_01.rtf

INFO [START] [T14_01] execution started
...
INFO [END] [T14_01] execution completed – 0.84s
```

The finalized log answers **what happened in this run** and connects the semantic execution path to its physical input and output artifacts.

TRACE does not automatically hash artifacts or capture the execution environment in the Developer Preview.

## 10. Review TRACE with the program and output

A reviewer should use TRACE alongside the statistical program, specification, and output:

```text
program / Quarto document
          │
          ▼
      TRACE log
          │
          ▼
     output artifact
```

TRACE can make population attrition, merges, derivations, analyses, validations, output production, and execution order easier to inspect. It does not replace code review, output review, specification review, or independent QC.

See [Reviewing Statistical Programs with TRACE](../framework/reviewer-guide.md) for the complete reviewer workflow.

## Next steps

- [TRACE API](../api/README.md) — exact public API signatures and parameter semantics.
- [TRACE Statistical Programming Examples](../../examples/README.md) — run the public CDISC Pilot Study flagship examples.
- [TRACE Reviewer Examples](../examples/README.md) — read those examples as execution evidence.
- [Using TRACE with Quarto](quarto.md) — use TRACE inside a Quarto statistical-programming workflow.
- [TRACE Core Operations v0.1](../framework/core-operations-v0.1.md) — canonical operation meanings.
