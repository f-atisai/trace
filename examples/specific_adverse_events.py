"""Specific-adverse-events example using public CDISC Pilot Study data.

Adapted from the PyCSR Quarto analysis ``analysis/tlf-06-specific.qmd`` in
``elong0527/demo-py-esub``. The Quarto wrapper is removed so this is a pure
Python program.

PyCSR's example workflow is used as the analysis reference, but TRACE does not
use PyCSR's parquet-converted data. TRACE reads the original public CDISC Pilot
Study ``adsl.xpt`` and ``adae.xpt`` datasets directly from the CDISC GitHub
repository.

Sources:
- https://pycsr.org/tlf-ae-specific.html
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
ADAE_PATH = DATA_DIR / "adae.xpt"
OUTPUT_PATH = OUTPUT_DIR / "tlf_ae_specific.rtf"
TREATMENTS = ["Placebo", "Xanomeline Low Dose", "Xanomeline High Dose"]


def load_xpt(path: Path) -> pd.DataFrame:
    """Read a SAS XPORT dataset into a pandas DataFrame."""
    return pd.read_sas(path, format="xport", encoding="utf-8")


def create_ae_by_soc_table(
    adae_safety: pd.DataFrame,
    pop_counts: pd.DataFrame,
    treatments: list[str],
) -> pd.DataFrame:
    """Reproduce the public PyCSR SOC/preferred-term table workflow."""
    analysis_data = adae_safety.copy()
    analysis_data["AEDECOD_STD"] = analysis_data["AEDECOD"].str.title()
    analysis_data["AEBODSYS_STD"] = analysis_data["AEBODSYS"].str.title()

    ae_counts = (
        analysis_data.groupby(
            ["TRT01A", "AEBODSYS_STD", "AEDECOD_STD"], dropna=False
        )["USUBJID"]
        .nunique()
        .reset_index(name="n")
        .sort_values(["AEBODSYS_STD", "AEDECOD_STD", "TRT01A"])
    )

    population_by_treatment = pop_counts.set_index("TRT01A")["N"].to_dict()
    table_data = [
        ["Participants in population"]
        + [str(population_by_treatment.get(treatment, 0)) for treatment in treatments],
        [""] * (len(treatments) + 1),
    ]

    for soc in sorted(ae_counts["AEBODSYS_STD"].dropna().unique()):
        table_data.append([soc] + [""] * len(treatments))
        soc_data = ae_counts.loc[ae_counts["AEBODSYS_STD"] == soc]

        for ae_term in sorted(soc_data["AEDECOD_STD"].dropna().unique()):
            row = [f"  {ae_term}"]
            for treatment in treatments:
                count_data = soc_data.loc[
                    (soc_data["AEDECOD_STD"] == ae_term)
                    & (soc_data["TRT01A"] == treatment),
                    "n",
                ]
                count = int(count_data.iloc[0]) if not count_data.empty else 0
                row.append(str(count))
            table_data.append(row)

    return pd.DataFrame(
        table_data,
        columns=["System Organ Class / Preferred Term", *treatments],
    )


with Trace("TLF_AE_SPECIFIC", study="CDISC Pilot") as trace:
    with trace.step("Load analysis data"):
        adsl = load_xpt(ADSL_PATH)
        trace.read(
            "ADSL",
            source=str(ADSL_PATH),
            rows=len(adsl),
            columns=len(adsl.columns),
        )

        adae = load_xpt(ADAE_PATH)
        trace.read(
            "ADAE",
            source=str(ADAE_PATH),
            rows=len(adae),
            columns=len(adae.columns),
        )

    with trace.step("Prepare safety population"):
        adsl_safety = adsl.loc[adsl["SAFFL"] == "Y", ["USUBJID", "TRT01A"]].copy()
        trace.filter(
            "ADSL",
            "SAFFL == 'Y'",
            result="Safety Population",
            before=len(adsl),
            after=len(adsl_safety),
        )

        pop_counts = (
            adsl_safety.groupby("TRT01A", dropna=False)
            .size()
            .reset_index(name="N")
            .sort_values("TRT01A")
        )
        trace.aggregate(
            "Safety Population",
            by=["TRT01A"],
            result="safety_population_counts",
            method="participant count",
            rows=len(pop_counts),
        )

        adae_safety = adae.merge(adsl_safety, on="USUBJID", how="inner")
        trace.merge(
            "ADAE",
            "Safety Population",
            on=["USUBJID"],
            how="inner",
            result="Safety ADAE",
            left_rows=len(adae),
            right_rows=len(adsl_safety),
            result_rows=len(adae_safety),
        )

    with trace.step("Summarize adverse events"):
        df_ae_specific = create_ae_by_soc_table(adae_safety, pop_counts, TREATMENTS)
        trace.aggregate(
            "Safety ADAE",
            by=["AEBODSYS", "AEDECOD", "TRT01A"],
            result="ae_soc_pt_table",
            method="unique participant incidence",
            rows=len(df_ae_specific),
        )
        trace.validate(
            "ae_soc_pt_table",
            "contains the population row and all treatment columns",
            passed=(
                len(df_ae_specific) > 0
                and all(treatment in df_ae_specific.columns for treatment in TREATMENTS)
            ),
            metrics={"rows": len(df_ae_specific)},
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
            rows=len(df_ae_specific),
        )
