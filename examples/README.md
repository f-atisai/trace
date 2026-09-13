# TRACE Statistical Programming Examples

The release examples use publicly available CDISC Pilot Study ADaM datasets and recognizable clinical-reporting workflows. They show the path from statistical program to TRACE execution evidence to an output artifact without making TRACE the center of the program.

| Example | Statistical-programming problem | Primary TRACE review value |
|---|---|---|
| [`population_summary.py`](population_summary.py) | Analysis-population summary | population attrition, treatment summaries, output validation |
| [`specific_adverse_events.py`](specific_adverse_events.py) | AEs by SOC and preferred term | safety-set selection, merge cardinality, subject incidence |

Both programs are pure-Python adaptations of analyses published in *Python for Clinical Study Reports and Submission* (PyCSR). Their original programs are Quarto documents. TRACE removes the Quarto wrapper so the examples demonstrate that execution evidence is independent of the authoring environment.

**Data-source note:** TRACE uses PyCSR's examples as references for the analysis workflows, but it does **not** use the parquet datasets from the PyCSR demonstration repository. PyCSR converted the CDISC Pilot Study data to parquet for its project. These TRACE examples instead download and read the original CDISC Pilot Study ADaM datasets directly from the CDISC GitHub repository in SAS XPORT (`.xpt`) format. PyCSR is therefore the analysis-workflow reference; CDISC is the authoritative data source.

## Run the examples

Install TRACE with the example-only dependencies. These packages are intentionally not TRACE Core runtime dependencies:

```bash
python -m pip install -e ".[examples]"
```

The example dependency set is deliberately small: pandas reads and processes the original XPT datasets, while `rtflite` produces the RTF output artifacts.

Download `adsl.xpt` and `adae.xpt` from the public CDISC Pilot Study repository:

```bash
python examples/fetch_example_data.py
```

Then run either example from the repository root:

```bash
python examples/population_summary.py
python examples/specific_adverse_events.py
```

The generated RTF artifacts are written to `example-output/`. Downloaded data and generated outputs are ignored by Git.

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

## What a reviewer should see

Across the examples, TRACE answers a compact set of execution questions: what data entered the program, what analysis set was selected, where counts changed, how datasets were combined, which expectations were explicitly validated, and what artifact was written. The program, specification, and output remain necessary for judging statistical correctness.

The examples are also an API stress test. Awkwardness found while instrumenting these realistic programs is release feedback; it is not a reason to add new TRACE abstractions automatically.
