"""Subject listing for participants in the Safety Population.

Representative TRACE output:
    INFO [READ] [ADSL] loaded – rows=6, columns=6
    INFO [FILTER] [ADSL] SAFFL == 'Y' applied – N=6 → 5
    INFO [SORT] [Safety Population] sorted – by=TRT01A, USUBJID
    INFO [TRANSFORM] [Safety Population] reporting columns selected
    INFO [OUTPUT] [L16_01] written – example-output/subject_listing.csv

Reviewer interpretation:
    Confirm that the listing is restricted to the intended population, ordered by
    treatment and participant, and contains the expected reporting columns. TRACE
    records the material listing preparation rather than every display-formatting line.
"""

from pathlib import Path

import pandas as pd

from trace_tlf import Trace

OUTPUT_DIR = Path("example-output")
OUTPUT_DIR.mkdir(exist_ok=True)

adsl = pd.DataFrame(
    {
        "USUBJID": [
            "STUDY01-003",
            "STUDY01-001",
            "STUDY01-006",
            "STUDY01-004",
            "STUDY01-002",
            "STUDY01-005",
        ],
        "SAFFL": ["Y", "Y", "Y", "N", "Y", "Y"],
        "ITTFL": ["Y", "Y", "Y", "Y", "Y", "Y"],
        "TRT01A": [
            "Drug A 100 mg",
            "Placebo",
            "Drug A 100 mg",
            "Placebo",
            "Placebo",
            "Drug A 100 mg",
        ],
        "AGE": [59, 44, 72, 66, 63, 51],
        "SEX": ["F", "M", "F", "M", "F", "M"],
    }
)

with Trace("L16_01", study="STUDY01") as trace:
    trace.read(
        "ADSL",
        source="analysis/adsl.parquet",
        rows=len(adsl),
        columns=len(adsl.columns),
    )

    listing = adsl.loc[adsl["SAFFL"] == "Y"].copy()
    trace.filter(
        "ADSL",
        "SAFFL == 'Y'",
        result="Safety Population",
        before=len(adsl),
        after=len(listing),
    )

    listing = listing.sort_values(["TRT01A", "USUBJID"])
    trace.sort(
        "Safety Population",
        by=["TRT01A", "USUBJID"],
        ascending=[True, True],
    )

    listing = listing[["USUBJID", "TRT01A", "AGE", "SEX"]].copy()
    trace.transform(
        "Safety Population",
        "reporting columns selected",
        result="subject_listing",
        details={"columns": ["USUBJID", "TRT01A", "AGE", "SEX"]},
    )

    path = OUTPUT_DIR / "subject_listing.csv"
    listing.to_csv(path, index=False)
    trace.output("L16_01", path, format="csv", rows=len(listing))
