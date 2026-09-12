"""Derive an ADLB-style ALT analysis dataset with baseline and change.

Representative TRACE output:
    INFO [READ] [ADSL] loaded – rows=5, columns=4
    INFO [READ] [ADLB_SOURCE] loaded – rows=9, columns=4
    INFO [FILTER] [ADLB_SOURCE] PARAMCD == 'ALT' applied – N=9 → 8
    INFO [MERGE] [ADLB_SOURCE + ADSL] merged – left_rows=8, right_rows=5, result_rows=8
    INFO [DERIVE] [ADY] created – dataset=ADLB, source=ADT, TRTSDT
    INFO [DERIVE] [ABLFL] created – dataset=ADLB, source=ADT, TRTSDT
    INFO [DERIVE] [BASE] created – dataset=ADLB, source=AVAL, ABLFL
    INFO [DERIVE] [CHG] created – dataset=ADLB, source=AVAL, BASE
    INFO [VALIDATE] [ADLB] at most one baseline record per subject and parameter – PASS
    INFO [OUTPUT] [ADLB] written – example-output/adlb.csv

Reviewer interpretation:
    Follow the derivation from source laboratory records through subject-level treatment
    data, analysis day, baseline selection, BASE, and CHG. Merge dimensions expose
    whether subject-level enrichment changed record cardinality, while validation makes
    the one-baseline-record expectation explicit.
"""

from pathlib import Path

import pandas as pd

from trace_tlf import Trace

OUTPUT_DIR = Path("example-output")
OUTPUT_DIR.mkdir(exist_ok=True)

adsl = pd.DataFrame(
    {
        "USUBJID": [f"STUDY01-{i:03d}" for i in range(1, 6)],
        "SAFFL": ["Y", "Y", "Y", "Y", "N"],
        "TRT01A": ["Placebo", "Drug A 100 mg", "Placebo", "Drug A 100 mg", "Placebo"],
        "TRTSDT": pd.to_datetime(["2026-01-05", "2026-01-06", "2026-01-07", "2026-01-08", "2026-01-09"]),
    }
)

adlb = pd.DataFrame(
    {
        "USUBJID": ["STUDY01-001", "STUDY01-001", "STUDY01-002", "STUDY01-002", "STUDY01-003", "STUDY01-003", "STUDY01-004", "STUDY01-004", "STUDY01-005"],
        "PARAMCD": ["ALT", "ALT", "ALT", "ALT", "ALT", "ALT", "ALT", "AST", "ALT"],
        "ADT": pd.to_datetime(["2026-01-04", "2026-01-12", "2026-01-05", "2026-01-15", "2026-01-07", "2026-01-20", "2026-01-07", "2026-01-07", "2026-01-08"]),
        "AVAL": [31.0, 35.0, 28.0, 30.0, 40.0, 44.0, 27.0, 25.0, 33.0],
    }
)

with Trace("ADLB", study="STUDY01") as trace:
    with trace.step("Read analysis sources"):
        trace.read("ADSL", source="analysis/adsl.parquet", rows=len(adsl), columns=len(adsl.columns))
        trace.read("ADLB_SOURCE", source="source/adlb_input.parquet", rows=len(adlb), columns=len(adlb.columns))

    with trace.step("Prepare ALT records"):
        adlb = adlb.sort_values(["USUBJID", "PARAMCD", "ADT"]).copy()
        trace.sort("ADLB_SOURCE", by=["USUBJID", "PARAMCD", "ADT"])

        source_rows = len(adlb)
        adlb = adlb.loc[adlb["PARAMCD"] == "ALT"].copy()
        trace.filter("ADLB_SOURCE", "PARAMCD == 'ALT'", before=source_rows, after=len(adlb))

    with trace.step("Add subject-level treatment data"):
        merged = adlb.merge(
            adsl[["USUBJID", "SAFFL", "TRT01A", "TRTSDT"]],
            on="USUBJID",
            how="left",
            validate="many_to_one",
        )
        trace.merge(
            "ADLB_SOURCE",
            "ADSL",
            on="USUBJID",
            how="left",
            result="ADLB_WORK",
            left_rows=len(adlb),
            right_rows=len(adsl),
            result_rows=len(merged),
            metrics={"unmatched_rows": int(merged["TRTSDT"].isna().sum())},
        )

    with trace.step("Derive analysis variables"):
        merged["ADY"] = (merged["ADT"] - merged["TRTSDT"]).dt.days
        merged["ADY"] = merged["ADY"].where(merged["ADY"] < 0, merged["ADY"] + 1)
        trace.derive("ADY", dataset="ADLB", source=["ADT", "TRTSDT"], method="ADT - TRTSDT; add 1 when non-negative")

        eligible = merged["ADT"].le(merged["TRTSDT"])
        latest_pre = merged.loc[eligible].groupby(["USUBJID", "PARAMCD"])["ADT"].transform("max")
        merged["ABLFL"] = ""
        merged.loc[eligible, "ABLFL"] = merged.loc[eligible, "ADT"].eq(latest_pre).map({True: "Y", False: ""})
        trace.derive("ABLFL", dataset="ADLB", source=["ADT", "TRTSDT"], method="latest assessment on or before treatment start")

        baseline = merged.loc[merged["ABLFL"] == "Y", ["USUBJID", "PARAMCD", "AVAL"]].rename(columns={"AVAL": "BASE"})
        merged = merged.merge(baseline, on=["USUBJID", "PARAMCD"], how="left", validate="many_to_one")
        trace.derive("BASE", dataset="ADLB", source=["AVAL", "ABLFL"], method="AVAL from baseline record by USUBJID and PARAMCD")

        merged["CHG"] = merged["AVAL"] - merged["BASE"]
        trace.derive("CHG", dataset="ADLB", source=["AVAL", "BASE"], method="AVAL - BASE")

    with trace.step("Validate ADLB"):
        trace.validate(
            "ADLB",
            "all records have subject-level treatment start date",
            passed=bool(merged["TRTSDT"].notna().all()),
            metrics={"missing_trtsdt_rows": int(merged["TRTSDT"].isna().sum())},
        )
        baseline_counts = merged.loc[merged["ABLFL"] == "Y"].groupby(["USUBJID", "PARAMCD"]).size()
        trace.validate(
            "ADLB",
            "at most one baseline record per subject and parameter",
            passed=bool((baseline_counts <= 1).all()),
            metrics={"baseline_records": int((merged["ABLFL"] == "Y").sum())},
        )

    path = OUTPUT_DIR / "adlb.csv"
    merged.to_csv(path, index=False)
    trace.output("ADLB", path, format="csv", rows=len(merged))
