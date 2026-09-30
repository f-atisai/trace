# TRACE Statistical Programming Examples

These examples show TRACE inside progressively more realistic statistical-programming workflows. The statistical code remains primary; TRACE records the important operations around it.

## Example progression

| Example | Workflow | TRACE concepts demonstrated |
|---|---|---|
| [`basic_analysis_workflow.py`](basic_analysis_workflow.py) | Small safety-population extract | `READ`, `FILTER`, `DERIVE`, `OUTPUT`, finalized run log |
| [`population_summary.py`](population_summary.py) | Analysis-population summary | analysis-set selection, aggregation, validation, `STEP`, RTF output, provenance |
| [`specific_adverse_events.py`](specific_adverse_events.py) | AEs by SOC and preferred term | multiple inputs, safety-set selection, merge diagnostics, aggregation, validation, `STEP`, RTF output, provenance |

The progression is intentional: start with the TRACE pattern, then see how the same vocabulary scales into familiar TLF workflows.

## 1. Basic analysis workflow

`basic_analysis_workflow.py` uses a small in-memory ADSL-like dataset. It is the quickest executable example of the core pattern:

```text
statistical code performs the work
             ↓
TRACE records the meaningful operation nearby
```

The program:

1. records ADSL as the working input;
2. selects the safety population;
3. derives an age group;
4. writes a CSV output; and
5. finalizes a TRACE log in `example-output/basic_analysis_workflow.log`.

Run it with:

```bash
python -m pip install -e ".[examples]"
python examples/basic_analysis_workflow.py
```

Because the input dataset is created in memory, the finalized provenance block has no physical input artifact. The CSV output is registered as the run's output artifact.

## 2. Analysis-population summary

`population_summary.py` uses the public CDISC Pilot Study ADSL dataset and reproduces a recognizable population-summary workflow.

Its main TRACE sequence is:

```text
READ
→ FILTER analysis populations
→ AGGREGATE treatment counts
→ TRANSFORM reporting layout
→ VALIDATE table structure
→ OUTPUT RTF
```

Logical stages are grouped with `trace.step()` so the log can be read at both workflow and operation level.

The managed run writes:

```text
example-output/tlf_population.rtf
example-output/tlf_population.log
```

The finalized log identifies `data/adsl.xpt` as the input artifact and the RTF as the output artifact.

## 3. Specific adverse events

`specific_adverse_events.py` demonstrates a multi-dataset workflow using ADSL and ADAE.

Its main TRACE sequence is:

```text
READ ADSL
READ ADAE
→ FILTER Safety Population
→ AGGREGATE population denominators
→ MERGE ADAE + Safety Population
→ AGGREGATE subject incidence
→ VALIDATE table structure
→ OUTPUT RTF
```

This example is particularly useful for seeing why TRACE's statistical vocabulary is more informative than arbitrary log strings: the log shows where the population was selected, how the analysis datasets were combined, and where subject-level incidence was summarized.

The managed run writes:

```text
example-output/tlf_ae_specific.rtf
example-output/tlf_ae_specific.log
```

Its finalized log identifies both XPT inputs and the RTF output at program level.

## Run the CDISC examples

The two TLF examples use publicly available CDISC Pilot Study ADaM datasets and recognizable clinical-reporting workflows.

Install the example-only dependencies. These packages are intentionally not TRACE Core runtime dependencies:

```bash
python -m pip install -e ".[examples]"
```

The example dependency set is deliberately small: pandas reads the original XPT datasets, Polars performs the transformations, and `rtflite` produces the RTF output artifacts.

Download `adsl.xpt` and `adae.xpt` from the public CDISC Pilot Study repository:

```bash
python examples/fetch_example_data.py
```

Then run:

```bash
python examples/population_summary.py
python examples/specific_adverse_events.py
```

Downloaded data and generated outputs are ignored by Git.

## Why the TLF examples use these workflows

The population and adverse-event programs are pure-Python adaptations of analyses published in *Python for Clinical Study Reports and Submission* (PyCSR). Their original programs are Quarto documents. TRACE removes the Quarto wrapper so the examples demonstrate that structured execution logging is independent of the authoring environment.

TRACE uses PyCSR's examples as references for the analysis workflows, but it does **not** use the parquet datasets from the PyCSR demonstration repository. PyCSR converted the CDISC Pilot Study data to parquet for its project. These TRACE examples instead download and read the original CDISC Pilot Study ADaM datasets directly from the CDISC GitHub repository in SAS XPORT (`.xpt`) format. PyCSR is therefore the analysis-workflow reference; CDISC is the authoritative data source.

## What the finalized log adds

For the managed examples, `log_file` produces a review log with program-level provenance followed by the operation stream:

```text
TRACE EXECUTION

Program:  TLF_POPULATION
Run ID:   ...
Executed: ...

Input artifacts:
  data/adsl.xpt

Output artifacts:
  example-output/tlf_population.rtf

INFO [START] ...
INFO [STEP] ...
INFO [READ] ...
...
INFO [END] ...
```

Provenance is recorded once for the run. It is not repeated on every operation.

## What a reviewer should see

Across the examples, TRACE helps answer a compact set of execution questions:

- What data entered the program?
- Which analysis population was selected?
- Where did counts change?
- How were datasets combined?
- Which summaries or analyses were produced?
- Which explicit checks passed or failed?
- What output artifact was written?

The program, specification, output, and independent QC remain necessary for judging statistical correctness.

The examples are also an API stress test. Awkwardness found while instrumenting these realistic programs is useful release feedback; it is not a reason to add new TRACE abstractions automatically.

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
