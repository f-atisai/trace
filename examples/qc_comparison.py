from pathlib import Path

import pandas as pd

from trace_tlf import Trace

OUTPUT_DIR = Path("example-output")
OUTPUT_DIR.mkdir(exist_ok=True)

production = pd.DataFrame(
    {
        "TRT01A": ["Placebo", "Drug A"],
        "N": [24, 27],
        "MEAN_AGE": [58.4, 60.1],
    }
)

qc = pd.DataFrame(
    {
        "TRT01A": ["Placebo", "Drug A"],
        "N": [24, 27],
        "MEAN_AGE": [58.4, 60.1],
    }
)

with Trace("QC_T14_01", study="PROTO001") as trace:
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

    trace.check(
        "T14_01_PRODUCTION",
        "row count observed",
        metrics={"rows": len(production)},
    )
    trace.check(
        "T14_01_QC",
        "row count observed",
        metrics={"rows": len(qc)},
    )

    trace.validate(
        "T14_01",
        "production and QC outputs have the same dimensions",
        passed=production.shape == qc.shape,
        metrics={
            "production_rows": len(production),
            "qc_rows": len(qc),
        },
    )

    comparison = production.merge(
        qc,
        on="TRT01A",
        suffixes=("_PROD", "_QC"),
        how="outer",
        indicator=True,
    )

    values_match = (
        (comparison["_merge"] == "both")
        & comparison["N_PROD"].eq(comparison["N_QC"])
        & comparison["MEAN_AGE_PROD"].eq(comparison["MEAN_AGE_QC"])
    ).all()

    trace.validate(
        "T14_01",
        "production and QC values match",
        passed=bool(values_match),
        metrics={"compared_rows": len(comparison)},
    )

    path = OUTPUT_DIR / "qc_comparison.csv"
    comparison.to_csv(path, index=False)
    trace.output("QC_T14_01", path, format="csv", rows=len(comparison))
