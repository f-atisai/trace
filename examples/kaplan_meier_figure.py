"""Kaplan-Meier figure for Overall Survival in the ITT Population.

Representative TRACE output:
    INFO [READ] [ADTTE] loaded – rows=12, columns=6
    INFO [FILTER] [ADTTE] PARAMCD == 'OS' and ITTFL == 'Y' applied – N=12 → 11
    INFO [SORT] [ADTTE] sorted – by=TRT01A, AVAL
    INFO [ANALYZE] [Overall Survival] analyzed – method=Kaplan-Meier, population=ITT
    INFO [VALIDATE] [km_curve] survival probabilities remain within [0, 1] – PASS
    INFO [OUTPUT] [F14_01] written – example-output/kaplan_meier_figure.png

Reviewer interpretation:
    Confirm that the OS parameter and ITT Population were used, AVAL is the
    time-to-event value, CNSR is the censoring indicator, treatment groups were
    analysed separately, and the resulting survival estimates passed basic bounds
    validation. TRACE records that Kaplan-Meier was executed; it does not validate
    the statistical implementation of this compact demonstration estimator.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from trace_tlf import Trace

OUTPUT_DIR = Path("example-output")
OUTPUT_DIR.mkdir(exist_ok=True)

adtte = pd.DataFrame(
    {
        "USUBJID": [f"STUDY01-{i:03d}" for i in range(1, 13)],
        "PARAMCD": ["OS"] * 12,
        "ITTFL": ["Y", "Y", "Y", "N", "Y", "Y", "Y", "Y", "Y", "Y", "Y", "Y"],
        "TRT01A": ["Placebo"] * 6 + ["Drug A 100 mg"] * 6,
        "AVAL": [120, 180, 240, 300, 365, 420, 140, 210, 280, 350, 410, 450],
        "CNSR": [0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0],
    }
)


def kaplan_meier(data: pd.DataFrame) -> pd.DataFrame:
    """Return a compact Kaplan-Meier curve for demonstration purposes."""
    rows = []
    survival = 1.0

    for time in sorted(data["AVAL"].unique()):
        at_risk = int((data["AVAL"] >= time).sum())
        events = int(((data["AVAL"] == time) & (data["CNSR"] == 0)).sum())
        if at_risk and events:
            survival *= 1 - events / at_risk
        rows.append(
            {
                "AVAL": int(time),
                "ATRISK": at_risk,
                "EVENTS": events,
                "SURVIVAL": survival,
            }
        )

    return pd.DataFrame(rows)


with Trace("F14_01", study="STUDY01") as trace:
    trace.read(
        "ADTTE",
        source="analysis/adtte.parquet",
        rows=len(adtte),
        columns=len(adtte.columns),
    )

    os_itt = adtte.loc[(adtte["PARAMCD"] == "OS") & (adtte["ITTFL"] == "Y")].copy()
    trace.filter(
        "ADTTE",
        "PARAMCD == 'OS' and ITTFL == 'Y'",
        before=len(adtte),
        after=len(os_itt),
    )

    os_itt = os_itt.sort_values(["TRT01A", "AVAL"])
    trace.sort("ADTTE", by=["TRT01A", "AVAL"])

    curves = []
    for treatment, group in os_itt.groupby("TRT01A"):
        curve = kaplan_meier(group)
        curve["TRT01A"] = treatment
        curves.append(curve)
    km = pd.concat(curves, ignore_index=True)

    trace.analyze(
        "ADTTE",
        "Overall Survival",
        method="Kaplan-Meier",
        population="ITT",
        result="km_curve",
        details={"time": "AVAL", "censor": "CNSR", "strata": "TRT01A"},
    )

    trace.validate(
        "km_curve",
        "survival probabilities remain within [0, 1]",
        passed=bool(km["SURVIVAL"].between(0, 1).all()),
        metrics={"curve_rows": len(km)},
    )

    figure_path = OUTPUT_DIR / "kaplan_meier_figure.png"
    for treatment, curve in km.groupby("TRT01A"):
        plt.step(curve["AVAL"], curve["SURVIVAL"], where="post", label=treatment)
    plt.xlabel("Days")
    plt.ylabel("Survival probability")
    plt.legend()
    plt.tight_layout()
    plt.savefig(figure_path)
    plt.close()

    trace.output("F14_01", figure_path, format="png")
