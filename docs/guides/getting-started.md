# Getting Started with TRACE

Add structured logging to a statistical program in a few minutes. Keep using pandas, Polars, or your usual reporting tools; TRACE records the important statistical operations around that work.

The basic pattern is simple:

```text
Do the statistical work.
Record the important operation nearby with TRACE.
```

TRACE does not perform the filter, derivation, merge, analysis, or output for you. Your statistical code does the work; TRACE records what happened in a consistent form.

## Install TRACE

TRACE currently supports Python 3.10+ and can be installed from the repository:

```bash
git clone https://github.com/f-atisai/trace.git
cd trace
python -m pip install -e .
```

The examples below use pandas:

```bash
python -m pip install pandas
```

## Create your first TRACE run

Start a run with `Trace`:

```python
from trace_tlf import Trace

with Trace("L16_01") as trace:
    ...
```

TRACE automatically records the start and end of the execution:

```text
INFO [START] [L16_01] execution started
...
INFO [END] [L16_01] execution completed – 0.01s
```

Use a new `Trace` instance for each program execution.

## Record a statistical operation

Suppose `adsl` is a pandas DataFrame and you select the safety population:

```python
listing = adsl.loc[adsl["SAFFL"] == "Y"]

trace.filter(
    "ADSL",
    "SAFFL == 'Y'",
    before=len(adsl),
    after=len(listing),
)
```

The pandas expression performs the filter. The nearby TRACE call records it:

```text
INFO [FILTER] [ADSL] SAFFL == 'Y' applied – N=4 → 3
```

This is the core TRACE workflow: **perform the work, then record the meaningful operation.**

You do not need to trace every line. Record the operations that help another programmer or reviewer understand how the run progressed.

## Add common operations

TRACE uses statistical-programming operations instead of arbitrary log messages. A small program might record a dataset read, a population filter, and an output:

```python
trace.read("ADSL", rows=len(adsl), columns=len(adsl.columns))

listing = adsl.loc[adsl["SAFFL"] == "Y"]
trace.filter(
    "ADSL",
    "SAFFL == 'Y'",
    result="Safety Subject Listing",
    before=len(adsl),
    after=len(listing),
)

listing.to_csv("outputs/safety_subject_listing.csv", index=False)
trace.output(
    "Safety Subject Listing",
    "outputs/safety_subject_listing.csv",
    format="CSV",
    rows=len(listing),
)
```

The resulting log follows the same vocabulary each time:

```text
INFO [READ] [ADSL] loaded – N=4, Vars=5
INFO [FILTER] [ADSL] SAFFL == 'Y' applied – N=4 → 3
INFO [OUTPUT] [Safety Subject Listing] written – outputs/safety_subject_listing.csv, format=CSV, N=3
```

Other TRACE operations cover checks, sorting, derivations, transformations, merges, aggregation, analyses, and validation. Use the [TRACE operations guide](operations.md) to choose the right operation, and the [TRACE API](../api/README.md) for exact method parameters.

## Put it together

Save the following as `subject_listing.py`:

```python
from pathlib import Path

import pandas as pd

from trace_tlf import Trace


adsl = pd.DataFrame(
    {
        "USUBJID": ["SUBJ001", "SUBJ002", "SUBJ003", "SUBJ004"],
        "SAFFL": ["Y", "Y", "N", "Y"],
        "TRT01A": ["Placebo", "Drug A", "Drug A", "Placebo"],
        "AGE": [45, 62, 51, 70],
        "SEX": ["F", "M", "F", "M"],
    }
)

output_path = Path("outputs/safety_subject_listing.csv")
output_path.parent.mkdir(exist_ok=True)

with Trace("L16_01", log_file="logs/L16_01.log") as trace:
    trace.read("ADSL", rows=len(adsl), columns=len(adsl.columns))

    listing = adsl.loc[
        adsl["SAFFL"] == "Y",
        ["USUBJID", "TRT01A", "AGE", "SEX"],
    ].sort_values(["TRT01A", "USUBJID"])

    trace.filter(
        "ADSL",
        "SAFFL == 'Y'",
        result="Safety Subject Listing",
        before=len(adsl),
        after=len(listing),
    )

    listing.to_csv(output_path, index=False)
    trace.output(
        "Safety Subject Listing",
        output_path,
        format="CSV",
        rows=len(listing),
    )
```

Run it:

```bash
python subject_listing.py
```

TRACE prints the execution log as the program runs:

```text
INFO [START] [L16_01] execution started
INFO [READ] [ADSL] loaded – N=4, Vars=5
INFO [FILTER] [ADSL] SAFFL == 'Y' applied – N=4 → 3
INFO [OUTPUT] [Safety Subject Listing] written – outputs/safety_subject_listing.csv, format=CSV, N=3
INFO [END] [L16_01] execution completed – 0.01s
```

## Write a review log

Pass `log_file` when you want a finalized log for the run:

```python
with Trace("L16_01", log_file="logs/L16_01.log") as trace:
    ...
```

The file begins with program-level run information and registered artifacts, followed by the execution log:

```text
TRACE EXECUTION

Program:  L16_01
Run ID:   7eab...
Executed: 2026-09-14T14:32:18Z

Input artifacts:
  (none)

Output artifacts:
  outputs/safety_subject_listing.csv

INFO [START] [L16_01] execution started
...
INFO [END] [L16_01] execution completed – 0.01s
```

This gives the execution log enough context to identify the program, run, execution time, and input/output artifacts without changing ownership of the statistical work.

TRACE records what the program reports through its TRACE calls. It does not independently prove that the statistical result is correct, and it does not replace code review, output review, or independent QC.

## Where to go next

- [TRACE operations](operations.md) — choose the right statistical operation and see practical examples.
- [TRACE API](../api/README.md) — see exact supported methods and parameters.
- [TRACE Statistical Programming Examples](../../examples/README.md) — run complete examples using the public CDISC Pilot Study data.
- [Reviewing Statistical Programs with TRACE](../framework/reviewer-guide.md) — see how another programmer or reviewer can use TRACE logs.
- [Using TRACE with Quarto](quarto.md) — add TRACE to a Quarto workflow.
