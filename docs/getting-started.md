# Getting Started

TRACE adds structured logging to Python statistical programs without taking over the statistical work itself.

The basic pattern is:

```text
Do the statistical work.
Record the important operation nearby with TRACE.
```

Your pandas, Polars, NumPy, or other statistical code performs the analysis. TRACE records the meaningful operation in a consistent form.

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
from trace_stat import Trace

with Trace("EXAMPLE") as trace:
    ...
```

TRACE records the run lifecycle automatically:

```text
INFO [START] [EXAMPLE] execution started
...
INFO [END] [EXAMPLE] execution completed – 0.01s
```

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

The pandas expression performs the filter. TRACE records it as:

```text
INFO [FILTER] [ADSL] SAFFL == 'Y' applied – N=4 → 3
```

This is the core TRACE workflow: **perform the work, then record the meaningful operation.**

You do not need to trace every line. Record operations that materially help another programmer or reviewer understand what happened during the run.

## A complete example

The repository includes a four-row example subject-level dataset at `examples/data/example_adsl.csv`. If you are following this guide without cloning the repository, [download the example CSV](https://raw.githubusercontent.com/f-atisai/trace/main/examples/data/example_adsl.csv) and save it at that path.

```python
from pathlib import Path

import pandas as pd

from trace_stat import Trace

input_path = Path("examples/data/example_adsl.csv")
output_path = Path("outputs/safety_subjects.csv")
output_path.parent.mkdir(parents=True, exist_ok=True)

with Trace("EXAMPLE", log_file="logs/EXAMPLE.log") as trace:
    adsl = pd.read_csv(input_path)
    trace.read(
        "ADSL",
        source=str(input_path),
        rows=len(adsl),
        columns=len(adsl.columns),
    )

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
INFO [START] [EXAMPLE] execution started
INFO [READ] [ADSL] loaded – source=examples/data/example_adsl.csv, N=4, Vars=3
INFO [FILTER] [ADSL] SAFFL == 'Y' applied – N=4 → 3
INFO [OUTPUT] [Safety Population] written – outputs/safety_subjects.csv, format=CSV, N=3
INFO [END] [EXAMPLE] execution completed – 0.01s
```

Because `log_file` was supplied, TRACE also writes a finalized run log containing program-level run information and the recorded event stream.

## Next Steps

TRACE uses a small statistical-programming vocabulary:

```text
READ  CHECK  FILTER  SORT  DERIVE  TRANSFORM
MERGE  AGGREGATE  ANALYZE  VALIDATE  OUTPUT
```

Use [TRACE operations](operations.md) to choose the right operation for your work.

Use [Logging with TRACE](logging-with-trace.md) to learn about steps, finalized file logs, provenance, and how to read a TRACE run.

For complete runnable programs, see the [statistical programming examples](../examples/README.md).

TRACE records what the program reports through its TRACE calls. It does not prove statistical correctness and does not replace code review, output review, or independent QC.
