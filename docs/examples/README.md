# TRACE Reviewer Examples

TRACE examples are intended to be read as execution evidence, not merely as API demonstrations. The executable programs under [`../../examples/`](../../examples/) use public CDISC Pilot Study ADaM data.

| Program | Reviewer focus |
|---|---|
| [`population_summary.py`](../../examples/population_summary.py) | analysis-population selection, attrition, treatment counts, validation, output |
| [`specific_adverse_events.py`](../../examples/specific_adverse_events.py) | Safety Population, ADSL/ADAE merge, subject incidence by SOC/PT, validation, output |

Both programs are pure-Python adaptations of public PyCSR analyses. PyCSR is used as the analysis-workflow reference only. TRACE reads the original CDISC Pilot Study XPORT (`.xpt`) datasets directly from the CDISC repository rather than using the parquet conversions in the PyCSR demonstration repository. Source and reproduction links are maintained in [`../../examples/README.md`](../../examples/README.md).

## Reviewer pattern

Across the programs, TRACE is most useful when the reviewer asks:

```text
What entered the analysis?
What population or records were selected?
Where did record counts change?
Did merges expand, contract, or preserve cardinality?
What summary operation was executed?
Which expectations were explicitly validated?
What output was produced?
Does this execution path make sense against the code, specification, and result?
```

The important distinction is between **execution evidence** and **statistical correctness**. A FILTER event can show how many records were retained. A MERGE event can expose cardinality. A VALIDATE PASS can show that an implemented criterion evaluated successfully. None of those statements, alone or together, proves that the specification, derivations, analysis rules, or final interpretation are correct.

## Population summary

Read the population FILTER events together. They expose how the same ADSL source contributes to the analysis populations and where participant counts change. The later summary and validation events make the treatment-level result reviewable, while OUTPUT connects that execution path to the generated RTF artifact.

The useful review sequence is:

```text
READ ADSL
    ↓
FILTER analysis populations
    ↓
AGGREGATE treatment summaries
    ↓
VALIDATE expected relationships
    ↓
OUTPUT RTF
```

With a managed provenance log, the reviewer can also connect that event sequence to the physical `adsl.xpt` input and RTF output recorded for the run.

## Specific adverse events

The critical path is:

```text
READ ADSL / ADAE
       ↓
FILTER Safety Population
       ↓
MERGE AE records with selected participants
       ↓
AGGREGATE unique participant incidence by SOC / PT / treatment
       ↓
VALIDATE
       ↓
OUTPUT RTF
```

The merge diagnostics make the analysis boundary reviewable. The reviewer can inspect which sources participated, how row counts changed, and whether the resulting incidence summary follows the intended Safety Population path.

## Live output and finalized review logs

During execution, TRACE events are visible immediately on the console. When a flagship program configures a managed `log_file`, the persistent log is finalized after execution with program-level provenance before the semantic event stream.

This creates two related review surfaces:

```text
Live console output
    = what is happening now

Final TRACE log
    = what happened in this run
```

The final log can identify the physical CDISC input artifacts and generated output artifact without repeating provenance on every semantic event.

Do not treat durations or example row counts as normative TRACE behavior. They are execution-specific diagnostics produced by the data and environment used for that run.

## Reproduce the examples

Install the example dependencies and fetch the public data:

```bash
python -m pip install -e ".[examples]"
python examples/fetch_example_data.py
```

Run the programs:

```bash
python examples/population_summary.py
python examples/specific_adverse_events.py
```

Generated RTF artifacts are written to `example-output/`. See [`../../examples/README.md`](../../examples/README.md) for the authoritative data sources and workflow references.

## What TRACE does not establish

A clean execution path does not prove that:

- the protocol or analysis specification is correct;
- the program implemented the specification correctly;
- the chosen statistical method is appropriate;
- every relevant QC criterion was implemented;
- the final table interpretation is correct.

TRACE makes execution evidence easier to inspect. Statistical and regulatory review still require the program, specification, output, and applicable QC process.
