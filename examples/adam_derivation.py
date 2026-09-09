from pathlib import Path

import pandas as pd

from trace_tlf import Trace

OUTPUT_DIR = Path("example-output")
OUTPUT_DIR.mkdir(exist_ok=True)

adsl = pd.DataFrame(
    {
        "USUBJID": ["SUBJ001", "SUBJ002", "SUBJ003", "SUBJ004"],
        "SAFFL": ["Y", "Y", "N", "Y"],
        "TRT01A": ["Placebo", "Drug A", "Drug A", "Placebo"],
        "TRTSDT": pd.to_datetime(
            ["2026-01-05", "2026-01-06", "2026-01-07", "2026-01-08"]
        ),
    }
)

adlb = pd.DataFrame(
    {
        "USUBJID": ["SUBJ002", "SUBJ001", "SUBJ004", "SUBJ001", "SUBJ002"],
        "PARAMCD": ["ALT", "ALT", "ALT", "ALT", "ALT"],
        "ADT": pd.to_datetime(
            ["2026-01-05", "2026-01-04", "2026-01-07", "2026-01-12", "2026-01-15"]
        ),
        "AVAL": [28.0, 31.0, 40.0, 35.0, 30.0],
    }
)

with Trace("ADLB", study="PROTO001") as trace:
    with trace.step("Read source data"):
        trace.read("ADSL", rows=len(adsl), columns=len(adsl.columns))
        trace.read("ADLB_SOURCE", rows=len(adlb), columns=len(adlb.columns))

    with trace.step("Prepare laboratory records"):
        adlb = adlb.sort_values(["USUBJID", "PARAMCD", "ADT"]).copy()
        trace.sort("ADLB_SOURCE", by=["USUBJID", "PARAMCD", "ADT"])

        source_rows = len(adlb)
        adlb = adlb.loc[adlb["PARAMCD"] == "ALT"].copy()
        trace.filter(
            "ADLB_SOURCE",
            "PARAMCD == 'ALT'",
            before=source_rows,
            after=len(adlb),
        )

    with trace.step("Merge subject-level treatment data"):
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
            metrics={
                "matched_rows": merged["USUBJID"].isin(adsl["USUBJID"]).sum(),
                "unmatched_rows": merged["TRTSDT"].isna().sum(),
            },
        )

    with trace.step("Derive analysis variables"):
        merged["ADY"] = (merged["ADT"] - merged["TRTSDT"]).dt.days
        merged["ADY"] = merged["ADY"].where(merged["ADY"] < 0, merged["ADY"] + 1)
        trace.derive(
            "ADY",
            dataset="ADLB",
            source=["ADT", "TRTSDT"],
            method="ADT - TRTSDT, add 1 for non-negative result",
        )

        eligible = merged["ADT"].le(merged["TRTSDT"])
        latest_pre = (
            merged.loc[eligible]
            .groupby(["USUBJID", "PARAMCD"])["ADT"]
            .transform("max")
        )
        merged["ABLFL"] = ""
        merged.loc[eligible, "ABLFL"] = (
            merged.loc[eligible, "ADT"].eq(latest_pre).map({True: "Y", False: ""})
        )
        trace.derive(
            "ABLFL",
            dataset="ADLB",
            source=["ADT", "TRTSDT"],
            method="latest assessment on or before treatment start",
        )

        baseline = (
            merged.loc[merged["ABLFL"] == "Y", ["USUBJID", "PARAMCD", "AVAL"]]
            .rename(columns={"AVAL": "BASE"})
        )
        merged = merged.merge(
            baseline,
            on=["USUBJID", "PARAMCD"],
            how="left",
        )
        trace.merge(
            "ADLB_WORK",
            "BASELINE_VALUES",
            on=["USUBJID", "PARAMCD"],
            how="left",
            result="ADLB_WORK",
            left_rows=len(merged),
            right_rows=len(baseline),
            result_rows=len(merged),
        )

        merged["CHG"] = merged["AVAL"] - merged["BASE"]
        trace.derive(
            "CHG",
            dataset="ADLB",
            source=["AVAL", "BASE"],
            method="AVAL - BASE",
        )

    with trace.step("Validate analysis dataset"):
        trace.validate(
            "ADLB",
            "all records have subject-level treatment start date",
            passed=bool(merged["TRTSDT"].notna().all()),
            metrics={"missing_trtsdt": int(merged["TRTSDT"].isna().sum())},
        )

        baseline_counts = (
            merged.loc[merged["ABLFL"] == "Y"]
            .groupby(["USUBJID", "PARAMCD"])
            .size()
        )
        trace.validate(
            "ADLB",
            "at most one baseline record per subject and parameter",
            passed=bool((baseline_counts <= 1).all()),
            metrics={"baseline_records": int((merged["ABLFL"] == "Y").sum())},
        )

    with trace.step("Write output"):
        path = OUTPUT_DIR / "adlb.csv"
        merged.to_csv(path, index=False)
        trace.output("ADLB", path, format="csv", rows=len(merged))
