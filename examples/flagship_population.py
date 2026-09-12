"""Flagship population-summary example using public PyCSR clinical data.

Adapted from the PyCSR Quarto analysis ``analysis/tlf-02-population.qmd`` in
``elong0527/demo-py-esub``. This TRACE example is deliberately presented as a
pure Python program rather than a Quarto document so the execution evidence is
visible independently of the reporting wrapper.

Source material:
- https://pycsr.org/tlf-population.html
- https://github.com/elong0527/demo-py-esub

The example expects ``data/adsl.parquet`` from the public demo-py-esub project.
"""

from pathlib import Path

import polars as pl
import rtflite as rtf

from trace_tlf import Trace

DATA_DIR = Path("data")
OUTPUT_DIR = Path("example-output")
OUTPUT_DIR.mkdir(exist_ok=True)

ADSL_PATH = DATA_DIR / "adsl.parquet"
OUTPUT_PATH = OUTPUT_DIR / "tlf_population.rtf"


def count_by_treatment(data: pl.DataFrame, population_name: str) -> pl.DataFrame:
    """Count participants by treatment and attach a population label."""
    return (
        data.group_by("TRT01P")
        .agg(n=pl.len())
        .with_columns(population=pl.lit(population_name))
    )


def create_population_summary(adsl: pl.DataFrame) -> pl.DataFrame:
    """Reproduce the public PyCSR population-summary helper logic."""
    populations = [count_by_treatment(adsl, "Participants in population")]

    for flag, label in (
        ("ITTFL", "Participants included in ITT population"),
        ("EFFFL", "Participants included in efficacy population"),
        ("SAFFL", "Participants included in safety population"),
    ):
        if flag in adsl.columns:
            population = adsl.filter(pl.col(flag) == "Y")
            populations.append(count_by_treatment(population, label))

    return pl.concat(populations, how="diagonal")


def format_population_table(
    pop_summary: pl.DataFrame,
    totals: pl.DataFrame,
) -> pl.DataFrame:
    """Format population counts and percentages as in the PyCSR example."""
    stats_with_pct = pop_summary.join(totals, on="TRT01P").with_columns(
        pct=(100.0 * pl.col("n") / pl.col("total")).round(1)
    )

    formatted_stats = stats_with_pct.with_columns(
        display=pl.when(pl.col("population") == "Participants in population")
        .then(pl.col("n").cast(str))
        .otherwise(
            pl.concat_str(
                [
                    pl.col("n").cast(str),
                    pl.lit(" ("),
                    pl.col("pct").round(1).cast(str),
                    pl.lit(")"),
                ]
            )
        )
    )

    return formatted_stats.pivot(
        values="display",
        index="population",
        on="TRT01P",
        maintain_order=True,
    ).select(
        [
            "population",
            "Placebo",
            "Xanomeline Low Dose",
            "Xanomeline High Dose",
        ]
    )


with Trace("TLF_POPULATION", study="CDISC Pilot") as trace:
    with trace.step("Load ADSL"):
        adsl = pl.read_parquet(ADSL_PATH)
        trace.read(
            "ADSL",
            source=str(ADSL_PATH),
            rows=adsl.height,
            columns=adsl.width,
        )

    with trace.step("Summarize analysis populations"):
        totals = adsl.group_by("TRT01P").agg(total=pl.len())

        for flag, result in (
            ("ITTFL", "ITT Population"),
            ("EFFFL", "Efficacy Population"),
            ("SAFFL", "Safety Population"),
        ):
            selected = adsl.filter(pl.col(flag) == "Y")
            trace.filter(
                "ADSL",
                f"{flag} == 'Y'",
                result=result,
                before=adsl.height,
                after=selected.height,
            )

        pop_summary = create_population_summary(adsl)
        trace.aggregate(
            "ADSL",
            by=["TRT01P", "analysis population"],
            result="population_summary",
            method="participant count",
            rows=pop_summary.height,
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
            passed=df_overview.height == 4,
            metrics={"rows": df_overview.height},
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
            rtf_source=rtf.RTFSource(text=["Source: public PyCSR ADSL dataset"]),
        )
        doc_overview.write_rtf(OUTPUT_PATH)
        trace.output("TLF_POPULATION", OUTPUT_PATH, format="rtf", rows=df_overview.height)
