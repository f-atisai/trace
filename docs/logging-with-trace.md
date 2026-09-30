# Logging with TRACE

TRACE adds structured, statistical-programming-aware logging around the work your program already performs.

The mental model is simple:

```text
statistical code does the work
          ↓
TRACE records the meaningful operation
          ↓
consistent execution log
```

TRACE does not filter data, derive variables, fit models, or generate outputs for you. pandas, Polars, NumPy, statistical libraries, or your own code perform those tasks. TRACE records the important operations and diagnostics nearby.

## Create a managed run

For a complete program run, use `Trace` as a context manager:

```python
from trace_tlf import Trace

with Trace("T14_01") as trace:
    ...
```

TRACE records the run boundaries automatically:

```text
INFO [START] [T14_01] execution started
...
INFO [END] [T14_01] execution completed – 0.84s
```

If the program exits through an ordinary Python exception, TRACE records a failed `END` event and the original exception continues to propagate.

Use a new `Trace` instance for each program execution.

## Record operations, not arbitrary messages

A TRACE call creates a structured event and then renders it as a readable log line.

```text
TRACE call
   ↓
structured event
   ↓
renderer
   ↓
execution log
```

For example:

```python
safety = adsl.loc[adsl["SAFFL"] == "Y"]

trace.filter(
    "ADSL",
    "SAFFL == 'Y'",
    result="Safety Population",
    before=len(adsl),
    after=len(safety),
)
```

produces a line such as:

```text
INFO [FILTER] [ADSL] SAFFL == 'Y' applied – N=754 → 720
```

The value of the structured event model is consistency. Instead of inventing a new `logging.info()` string for every program, TRACE uses the same operation vocabulary and rendering conventions across programs.

Use [TRACE operations](operations.md) to choose the right operation for a statistical task.

## What to log

Record operations that materially help someone understand how the analysis progressed.

Good candidates include:

- important input datasets;
- analysis-population and subset filters;
- meaningful derivations;
- merges where keys or row counts matter;
- grouped summaries;
- statistical analyses;
- explicit validations;
- material reporting transformations; and
- externally produced outputs.

For example:

```python
trace.read("ADSL", source="data/adsl.xpt", rows=len(adsl), columns=len(adsl.columns))

safety = adsl.loc[adsl["SAFFL"] == "Y"]
trace.filter(
    "ADSL",
    "SAFFL == 'Y'",
    result="Safety Population",
    before=len(adsl),
    after=len(safety),
)

summary.to_csv("outputs/safety_summary.csv", index=False)
trace.output(
    "Safety Summary",
    "outputs/safety_summary.csv",
    format="CSV",
    rows=len(summary),
)
```

## What not to log

TRACE is not intended to be a line-by-line execution trace.

Avoid recording:

- every temporary variable;
- every dataframe method call;
- implementation details that do not help explain the analysis;
- long narrative rationale already documented elsewhere; or
- duplicate events for the same meaningful operation.

A useful rule is: **record the analytical decision or transition, not every Python statement used to implement it.**

## Use steps for logical stages

`trace.step()` groups a coarse stage of the program:

```python
with trace.step("Analysis population"):
    safety = adsl.loc[adsl["SAFFL"] == "Y"]
    trace.filter(
        "ADSL",
        "SAFFL == 'Y'",
        result="Safety Population",
        before=len(adsl),
        after=len(safety),
    )
```

TRACE records the step boundaries around the operation:

```text
INFO [STEP]   [Analysis population] started
INFO [FILTER] [ADSL] SAFFL == 'Y' applied – N=754 → 720
INFO [STEP]   [Analysis population] completed – 0.031s
```

Good step names describe recognizable analysis stages such as:

```text
Load analysis data
Select safety population
Derive analysis variables
Generate statistics
Format table
Write output
```

Do not wrap every individual operation in its own step. Steps are most useful when they make the larger execution flow easier to scan.

## Console logging and finalized file logs

TRACE events are written to the console as the program runs.

For a persistent review log, supply `log_file` to a managed run:

```python
with Trace("T14_01", log_file="logs/T14_01.log") as trace:
    ...
```

After the run completes, the file contains program-level provenance followed by the recorded event stream:

```text
TRACE EXECUTION

Program:  T14_01
Run ID:   7eab...
Executed: 2026-09-30T09:15:22Z

Input artifacts:
  data/adsl.xpt

Output artifacts:
  outputs/T14_01.rtf

INFO [START] [T14_01] execution started
...
INFO [END] [T14_01] execution completed – 0.84s
```

The console answers **what is happening now**. The finalized log records **what happened in this run**.

## Program-level provenance

TRACE keeps provenance at the run level rather than repeating it on every event.

The current Developer Preview records:

- **Program** — the program identity supplied to `Trace`;
- **Run ID** — one identifier for the TRACE execution;
- **Executed** — the execution timestamp;
- **Input artifacts** — physical paths registered by supported `READ` calls; and
- **Output artifacts** — physical paths registered by supported `OUTPUT` calls.

For example:

```python
with Trace("T14_01", log_file="logs/T14_01.log") as trace:
    trace.read(
        "ADSL",
        source="data/adsl.xpt",
        rows=len(adsl),
        columns=len(adsl.columns),
    )

    # statistical work

    trace.output("T14_01", "outputs/T14_01.rtf", format="RTF")
```

The `READ` and `OUTPUT` events explain the statistical workflow. The provenance block identifies the physical artifacts associated with the run.

Artifact hashing, environment fingerprinting, and public provenance configuration are not part of the current Developer Preview.

## TRACE works in normal Python environments

TRACE does not depend on a particular authoring environment. The same instrumentation pattern can be used in:

```text
.py scripts
.qmd documents
notebooks
batch pipelines
scheduled jobs
other Python execution environments
```

For example, Quarto can provide narrative and analysis code while TRACE records the important operations executed by that code. TRACE does not need a Quarto-specific mode, extension, or vocabulary.

Keep responsibilities separate:

```text
narrative/specification   why the analysis is being done
Python code               how it is implemented
TRACE log                 what operations were recorded during the run
output                    the resulting analytical artifact
```

## Reading a TRACE log

Read the events in execution order. The log is intended to provide a compact map of the statistical workflow.

For example:

```text
READ ADSL
  → FILTER Safety Population
  → DERIVE analysis variable
  → AGGREGATE treatment summary
  → VALIDATE expected relationship
  → OUTPUT table
```

Useful review questions include:

- Were the expected inputs recorded?
- Did populations or subsets change plausibly?
- Did merge row counts behave as expected?
- Were important derivations or analyses recorded?
- Did explicit validations pass or fail?
- Was the expected output produced?
- Does the sequence of operations make sense against the program and specification?

TRACE does not infer operations that were never instrumented. The absence of an event does not prove that an operation did not occur.

## TRACE and correctness

A clean TRACE log does not prove that:

- the specification is correct;
- the source data are correct;
- a derivation or model is correctly implemented;
- every important operation was instrumented;
- the resulting table, listing, figure, or dataset is correct; or
- independent QC is unnecessary.

A passing `VALIDATE` event means only that the implemented validation criterion evaluated successfully.

TRACE is a logging and review aid. Use it alongside the source code, specification, output, and applicable QC process.

## Where to go next

- [Getting Started](getting-started.md) — instrument a first TRACE program.
- [TRACE operations](operations.md) — choose the right operation and see practical examples.
- [Examples](../examples/README.md) — run complete statistical-programming workflows.
