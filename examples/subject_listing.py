from pathlib import Path

import pandas as pd

from trace_tlf import Trace

OUTPUT_DIR = Path("example-output")
OUTPUT_DIR.mkdir(exist_ok=True)

adsl = pd.DataFrame(
    {
        "USUBJID": ["SUBJ003", "SUBJ001", "SUBJ004", "SUBJ002"],
        "SAFFL": ["Y", "Y", "N", "Y"],
        "TRT01A": ["Drug A", "Placebo", "Drug A", "Placebo"],
        "AGE": [59, 44, 72, 66],
        "SEX": ["F", "M", "F", "M"],
    }
)

with Trace("L16_01", study="PROTO001") as trace:
    trace.read("ADSL", rows=len(adsl), columns=len(adsl.columns))

    listing = adsl.loc[adsl["SAFFL"] == "Y"].copy()
    trace.filter("ADSL", "SAFFL == 'Y'", before=len(adsl), after=len(listing))

    listing = listing.sort_values(["TRT01A", "USUBJID"])
    trace.sort(
        "ADSL",
        by=["TRT01A", "USUBJID"],
        ascending=[True, True],
    )

    listing["AGE_SEX"] = listing["AGE"].astype(str) + " / " + listing["SEX"]
    listing = listing[["USUBJID", "TRT01A", "AGE_SEX"]]
    trace.transform(
        "ADSL",
        "combined AGE and SEX for listing display",
        source="AGE, SEX",
        result="AGE_SEX",
    )

    path = OUTPUT_DIR / "subject_listing.csv"
    listing.to_csv(path, index=False)
    trace.output("L16_01", path, format="csv", rows=len(listing))
