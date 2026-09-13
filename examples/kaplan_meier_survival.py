"""Kaplan-Meier overall-survival example using public CDISC Pilot Study ADTTE.

TRACE reads the original public CDISC ``adtte.xpt`` dataset directly. The
analysis uses lifelines' KaplanMeierFitter for non-parametric survival
estimation and is independent of the PyCSR Quarto examples.

Sources:
- https://github.com/cdisc-org/sdtm-adam-pilot-project
- https://lifelines.readthedocs.io/en/stable/fitters/univariate/KaplanMeierFitter.html
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import polars as pl
from lifelines import KaplanMeierFitter

from trace_tlf import Trace

DATA_DIR = Path("data")
OUTPUT_DIR = Path("example-output")
OUTPUT_DIR.mkdir(exist_ok=True)

ADTTE_PATH = DATA_DIR / "adtte.xpt"
OUTPUT_PATH = OUTPUT_DIR / "kaplan_meier_overall_survival.png"


def load_xpt(path: Path) -> pl.DataFrame:
    """Read a SAS XPORT dataset and return a Polars DataFrame."""
    return pl.from_pandas(pd.read_sas(path, format="xport", encoding="utf-8"))


with Trace("FIGURE_OS_KM", study="CDISC Pilot") as trace:
    with trace.step("Load ADTTE"):
        adtte = load_xpt(ADTTE_PATH)
        trace.read(
            "ADTTE",
            source=str(ADTTE_PATH),
            rows=adtte.height,
            columns=adtte.width,
        )

    with trace.step("Select overall-survival records"):
        parameter_column = "PARAMCD" if "PARAMCD" in adtte.columns else "PARAM"
        parameter_values = adtte[parameter_column].unique().to_list()
        os_value = next(
            (
                value
                for value in parameter_values
                if str(value).upper() == "OS"
                or "OVERALL SURVIVAL" in str(value).upper()
            ),
            None,
        )
        if os_value is None:
            raise ValueError("ADTTE does not contain an overall-survival parameter")

        os_data = adtte.filter(pl.col(parameter_column) == os_value)
        trace.filter(
            "ADTTE",
            f"{parameter_column} == {os_value!r}",
            result="Overall Survival Analysis Set",
            before=adtte.height,
            after=os_data.height,
        )

        trace.validate(
            "Overall Survival Analysis Set",
            "contains non-missing analysis times and censoring indicators",
            passed=(
                os_data.height > 0
                and os_data["AVAL"].null_count() == 0
                and os_data["CNSR"].null_count() == 0
            ),
            metrics={"rows": os_data.height},
        )

    with trace.step("Estimate Kaplan-Meier curves"):
        treatment_column = "TRT01A" if "TRT01A" in os_data.columns else "TRTA"
        kmf = KaplanMeierFitter()
        curve_frames: list[pl.DataFrame] = []

        figure, axis = plt.subplots()
        for treatment in os_data[treatment_column].unique().sort().to_list():
            group = os_data.filter(pl.col(treatment_column) == treatment)
            durations = group["AVAL"].to_numpy()
            event_observed = group["CNSR"].to_numpy() == 0

            kmf.fit(
                durations=durations,
                event_observed=event_observed,
                label=str(treatment),
            )
            kmf.plot_survival_function(ax=axis)

            survival = kmf.survival_function_.reset_index()
            survival.columns = ["timeline", "survival"]
            curve_frames.append(
                pl.from_pandas(survival).with_columns(
                    pl.lit(str(treatment)).alias("treatment")
                )
            )

        km_curves = pl.concat(curve_frames)
        trace.analyze(
            "Overall Survival Analysis Set",
            "Overall Survival",
            method="Kaplan-Meier",
            population="analysis records in CDISC Pilot ADTTE",
            result="km_survival_curves",
            details={
                "time": "AVAL",
                "censor": "CNSR",
                "event": "CNSR == 0",
                "strata": treatment_column,
            },
        )

        probabilities_valid = km_curves["survival"].is_between(0.0, 1.0).all()
        trace.validate(
            "km_survival_curves",
            "survival probabilities remain within [0, 1]",
            passed=bool(probabilities_valid),
            metrics={"curve_rows": km_curves.height},
        )

    with trace.step("Write survival figure"):
        axis.set_xlabel("Analysis time")
        axis.set_ylabel("Survival probability")
        axis.set_ylim(0.0, 1.0)
        figure.tight_layout()
        figure.savefig(OUTPUT_PATH)
        plt.close(figure)

        trace.output("FIGURE_OS_KM", OUTPUT_PATH, format="png")
