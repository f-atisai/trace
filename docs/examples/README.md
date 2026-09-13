# TRACE Reviewer Examples

TRACE examples are intended to be read as execution evidence, not merely as API demonstrations. The executable programs under [`../../examples/`](../../examples/) use public CDISC Pilot Study ADaM data.

| Program | Reviewer focus |
|---|---|
| [`population_summary.py`](../../examples/population_summary.py) | analysis-population selection, attrition, treatment counts, output |
| [`specific_adverse_events.py`](../../examples/specific_adverse_events.py) | Safety Population, ADSL/ADAE merge, subject incidence by SOC/PT |
| [`kaplan_meier_survival.py`](../../examples/kaplan_meier_survival.py) | OS endpoint selection, censoring convention, Kaplan-Meier method, curve validation |

The population and adverse-event programs are pure-Python adaptations of public PyCSR analyses. They read the original CDISC Pilot Study XPORT datasets rather than PyCSR's parquet conversions. The Kaplan-Meier program uses the CDISC Pilot Study ADTTE data with `lifelines.KaplanMeierFitter`. Source and reproduction links are maintained in [`../../examples/README.md`](../../examples/README.md).

## Reviewer pattern

Across the programs, TRACE is most useful when the reviewer asks:

```text
What entered the analysis?
What population or records were selected?
Where did record counts change?
Did merges expand, contract, or preserve cardinality?
What summary or statistical method was executed?
Which expectations were explicitly validated?
What output was produced?
Does this execution path make sense against the code, specification, and result?
```

The important distinction is between **execution evidence** and **statistical correctness**. A FILTER event can show exactly how many records were retained. A MERGE event can expose cardinality. An ANALYZE event can record that Kaplan-Meier was the method executed. A VALIDATE PASS can show that an implemented criterion evaluated successfully. None of those statements, alone or together, proves that the specification, derivations, estimator, censoring rules, or final interpretation are correct.

## Reading the examples

### Population summary

Read the FILTER events together. They expose how the same ADSL source contributes to the ITT, efficacy, and Safety Populations. The AGGREGATE event identifies the treatment-level participant summary, and the OUTPUT event connects that execution path to the RTF table.

### Specific adverse events

The critical path is READ ADSL/ADAE → FILTER Safety Population → MERGE ADAE with the selected participants → AGGREGATE unique participant incidence by SOC/preferred term/treatment → VALIDATE → OUTPUT.

The merge diagnostics make the analysis boundary reviewable. The reviewer can see which source supplied treatment-population membership and whether the AE analysis records changed when restricted to that population.

### Kaplan-Meier overall survival

The critical path is READ ADTTE → FILTER the OS parameter → VALIDATE required time/censor information → ANALYZE using Kaplan-Meier by treatment → VALIDATE probability bounds → OUTPUT the survival figure.

The analysis records `AVAL` as analysis time and `CNSR == 0` as the event convention. The reviewer still needs the ADaM metadata and SAP to establish whether those choices are correct for the intended endpoint.

## Captured TRACE output

The programs should be executed in a clean environment before release and their actual TRACE output captured from that execution. This document deliberately does not invent row counts or durations before that verification run.
