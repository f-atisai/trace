# TRACE Statistical Programming Examples

These examples show TRACE inside recognizable clinical/statistical-programming workflows. They are intentionally small and self-contained so the execution path is easy to inspect, but the variables, operations, and review questions reflect real TLF, ADaM, and QC work.

| Example | Statistical-programming problem | Primary TRACE review value |
|---|---|---|
| [`demographics_table.py`](demographics_table.py) | Safety-population demographics by treatment | population attrition, derivation, treatment summaries |
| [`adverse_events_table.py`](adverse_events_table.py) | Treatment-emergent AE summary by SOC/PT | merge cardinality, safety population, subject incidence |
| [`subject_listing.py`](subject_listing.py) | Safety subject listing | population selection, ordering, presentation transform |
| [`kaplan_meier_figure.py`](kaplan_meier_figure.py) | Kaplan-Meier overall-survival figure | ITT population, time-to-event analysis, curve validation |
| [`adam_derivation.py`](adam_derivation.py) | ADLB baseline/change derivation | source preparation, treatment merge, baseline derivation |
| [`qc_comparison.py`](qc_comparison.py) | Independent QC comparison | independent result comparison and explicit validation |

The examples use familiar variables including `USUBJID`, `TRT01A`, `SAFFL`, `ITTFL`, `AGE`, `SEX`, `AEBODSYS`, `AEDECOD`, `TRTEMFL`, `PARAMCD`, `AVAL`, and `CNSR`.

Each example contains:

1. the statistical-programming task;
2. the Python implementation;
3. TRACE instrumentation using the current API;
4. representative TRACE output; and
5. the review questions that evidence supports.

The examples are not intended to define new TRACE vocabulary. If a realistic workflow exposes API friction, that is evidence for the later API-friction review rather than a reason to invent a new operation solely for the example.

The sample programs use pandas, and the Kaplan-Meier example also uses matplotlib for a simple figure. These are example dependencies, not TRACE Core dependencies.
