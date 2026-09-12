"""Independent QC comparison of a demographics result.

Representative TRACE output:
    INFO [READ] [T14_01_PRODUCTION] loaded – rows=6, columns=5
    INFO [READ] [T14_01_QC] loaded – rows=6, columns=5
    INFO [MERGE] [T14_01_PRODUCTION + T14_01_QC] merged
    INFO [VALIDATE] [T14_01] production and QC keys match – PASS
    INFO [VALIDATE] [T14_01] production and QC statistics match – PASS
    INFO [OUTPUT] [QC_T14_01] written – example-output/qc_comparison.csv

Reviewer interpretation:
    The QC program treats production and independently programmed results as separate
    inputs, aligns them by reporting keys, then explicitly validates key coverage and
    statistic equality. A PASS records that these implemented comparisons passed; it
    does not establish correctness beyond the checks performed.
"""

from pathlib import Path

import pandas as pd

from trace_tlf import Trace

OUTPUT_DIR = Path("example-output")
OUTPUT_DIR.mkdir(exist_ok=True)

TREATMENTS = [
    "Placebo",
    "Placebo",
    "Placebo",
    "Drug A 100 mg",
    "Drug A 100 mg",
    "Drug A 100 mg",
]

production = pd.DataFrame(
    {
        "TRT01A": TREATMENTS,
        "STAT": ["N", "MEAN", "SD", "N", "MEAN", "SD"],
        "PARAM": ["AGE"] * 6,
        "VALUE": [118.0, 58.4, 12.6, 121.0, 60.1, 11.9],
        "DISPLAY": ["118", "58.4", "12.6", "121", "60.1", "11.9"],
    }
)

qc = pd.DataFrame(
    {
        "TRT01A": TREATMENTS,
        "STAT": ["N", "MEAN", "SD", "N", "MEAN", "SD"],
        "PARAM": ["AGE"] * 6,
        "VALUE": [118.0, 58.4, 12.6, 121.0, 60.1, 11.9],
        "DISPLAY": ["118", "58.4", "12.6", "121", "60.1", "11.9"],
    }
)

with Trace("QC_T14_01", study="STUDY01") as trace:
    trace.read(
        "T14_01_PRODUCTION",
        source="outputs/T14_01.csv",
        rows=len(production),
        columns=len(production.columns),
    )
    trace.read(
        "T14_01_QC",
        source="qc/T14_01_qc.csv",
        rows=len(qc),
        columns=len(qc.columns),
    )

    keys = ["TRT01A", "PARAM", "STAT"]
    comparison = production.merge(
        qc,
        on=keys,
        suffixes=("_PROD", "_QC"),
        how="outer",
        indicator=True,
        validate="one_to_one",
    )
    trace.merge(
        "T14_01_PRODUCTION",
        "T14_01_QC",
        on=keys,
        how="outer",
        result="T14_01_COMPARISON",
        left_rows=len(production),
        right_rows=len(qc),
        result_rows=len(comparison),
        metrics={
            "unmatched_keys": int((comparison["_merge"] != "both").sum())
        },
    )

    keys_match = bool((comparison["_merge"] == "both").all())
    trace.validate(
        "T14_01",
        "production and QC keys match",
        passed=keys_match,
        metrics={
            "unmatched_keys": int((comparison["_merge"] != "both").sum())
        },
    )

    value_match = comparison["VALUE_PROD"].eq(comparison["VALUE_QC"])
    display_match = comparison["DISPLAY_PROD"].eq(comparison["DISPLAY_QC"])
    statistics_match = bool((value_match & display_match).all())
    trace.validate(
        "T14_01",
        "production and QC statistics match",
        passed=statistics_match,
        metrics={"mismatched_rows": int((~(value_match & display_match)).sum())},
    )

    path = OUTPUT_DIR / "qc_comparison.csv"
    comparison.to_csv(path, index=False)
    trace.output("QC_T14_01", path, format="csv", rows=len(comparison))
