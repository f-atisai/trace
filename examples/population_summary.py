"""Population-summary example using the public CDISC Pilot Study ADSL data.

Adapted from the PyCSR Quarto analysis ``analysis/tlf-02-population.qmd`` in
``elong0527/demo-py-esub``. This TRACE example is intentionally pure Python so
execution evidence is independent of the Quarto reporting wrapper.

PyCSR's example workflow is used as the analysis reference, but TRACE does not
use PyCSR's parquet-converted data. TRACE reads the original public CDISC Pilot
Study ``adsl.xpt`` dataset directly from the CDISC GitHub repository.

Sources:
- https://pycsr.org/tlf-population.html
- https://github.com/elong0527/demo-py-esub
- https://github.com/cdisc-org/sdtm-adam-pilot-project
"""

from pathlib import Path

import pandas as pd
import rtflite as rtf

from trace_tlf import Trace

DATA_DIR = Path("data")
OUTPUT_DIR = Path("example-output")
OUTPUT_DIR.mkdir(exist_ok=True)

ADSL_PATH = DATA_DIR / "adsl.xpt"
OUTPUT_PATH = OUTPUT_DIR / "tlf_population.rtf"


def load_xpt(path: Path) -> pd.DataFrame:
    """Read a SAS XPORT dataset into a pandas DataFrame."""
    return pd.read_sas(path, format="xport", encoding="utf-8")


def count_by_treatment(data: pd.DataFrame, population_name: str) -> pd.DataFrame:
    """Count participants by treatment and attach a population label."""
    counts = data.groupby("TRT01P", dropna=False).size().reset_index(name="n")
    counts["population"] = population_name
    return counts


def create_population_summary(adsl: pd.DataFrame) -> pd.DataFrame:
    """Reproduce the public PyCSR population-summary workflow."""
    populations = [count_by_treatment(adsl, "Participants in population")]

    for flag, label in (
        ("ITTFL", "Participants included in ITT population"),
        ("EFFFL", "Participants included in efficacy population"),
        ("SAFFL", "Participants included in safety population"),
    ):
        if flag in adsl.columns:
            population = adsl.loc[adsl[flag] == "Y"].copy()
            populations.append(count_by_treatment(population, label))

    return pd.concat(populations, ignore_index=True)


def format_population_table(
    pop_summary: pd.DataFrame,
    totals: pd.DataFrame,
) -> pd.DataFrame:
    """Format population counts and percentages as in the PyCSR example."""
    stats_with_pct = pop_summary.merge(totals, on="TRT01P", how="left")
    stats_with_pct["pct"] = (
        100.0 * stats_with_pct["n"] / stats_with_pct["total"]
    ).round(1)

    is_total = stats_with_pct["population"] == "Participants in population"
    stats_with_pct["display"] = stats_with_pct["n"].astype(str)
    stats_with_pct.loc[~is_total, "display"] = (
        stats_with_pct.loc[~is_total, "n"].astype(str)
        + " ("
        + stats_with_pct.loc[~is_total, "pct"].map(lambda value: f"{value:.1f}")
        + ")"
    )

    table = stats_with_pct.pivot(
        index="population",
        columns="TRT01P",
        values="display",
    ).reset_index()

    population_order = [
        "Participants in population",
        "Participants included in ITT population",
        "Participants included in efficacy population",
        "Participants included in safety population",
    ]
    table["population"] = pd.Categorical(
        table["population"], categories=population_order, ordered=True
    )
    table = table.sort_values("population").reset_index(drop=True)
    table["population"] = table["population"].astype(str)

    return table[
        [
            "population",
            "Placebo",
            "Xanomeline Low Dose",
            "Xanomeline High Dose",
        ]
    ]


with Trace("TLF_POPULATION", study="CDISC Pilot") as trace:
    with trace.step("Load ADSL"):
        adsl = load_xpt(ADSL_PATH)
        trace.read(
            "ADSL",
            source=str(ADSL_PATH),
            rows=len(adsl),
            columns=len(adsl.columns),
        )

    with trace.step("Summarize analysis populations"):
        totals = adsl.groupby("TRT01P", dropna=False).size().reset_index(name="total")

        for flag, result in (
            ("ITTFL", "ITT Population"),
            ("EFFFL", "Efficacy Population"),
            ("SAFFL", "Safety Population"),
        ):
            selected = adsl.loc[adsl[flag] == "Y"].copy()
            trace.filter(
                "ADSL",
                f"{flag} == 'Y'",
                result=result,
                before=len(adsl),
                after=len(selected),
            )

        pop_summary = create_population_summary(adsl)
        trace.aggregate(
            "ADSL",
            by=["TRT01P", "analysis population"],
            result="population_summary",
            method="participant count",
            rows=len(pop_summary),
        )

    with trace.step("Format population table"):
        df_overview = format_population_table(pop_summary, totals)
        trace.transform(
            "population_summary",
            "format counts and percentages and pivot treatment groups",
            result="population_table",
        )
        trace.validate(
            "population_table",
            "contains one row for each planned analysis-population display",
            passed=len(df_overview) == 4,
            metrics={"rows": len(df_overview)},
        )

    with trace.step("Write RTF output"):
        doc_overview = rtf.RTFDocument(
            df=df_overview,
            rtf_title=rtf.RTFTitle(
                text=["Analysis Population", "All Participants Randomized"]
            ),
            rtf_column_header=rtf.RTFColumnHeader(
                text=[
                    "",
                    "Placebo\nn (%)",
                    "Xanomeline Low Dose\nn (%)",
                    "Xanomeline High Dose\nn (%)",
                ],
                col_rel_width=[4, 2, 2, 2],
                text_justification=["l", "c", "c", "c"],
            ),
            rtf_body=rtf.RTFBody(
                col_rel_width=[4, 2, 2, 2],
                text_justification=["l", "c", "c", "c"],
            ),
            rtf_source=rtf.RTFSource(text=["Source: CDISC Pilot Study ADSL"]),
        )
        doc_overview.write_rtf(OUTPUT_PATH)
        trace.output("TLF_POPULATION", OUTPUT_PATH, format="rtf", rows=len(df_overview))
