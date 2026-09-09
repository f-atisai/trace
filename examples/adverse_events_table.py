from pathlib import Path

import pandas as pd

from trace_tlf import Trace

OUTPUT_DIR = Path("example-output")
OUTPUT_DIR.mkdir(exist_ok=True)

adsl = pd.DataFrame(
    {
        "USUBJID": ["SUBJ001", "SUBJ002", "SUBJ003", "SUBJ004", "SUBJ005", "SUBJ006"],
        "SAFFL": ["Y", "Y", "Y", "N", "Y", "Y"],
        "TRT01A": ["Placebo", "Placebo", "Drug A", "Drug A", "Drug A", "Placebo"],
    }
)

adae = pd.DataFrame(
    {
        "USUBJID": ["SUBJ001", "SUBJ001", "SUBJ002", "SUBJ003", "SUBJ004", "SUBJ005", "SUBJ005"],
        "TRTEMFL": ["Y", "Y", "N", "Y", "Y", "Y", "Y"],
        "AESOC": [
            "Gastrointestinal disorders",
            "Nervous system disorders",
            "Nervous system disorders",
            "Gastrointestinal disorders",
            "Infections",
            "Nervous system disorders",
            "Nervous system disorders",
        ],
    }
)

with Trace("T14_03", study="PROTO001") as trace:
    trace.read("ADSL", rows=len(adsl), columns=len(adsl.columns))
    trace.read("ADAE", rows=len(adae), columns=len(adae.columns))

    safety = adsl.loc[adsl["SAFFL"] == "Y", ["USUBJID", "TRT01A"]].copy()
    trace.filter("ADSL", "SAFFL == 'Y'", before=len(adsl), after=len(safety))

    teae = adae.loc[adae["TRTEMFL"] == "Y"].copy()
    trace.filter("ADAE", "TRTEMFL == 'Y'", before=len(adae), after=len(teae))

    merged = teae.merge(
        safety,
        on="USUBJID",
        how="inner",
        validate="many_to_one",
    )
    matched_subjects = int(merged["USUBJID"].nunique())
    unmatched_subjects = int(
        teae.loc[
            ~teae["USUBJID"].isin(safety["USUBJID"]),
            "USUBJID",
        ].nunique()
    )

    trace.merge(
        "ADAE",
        "ADSL",
        on="USUBJID",
        how="inner",
        result="TEAE_SAFETY",
        left_rows=len(teae),
        right_rows=len(safety),
        result_rows=len(merged),
        metrics={
            "matched_subjects": matched_subjects,
            "unmatched_subjects": unmatched_subjects,
        },
    )

    summary = (
        merged.groupby(["TRT01A", "AESOC"])["USUBJID"]
        .nunique()
        .reset_index(name="N")
    )
    trace.aggregate(
        "TEAE_SAFETY",
        by=["TRT01A", "AESOC"],
        result="ae_summary",
        method="distinct subjects",
        rows=len(summary),
    )

    trace.validate(
        "TEAE_SAFETY",
        "all merged subjects belong to safety population",
        passed=bool(merged["USUBJID"].isin(safety["USUBJID"]).all()),
        metrics={"subjects": matched_subjects},
    )

    path = OUTPUT_DIR / "adverse_events_table.csv"
    summary.to_csv(path, index=False)
    trace.output("T14_03", path, format="csv", rows=len(summary))
