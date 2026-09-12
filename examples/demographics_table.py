"""Demographics table for the Safety Population.

Representative TRACE output:
    INFO [READ] [ADSL] loaded – rows=12, columns=6
    INFO [FILTER] [ADSL] SAFFL == 'Y' applied – N=12 → 10
    INFO [DERIVE] [AGEGR1] created – dataset=ADSL, source=AGE
    INFO [AGGREGATE] [ADSL] aggregated – by=TRT01A, SEX, AGEGR1
    INFO [VALIDATE] [demographics_summary] expected treatment groups present – PASS
    INFO [OUTPUT] [T14_01] written – example-output/demographics_table.csv

Reviewer interpretation:
    Confirm that the Safety Population was selected, the age grouping matches the
    intended analysis, both treatment groups are represented, and the summary was
    produced from the expected population. Counts are execution diagnostics, not
    proof that the population definition is statistically correct.
"""

from pathlib import Path

import pandas as pd

from trace_tlf import Trace

OUTPUT_DIR = Path("example-output")
OUTPUT_DIR.mkdir(exist_ok=True)

adsl = pd.DataFrame(
    {
        "USUBJID": [f"STUDY01-{i:03d}" for i in range(1, 13)],
        "SAFFL": ["Y", "Y", "Y", "N", "Y", "Y", "Y", "Y", "N", "Y", "Y", "Y"],
        "ITTFL": ["Y"] * 12,
        "TRT01A": ["Placebo"] * 6 + ["Drug A 100 mg"] * 6,
        "AGE": [42, 67, 58, 71, 36, 64, 69, 55, 62, 73, 48, 66],
        "SEX": ["F", "M", "F", "M", "F", "M", "F", "M", "F", "M", "F", "M"],
    }
)

with Trace("T14_01", study="STUDY01") as trace:
    with trace.step("Read analysis data"):
        trace.read(
            "ADSL",
            source="analysis/adsl.parquet",
            rows=len(adsl),
            columns=len(adsl.columns),
        )

    with trace.step("Safety Population"):
        safety = adsl.loc[adsl["SAFFL"] == "Y"].copy()
        trace.filter(
            "ADSL",
            "SAFFL == 'Y'",
            before=len(adsl),
            after=len(safety),
        )

    with trace.step("Demographic summaries"):
        safety["AGEGR1"] = pd.cut(
            safety["AGE"],
            bins=[0, 65, float("inf")],
            labels=["<65", ">=65"],
            right=False,
        )
        trace.derive(
            "AGEGR1",
            dataset="ADSL",
            source="AGE",
            method="AGE < 65 vs AGE >= 65",
        )

        summary = (
            safety.groupby(["TRT01A", "SEX", "AGEGR1"], observed=False)["USUBJID"]
            .nunique()
            .reset_index(name="N")
        )
        trace.aggregate(
            "ADSL",
            by=["TRT01A", "SEX", "AGEGR1"],
            result="demographics_summary",
            method="distinct subjects",
            rows=len(summary),
        )

        expected_treatments = {"Placebo", "Drug A 100 mg"}
        observed_treatments = set(safety["TRT01A"].dropna().unique())
        trace.validate(
            "demographics_summary",
            "expected treatment groups present",
            passed=observed_treatments == expected_treatments,
            metrics={"treatment_groups": len(observed_treatments)},
        )

    with trace.step("Write table"):
        path = OUTPUT_DIR / "demographics_table.csv"
        summary.to_csv(path, index=False)
        trace.output("T14_01", path, format="csv", rows=len(summary))
