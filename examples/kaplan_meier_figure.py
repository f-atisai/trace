from pathlib import Path

import pandas as pd

from trace_tlf import Trace

OUTPUT_DIR = Path("example-output")
OUTPUT_DIR.mkdir(exist_ok=True)

adtte = pd.DataFrame(
    {
        "USUBJID": [f"SUBJ{i:03d}" for i in range(1, 11)],
        "ITTFL": ["Y", "Y", "Y", "N", "Y", "Y", "Y", "Y", "Y", "Y"],
        "TRT01A": ["Placebo"] * 5 + ["Drug A"] * 5,
        "AVAL": [4, 6, 8, 10, 12, 5, 7, 9, 11, 14],
        "CNSR": [0, 1, 0, 0, 1, 0, 0, 1, 0, 1],
    }
)


def kaplan_meier(data: pd.DataFrame) -> pd.DataFrame:
    rows = []
    survival = 1.0

    for time in sorted(data["AVAL"].unique()):
        at_risk = int((data["AVAL"] >= time).sum())
        events = int(((data["AVAL"] == time) & (data["CNSR"] == 0)).sum())

        if at_risk and events:
            survival *= 1 - events / at_risk

        rows.append(
            {
                "time": int(time),
                "at_risk": at_risk,
                "events": events,
                "survival": survival,
            }
        )

    return pd.DataFrame(rows)


with Trace("F14_01", study="PROTO001") as trace:
    trace.read("ADTTE", rows=len(adtte), columns=len(adtte.columns))

    itt = adtte.loc[adtte["ITTFL"] == "Y"].copy()
    trace.filter("ADTTE", "ITTFL == 'Y'", before=len(adtte), after=len(itt))

    curves = []
    for treatment, group in itt.groupby("TRT01A"):
        curve = kaplan_meier(group)
        curve["TRT01A"] = treatment
        curves.append(curve)

    km = pd.concat(curves, ignore_index=True)

    trace.analyze(
        "Overall survival",
        method="Kaplan-Meier",
        population="ITT",
        result="km_curve",
        details={
            "time_variable": "AVAL",
            "censor_variable": "CNSR",
            "strata": "TRT01A",
        },
    )

    trace.validate(
        "km_curve",
        "survival probabilities remain within [0, 1]",
        passed=bool(km["survival"].between(0, 1).all()),
        metrics={"rows": len(km)},
    )

    path = OUTPUT_DIR / "kaplan_meier_curve.csv"
    km.to_csv(path, index=False)
    trace.output("F14_01", path, format="csv", rows=len(km))
