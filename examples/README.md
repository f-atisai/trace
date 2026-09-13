# TRACE Statistical Programming Examples

These three examples use the publicly available CDISC Pilot Study ADaM datasets and recognizable clinical-reporting workflows. They show the path from statistical program to TRACE execution evidence to output without making TRACE the center of the program.

| Example | Statistical-programming problem | Primary TRACE review value |
|---|---|---|
| [`population_summary.py`](population_summary.py) | Analysis-population summary | population attrition, treatment summaries, output validation |
| [`specific_adverse_events.py`](specific_adverse_events.py) | AEs by SOC and preferred term | safety-set selection, merge cardinality, subject incidence |
| [`kaplan_meier_survival.py`](kaplan_meier_survival.py) | Kaplan-Meier overall-survival figure | endpoint selection, censoring convention, method, curve validation |

The population and adverse-event programs are pure-Python adaptations of analyses published in *Python for Clinical Study Reports and Submission* (PyCSR). Their original programs are Quarto documents. TRACE removes the Quarto wrapper here so the examples demonstrate that execution evidence is independent of the authoring environment.

PyCSR converts the CDISC Pilot Study data to parquet for its demonstration repository. TRACE instead downloads and reads the original CDISC ADaM XPORT (`.xpt`) datasets directly from the CDISC GitHub repository. PyCSR is therefore the analysis-workflow reference for the first two examples, while CDISC is the authoritative data source for all three.

The Kaplan-Meier example uses `lifelines.KaplanMeierFitter` for non-parametric survival estimation.

## Run the examples

Install TRACE with the example-only dependencies. These packages are intentionally not TRACE Core runtime dependencies:

```bash
python -m pip install -e ".[examples]"
```

Download `adsl.xpt`, `adae.xpt`, and `adtte.xpt` from the public CDISC Pilot Study repository:

```bash
python examples/fetch_example_data.py
```

Then run any example from the repository root:

```bash
python examples/population_summary.py
python examples/specific_adverse_events.py
python examples/kaplan_meier_survival.py
```

Generated RTF and PNG artifacts are written to `example-output/`. Downloaded data and generated outputs are ignored by Git.

## Sources

CDISC Pilot Study data:
- Repository: https://github.com/cdisc-org/sdtm-adam-pilot-project
- ADaM datasets: https://github.com/cdisc-org/sdtm-adam-pilot-project/tree/master/updated-pilot-submission-package/900172/m5/datasets/cdiscpilot01/analysis/adam/datasets

Population example:
- PyCSR chapter: https://pycsr.org/tlf-population.html
- Quarto source: https://github.com/elong0527/demo-py-esub/blob/main/analysis/tlf-02-population.qmd
- Population helper: https://github.com/elong0527/demo-py-esub/blob/main/src/demo001/population.py

Specific adverse-events example:
- PyCSR chapter: https://pycsr.org/tlf-ae-specific.html
- Quarto source: https://github.com/elong0527/demo-py-esub/blob/main/analysis/tlf-06-specific.qmd
- Safety helper: https://github.com/elong0527/demo-py-esub/blob/main/src/demo001/safety.py

Kaplan-Meier example:
- CDISC ADTTE input: https://github.com/cdisc-org/sdtm-adam-pilot-project/tree/master/updated-pilot-submission-package/900172/m5/datasets/cdiscpilot01/analysis/adam/datasets
- lifelines `KaplanMeierFitter`: https://lifelines.readthedocs.io/en/stable/fitters/univariate/KaplanMeierFitter.html
- lifelines quickstart: https://lifelines.readthedocs.io/en/stable/Quickstart.html

## What a reviewer should see

Across the examples, TRACE answers a compact set of execution questions: what data entered the program, what analysis set was selected, where counts changed, how datasets were combined, what summary or statistical method ran, which expectations were explicitly validated, and what artifact was written. The program, specification, and output remain necessary for judging statistical correctness.

The examples are also an API stress test. Awkwardness found while instrumenting these realistic programs is release feedback; it is not a reason to add new TRACE abstractions automatically.
