from pathlib import Path

import pandas as pd

from trace_tlf import Trace

OUTPUT_DIR = Path("example-output")
OUTPUT_DIR.mkdir(exist_ok=True)

adsl = pd.DataFrame(
    {
        "USUBJID": [f"SUBJ{i:03d}" for i in range(1, 13)],
        "SAFFL": ["Y", "Y", "Y", "N", "Y", "Y", "Y", "Y", "N", "Y", "Y", "Y"],
        "TRT01A": ["Placebo"] * 6 + ["Drug A"] * 6,
        "AGE": [42, 67, 58, 71, 36, 64, 69, 55, 62, 73, 48, 66],
    }
)

with Trace("T14_01", study="PROTO001") as trace:
    with trace.step("Read source data"):
        trace.read(
            "ADSL",
            source="analysis/adsl.parquet",
            rows=len(adsl),
            columns=len(adsl.columns),
        )

    with trace.step("Analysis population"):
        safety = adsl.loc[adsl["SAFFL"] == "Y"].copy()
        trace.filter(
            "ADSL",
            "SAFFL == 'Y'",
            before=len(adsl),
            after=len(safety),
        )

    with trace.step("Derive analysis variables"):
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

    with trace.step("Generate statistics"):
        summary = (
            safety.groupby(["TRT01A", "AGEGR1"], observed=False)
            .size()
            .reset_index(name="N")
        )
        trace.aggregate(
            "ADSL",
            by=["TRT01A", "AGEGR1"],
            result="demographics_summary",
            method="count",
            rows=len(summary),
        )

        expected = len(safety)
        observed = int(summary["N"].sum())
        trace.validate(
            "demographics_summary",
            "group counts sum to safety population",
            passed=observed == expected,
            metrics={"expected": expected, "observed": observed},
        )

    with trace.step("Write output"):
        path = OUTPUT_DIR / "demographics_table.csv"
        summary.to_csv(path, index=False)
        trace.output("T14_01", path, format="csv", rows=len(summary))
