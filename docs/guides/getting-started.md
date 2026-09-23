# Getting Started with TRACE

Add TRACE to a statistical program in a few minutes. Keep using pandas and your usual reporting tools; TRACE simply records the operations you want reviewers to see.

## Install TRACE

TRACE currently supports Python 3.10+ and can be installed from the repository:

```bash
git clone https://github.com/f-atisai/trace.git
cd trace
python -m pip install -e .
```

The example below uses pandas:

```bash
python -m pip install pandas
```

## Create a subject listing

Save this example as `subject_listing.py`. It creates a small safety-population listing and records the important parts of the run.

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

TRACE prints each event as it happens:

```text
INFO [START] [L16_01] execution started
INFO [READ] [ADSL] loaded – N=4, Vars=5
INFO [FILTER] [ADSL] SAFFL == 'Y' applied – N=4 → 3
INFO [OUTPUT] [Safety Subject Listing] written – outputs/safety_subject_listing.csv, format=CSV, N=3
INFO [END] [L16_01] execution completed – 0.01s
```

That is the basic TRACE pattern: perform the work, then record the operation with a nearby TRACE call.

>Tip: You do not need to trace every line.

For every available method and parameter, see the [TRACE API](../api/README.md).

## Open the review log

The example also creates `logs/L16_01.log`. It begins with the run and its output artifact, followed by the execution events:

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

Start each execution with a new `Trace` instance. TRACE records what the program did.

> Note: TRACE does not replace code review, output review, or independent QC.

## Where to go next

- [TRACE API](../api/README.md) — explore every operation and parameter.
- [TRACE Statistical Programming Examples](../../examples/README.md) — run the public CDISC Pilot Study examples.
- [Reviewing Statistical Programs with TRACE](../framework/reviewer-guide.md) — see how TRACE fits into review.
- [Using TRACE with Quarto](quarto.md) — add TRACE to a Quarto workflow.
