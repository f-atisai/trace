"""Treatment-emergent adverse-event summary by SOC, PT, and treatment.

Representative TRACE output:
    INFO [READ] [ADSL] loaded – rows=8, columns=3
    INFO [FILTER] [ADSL] SAFFL == 'Y' applied – N=8 → 7
    INFO [READ] [ADAE] loaded – rows=12, columns=4
    INFO [FILTER] [ADAE] TRTEMFL == 'Y' applied – N=12 → 10
    INFO [MERGE] [ADAE + ADSL] merged – left_rows=10, right_rows=7, result_rows=9
    INFO [AGGREGATE] [TEAE_SAFETY] aggregated – by=TRT01A, AEBODSYS, AEDECOD
    INFO [VALIDATE] [ae_summary] expected treatment groups present – PASS
    INFO [OUTPUT] [T14_03] written – example-output/adverse_events_table.csv

Reviewer interpretation:
    The merge is deliberately important: 10 treatment-emergent AE records become
    9 analysis records because one event belongs to a participant outside the Safety
    Population. A reviewer can investigate that contraction rather than assuming the
    merge was neutral. The final summary counts distinct participants by treatment,
    SOC, and preferred term.
"""

from pathlib import Path

import pandas as pd

from trace_tlf import Trace

OUTPUT_DIR = Path("example-output")
OUTPUT_DIR.mkdir(exist_ok=True)

adsl = pd.DataFrame(
    {
        "USUBJID": [f"STUDY01-{i:03d}" for i in range(1, 9)],
        "SAFFL": ["Y", "Y", "Y", "N", "Y", "Y", "Y", "Y"],
        "TRT01A": ["Placebo"] * 4 + ["Drug A 100 mg"] * 4,
    }
)

adae = pd.DataFrame(
    {
        "USUBJID": [
            "STUDY01-001",
            "STUDY01-001",
            "STUDY01-002",
            "STUDY01-003",
            "STUDY01-004",
            "STUDY01-005",
            "STUDY01-005",
            "STUDY01-006",
            "STUDY01-006",
            "STUDY01-007",
            "STUDY01-008",
            "STUDY01-008",
        ],
        "TRTEMFL": ["Y", "Y", "N", "Y", "Y", "Y", "Y", "Y", "N", "Y", "Y", "Y"],
        "AEBODSYS": [
            "Gastrointestinal disorders",
            "Nervous system disorders",
            "Nervous system disorders",
            "Gastrointestinal disorders",
            "Infections and infestations",
            "Nervous system disorders",
            "Gastrointestinal disorders",
            "Nervous system disorders",
            "Gastrointestinal disorders",
            "Infections and infestations",
            "Nervous system disorders",
            "Nervous system disorders",
        ],
        "AEDECOD": [
            "Nausea",
            "Headache",
            "Dizziness",
            "Nausea",
            "Nasopharyngitis",
            "Headache",
            "Nausea",
            "Dizziness",
            "Diarrhoea",
            "Nasopharyngitis",
            "Headache",
            "Dizziness",
        ],
    }
)

with Trace("T14_03", study="STUDY01") as trace:
    with trace.step("Safety Population"):
        trace.read(
            "ADSL",
            source="analysis/adsl.parquet",
            rows=len(adsl),
            columns=len(adsl.columns),
        )
        safety = adsl.loc[adsl["SAFFL"] == "Y", ["USUBJID", "TRT01A"]].copy()
        trace.filter(
            "ADSL",
            "SAFFL == 'Y'",
            result="Safety Population",
            before=len(adsl),
            after=len(safety),
        )

    with trace.step("Treatment-emergent adverse events"):
        trace.read(
            "ADAE",
            source="analysis/adae.parquet",
            rows=len(adae),
            columns=len(adae.columns),
        )
        teae = adae.loc[adae["TRTEMFL"] == "Y"].copy()
        trace.filter(
            "ADAE",
            "TRTEMFL == 'Y'",
            result="TEAE",
            before=len(adae),
            after=len(teae),
        )

    with trace.step("Apply treatment and population"):
        merged = teae.merge(
            safety,
            on="USUBJID",
            how="inner",
            validate="many_to_one",
        )
        unmatched_subjects = int(
            teae.loc[
                ~teae["USUBJID"].isin(safety["USUBJID"]), "USUBJID"
            ].nunique()
        )
        trace.merge(
            "ADAE",
            "ADSL",
            on="USUBJID",
            how="inner",
            result="TEAE_SAFETY",
            left_rows=len(teae),
            right_rows=len(safety),
            result_rows=len(merged),
            metrics={
                "matched_subjects": int(merged["USUBJID"].nunique()),
                "unmatched_subjects": unmatched_subjects,
            },
        )

    with trace.step("Summarize participant incidence"):
        summary = (
            merged.groupby(["TRT01A", "AEBODSYS", "AEDECOD"])["USUBJID"]
            .nunique()
            .reset_index(name="N")
        )
        trace.aggregate(
            "TEAE_SAFETY",
            by=["TRT01A", "AEBODSYS", "AEDECOD"],
            result="ae_summary",
            method="distinct subjects",
            rows=len(summary),
        )

        expected_treatments = {"Placebo", "Drug A 100 mg"}
        observed_treatments = set(merged["TRT01A"].dropna().unique())
        trace.validate(
            "ae_summary",
            "expected treatment groups present",
            passed=observed_treatments == expected_treatments,
            metrics={"treatment_groups": len(observed_treatments)},
        )

    path = OUTPUT_DIR / "adverse_events_table.csv"
    summary.to_csv(path, index=False)
    trace.output("T14_03", path, format="csv", rows=len(summary))
