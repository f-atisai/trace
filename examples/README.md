# TRACE Statistical Programming Examples

The three flagship examples use publicly available clinical/statistical data and recognizable reporting workflows. Their purpose is to show the complete path from statistical program to TRACE execution evidence to output without making TRACE the center of the program.

## Flagship examples

| Example | Statistical-programming problem | Primary TRACE review value |
|---|---|---|
| [`flagship_population.py`](flagship_population.py) | Analysis-population summary | population attrition, treatment summaries, output validation |
| [`flagship_specific_adverse_events.py`](flagship_specific_adverse_events.py) | AEs by SOC and preferred term | safety-set selection, merge cardinality, subject incidence |
| [`flagship_kaplan_meier.py`](flagship_kaplan_meier.py) | Kaplan-Meier overall-survival figure | endpoint selection, censoring convention, method, curve validation |

The first two programs are pure-Python adaptations of analyses published in *Python for Clinical Study Reports and Submission* (PyCSR). The original programs are Quarto documents. TRACE deliberately removes the Quarto wrapper here so the examples demonstrate that TRACE execution evidence is independent of the authoring environment.

The Kaplan-Meier example uses the public ADTTE dataset in the same `demo-py-esub` repository and `lifelines.KaplanMeierFitter`. CDISC's public pancreatic-cancer ADTTE example is referenced for the ADaM time-to-event conventions: `AVAL` is analysis duration, `PARAMCD="OS"` identifies Overall Survival, and `CNSR=0` identifies the event while `CNSR=1` identifies censoring.

## Run the flagship examples

Install TRACE with the example-only dependencies. These packages are intentionally not TRACE Core runtime dependencies:

```bash
python -m pip install -e ".[examples]"
```

Download the public parquet inputs from `elong0527/demo-py-esub`:

```bash
python examples/fetch_flagship_data.py
```

Then run any example from the repository root:

```bash
python examples/flagship_population.py
python examples/flagship_specific_adverse_events.py
python examples/flagship_kaplan_meier.py
```

Generated RTF and PNG artifacts are written to `example-output/`. Downloaded data and generated outputs are ignored by Git.

## Sources

Population example:
- PyCSR chapter: https://pycsr.org/tlf-population.html
- Quarto source: https://github.com/elong0527/demo-py-esub/blob/main/analysis/tlf-02-population.qmd
- Population helper: https://github.com/elong0527/demo-py-esub/blob/main/src/demo001/population.py
- Dataset loader used by the original project: https://github.com/elong0527/demo-py-esub/blob/main/src/demo001/utils.py

Specific adverse-events example:
- PyCSR chapter: https://pycsr.org/tlf-ae-specific.html
- Quarto source: https://github.com/elong0527/demo-py-esub/blob/main/analysis/tlf-06-specific.qmd
- Safety helper: https://github.com/elong0527/demo-py-esub/blob/main/src/demo001/safety.py

Kaplan-Meier example:
- Public ADTTE input: https://github.com/elong0527/demo-py-esub/blob/main/data/adtte.parquet
- CDISC ADTTE time-to-event example: https://www.cdisc.org/kb/examples/pancreatic-cancer-adtte-survival-and-duration-follow-103759150
- lifelines `KaplanMeierFitter`: https://lifelines.readthedocs.io/en/stable/fitters/univariate/KaplanMeierFitter.html
- lifelines multiple-group Kaplan-Meier quickstart: https://lifelines.readthedocs.io/en/stable/Quickstart.html

The public PyCSR data files used here are `adsl.parquet`, `adae.parquet`, and `adtte.parquet` from the `data/` directory of `demo-py-esub`.

## What a reviewer should see

Across the examples, TRACE answers a compact set of execution questions: what data entered the program, what analysis set was selected, where counts changed, how datasets were combined, what summary or statistical method ran, which expectations were explicitly validated, and what artifact was written. The program, specification, and output remain necessary for judging statistical correctness.

The examples are also an API stress test. Awkwardness found while instrumenting these realistic programs is release feedback; it is not a reason to add new TRACE abstractions automatically.

## Earlier synthetic examples

The repository still contains the earlier small synthetic examples used during API design:

- `demographics_table.py`
- `adverse_events_table.py`
- `subject_listing.py`
- `kaplan_meier_figure.py`
- `adam_derivation.py`
- `qc_comparison.py`

They remain useful as compact development fixtures, but the public-data flagship programs above are the examples intended to represent the developer preview.
