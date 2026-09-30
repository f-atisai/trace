"""Basic TRACE workflow using a small in-memory ADSL-like dataset.

This example is intentionally small. It demonstrates the core TRACE pattern:
perform the statistical work first, then record the meaningful operation nearby.
"""

from pathlib import Path

import pandas as pd

from trace_tlf import Trace

OUTPUT_DIR = Path("example-output")
OUTPUT_DIR.mkdir(exist_ok=True)

OUTPUT_PATH = OUTPUT_DIR / "safety_population.csv"
LOG_PATH = OUTPUT_DIR / "basic_analysis_workflow.log"

adsl = pd.DataFrame(
    {
        "USUBJID": ["01-001", "01-002", "01-003", "01-004"],
        "SAFFL": ["Y", "Y", "N", "Y"],
        "TRT01A": ["Placebo", "Drug A", "Drug A", "Placebo"],
        "AGE": [45, 62, 51, 70],
    }
)

with Trace("BASIC_ANALYSIS", study="Example Study", log_file=LOG_PATH) as trace:
    trace.read("ADSL", rows=len(adsl), columns=len(adsl.columns))

    safety = adsl.loc[adsl["SAFFL"] == "Y"].copy()
    trace.filter(
        "ADSL",
        "SAFFL == 'Y'",
        result="Safety Population",
        before=len(adsl),
        after=len(safety),
    )

    safety["AGEGR1"] = pd.cut(
        safety["AGE"],
        bins=[0, 64, 200],
        labels=["<65", ">=65"],
    )
    trace.derive(
        "AGEGR1",
        dataset="ADSL",
        source="AGE",
        method="<65 / >=65 age category",
    )

    safety.to_csv(OUTPUT_PATH, index=False)
    trace.output(
        "Safety Population",
        OUTPUT_PATH,
        format="CSV",
        rows=len(safety),
    )
