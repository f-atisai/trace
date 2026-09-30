# Getting Started with TRACE

TRACE adds structured logging to Python statistical programs without taking over the statistical work itself.

The basic pattern is:

```text
Do the statistical work.
Record the important operation nearby with TRACE.
```

Your pandas, Polars, NumPy, or other statistical code performs the filter, derivation, merge, analysis, or output. TRACE records the meaningful operation in a consistent form.

## Install TRACE

TRACE currently supports Python 3.10+ and can be installed from the repository:

```bash
git clone https://github.com/f-atisai/trace.git
cd trace
python -m pip install -e .
```

## Create a TRACE run

Import `Trace` and use it as a context manager around a program run:

```python
from trace_tlf import Trace

with Trace("L16_01") as trace:
    ...
```

TRACE records the run lifecycle automatically:

```text
INFO [START] [L16_01] execution started
...
INFO [END] [L16_01] execution completed – 0.01s
```

Use a new `Trace` instance for each program execution.

## Record an operation

Suppose `adsl` is a pandas DataFrame and you select the Safety Population:

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

The pandas expression performs the filter. TRACE records it:

```text
INFO [FILTER] [ADSL] SAFFL == 'Y' applied – N=4 → 3
```

This is the core TRACE workflow: **perform the work, then record the meaningful operation.**

You do not need to trace every line. Record operations that materially help another programmer or reviewer understand what happened during the run.

## A complete example

```python
from pathlib import Path

import pandas as pd

from trace_tlf import Trace


adsl = pd.DataFrame(
    {
        "USUBJID": ["SUBJ001", "SUBJ002", "SUBJ003", "SUBJ004"],
        "SAFFL": ["Y", "Y", "N", "Y"],
        "TRT01A": ["Placebo", "Drug A", "Drug A", "Placebo"],
    }
)

output_path = Path("outputs/safety_subjects.csv")
output_path.parent.mkdir(parents=True, exist_ok=True)

with Trace("L16_01", log_file="logs/L16_01.log") as trace:
    trace.read("ADSL", rows=len(adsl), columns=len(adsl.columns))

    safety = adsl.loc[adsl["SAFFL"] == "Y"]
    trace.filter(
        "ADSL",
        "SAFFL == 'Y'",
        result="Safety Population",
        before=len(adsl),
        after=len(safety),
    )

    safety.to_csv(output_path, index=False)
    trace.output(
        "Safety Population",
        output_path,
        format="CSV",
        rows=len(safety),
    )
```

Run the program normally:

```bash
python subject_listing.py
```

The console shows the execution as it happens:

```text
INFO [START] [L16_01] execution started
INFO [READ] [ADSL] loaded – N=4, Vars=3
INFO [FILTER] [ADSL] SAFFL == 'Y' applied – N=4 → 3
INFO [OUTPUT] [Safety Population] written – outputs/safety_subjects.csv, format=CSV, N=3
INFO [END] [L16_01] execution completed – 0.01s
```

Because `log_file` was supplied, TRACE also writes a finalized run log containing program-level run information and the recorded event stream.

## What to learn next

TRACE uses a small statistical-programming vocabulary:

```text
READ  CHECK  FILTER  SORT  DERIVE  TRANSFORM
MERGE  AGGREGATE  ANALYZE  VALIDATE  OUTPUT
```

- [Logging with TRACE](logging-with-trace.md) — learn how lifecycle, steps, file logs, provenance, and review fit together.
- [TRACE operations](guides/operations.md) — choose the right operation for your work.
- [Statistical programming examples](../examples/README.md) — run complete TRACE programs.

TRACE records what the program reports through its TRACE calls. It does not prove statistical correctness and does not replace code review, output review, or independent QC.
