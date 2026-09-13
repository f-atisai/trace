"""Specific-adverse-events example using public CDISC Pilot Study data.

Adapted from the PyCSR Quarto analysis ``analysis/tlf-06-specific.qmd`` in
``elong0527/demo-py-esub``. The Quarto wrapper is removed so this is a pure
Python program. TRACE reads the original CDISC ``adsl.xpt`` and ``adae.xpt``
rather than the parquet conversions used by PyCSR.

Sources:
- https://pycsr.org/tlf-ae-specific.html
- https://github.com/elong0527/demo-py-esub
- https://github.com/cdisc-org/sdtm-adam-pilot-project
"""

from pathlib import Path

import pandas as pd
import polars as pl
import rtflite as rtf

from trace_tlf import Trace

DATA_DIR = Path("data")
OUTPUT_DIR = Path("example-output")
OUTPUT_DIR.mkdir(exist_ok=True)

ADSL_PATH = DATA_DIR / "adsl.xpt"
ADAE_PATH = DATA_DIR / "adae.xpt"
OUTPUT_PATH = OUTPUT_DIR / "tlf_ae_specific.rtf"
TREATMENTS = ["Placebo", "Xanomeline Low Dose", "Xanomeline High Dose"]


def load_xpt(path: Path) -> pl.DataFrame:
    """Read a SAS XPORT dataset and return a Polars DataFrame."""
    return pl.from_pandas(pd.read_sas(path, format="xport", encoding="utf-8"))


def create_ae_by_soc_table(
    adae_safety: pl.DataFrame,
    pop_counts: pl.DataFrame,
    treatments: list[str],
) -> pl.DataFrame:
    """Reproduce the public PyCSR SOC/preferred-term table helper logic."""
    ae_counts = (
        adae_safety.with_columns(
            [
                pl.col("AEDECOD").str.to_titlecase().alias("AEDECOD_STD"),
                pl.col("AEBODSYS").str.to_titlecase().alias("AEBODSYS_STD"),
            ]
        )
        .group_by(["TRT01A", "AEBODSYS_STD", "AEDECOD_STD"])
        .agg(n=pl.col("USUBJID").n_unique())
        .sort(["AEBODSYS_STD", "AEDECOD_STD", "TRT01A"])
    )

    table_data = [
        ["Participants in population"]
        + [
            str(pop_counts.filter(pl.col("TRT01A") == treatment)["N"][0])
            for treatment in treatments
        ],
        [""] * (len(treatments) + 1),
    ]

    for soc in ae_counts["AEBODSYS_STD"].unique().sort():
        table_data.append([soc] + [""] * len(treatments))
        soc_data = ae_counts.filter(pl.col("AEBODSYS_STD") == soc)

        for ae_term in soc_data["AEDECOD_STD"].unique().sort():
            row = [f"  {ae_term}"]
            for treatment in treatments:
                count_data = soc_data.filter(
                    (pl.col("AEDECOD_STD") == ae_term)
                    & (pl.col("TRT01A") == treatment)
                )
                count = count_data["n"][0] if count_data.height > 0 else 0
                row.append(str(count))
            table_data.append(row)

    return pl.DataFrame(
        table_data,
        schema=["System Organ Class / Preferred Term"] + treatments,
        orient="row",
    )


with Trace("TLF_AE_SPECIFIC", study="CDISC Pilot") as trace:
    with trace.step("Load analysis data"):
        adsl = load_xpt(ADSL_PATH)
        trace.read(
            "ADSL", source=str(ADSL_PATH), rows=adsl.height, columns=adsl.width
        )

        adae = load_xpt(ADAE_PATH)
        trace.read(
            "ADAE", source=str(ADAE_PATH), rows=adae.height, columns=adae.width
        )

    with trace.step("Prepare safety population"):
        adsl_safety = adsl.filter(pl.col("SAFFL") == "Y").select(
            ["USUBJID", "TRT01A"]
        )
        trace.filter(
            "ADSL",
            "SAFFL == 'Y'",
            result="Safety Population",
            before=adsl.height,
            after=adsl_safety.height,
        )

        pop_counts = adsl_safety.group_by("TRT01A").agg(N=pl.len()).sort("TRT01A")
        trace.aggregate(
            "Safety Population",
            by=["TRT01A"],
            result="safety_population_counts",
            method="participant count",
            rows=pop_counts.height,
        )

        adae_safety = adae.join(adsl_safety, on="USUBJID", how="inner")
        trace.merge(
            "ADAE",
            "Safety Population",
            on=["USUBJID"],
            how="inner",
            result="Safety ADAE",
            left_rows=adae.height,
            right_rows=adsl_safety.height,
            result_rows=adae_safety.height,
        )

    with trace.step("Summarize adverse events"):
        df_ae_specific = create_ae_by_soc_table(adae_safety, pop_counts, TREATMENTS)
        trace.aggregate(
            "Safety ADAE",
            by=["AEBODSYS", "AEDECOD", "TRT01A"],
            result="ae_soc_pt_table",
            method="unique participant incidence",
            rows=df_ae_specific.height,
        )
        trace.validate(
            "ae_soc_pt_table",
            "contains the population row and all treatment columns",
            passed=(
                df_ae_specific.height > 0
                and all(treatment in df_ae_specific.columns for treatment in TREATMENTS)
            ),
            metrics={"rows": df_ae_specific.height},
        )

    with trace.step("Write RTF output"):
        doc = rtf.RTFDocument(
            df=df_ae_specific,
            rtf_title=rtf.RTFTitle(
                text=[
                    "Adverse Events by System Organ Class and Preferred Term",
                    "(Safety Analysis Set)",
                ]
            ),
            rtf_column_header=rtf.RTFColumnHeader(
                text=[
                    "System Organ Class\\line   Preferred Term",
                    "Placebo",
                    "Xanomeline Low Dose",
                    "Xanomeline High Dose",
                ],
                col_rel_width=[4, 1.5, 1.5, 1.5],
                text_justification=["l", "c", "c", "c"],
                text_format="b",
                border_bottom="single",
            ),
            rtf_body=rtf.RTFBody(
                col_rel_width=[4, 1.5, 1.5, 1.5],
                text_justification=["l", "c", "c", "c"],
            ),
            rtf_footnote=rtf.RTFFootnote(
                text=[
                    "Each participant is counted once within each preferred term "
                    "and system organ class."
                ]
            ),
            rtf_source=rtf.RTFSource(text=["Source: CDISC Pilot Study ADAE"]),
        )
        doc.write_rtf(OUTPUT_PATH)
        trace.output(
            "TLF_AE_SPECIFIC",
            OUTPUT_PATH,
            format="rtf",
            rows=df_ae_specific.height,
        )
