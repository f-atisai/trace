# Using TRACE with Quarto

TRACE works naturally inside Quarto documents because Quarto can execute Python code. Quarto is optional: TRACE remains fully usable in ordinary Python scripts and other execution environments.

The relationship is:

```text
Quarto
  └─ rationale + narrative + code

TRACE
  └─ structured execution log

TLF
  └─ analytical result
```

Quarto explains the analysis. TRACE records important statistical operations and run context. The resulting table, listing, figure, dataset, or other artifact remains the analytical result under review.

## Quarto is not required

TRACE does not depend on Quarto and does not require literate programming.

The same TRACE API works in:

```text
.py scripts
.qmd documents
notebooks
batch pipelines
scheduled jobs
other Python execution environments
```

A Quarto document is one possible host for a TRACE-instrumented statistical program, not a TRACE runtime or prerequisite.

```text
Without Quarto

analysis.py ──────► TRACE log ──────► TLF

With Quarto

analysis.qmd ─────► TRACE log ──────► TLF
```

The TRACE operations remain the same when the same analysis is implemented in either form.

## Division of responsibility

| Concern | Quarto | TRACE |
|---|---|---|
| Analytical rationale | Yes | No |
| Narrative explanation | Yes | No |
| Python source code | Yes | Runs alongside it |
| Structured statistical operations | No | Yes |
| Diagnostics and validations | No | Yes |
| Program-level provenance | No | Yes |
| Statistical output | May present it | Records its production |

TRACE should not duplicate explanatory prose already present in a Quarto document.

## Example: analysis population

A Quarto section might explain the intent:

```markdown
## Analysis population

The Safety Population includes all participants who received at least one dose of study treatment.
```

The Python code performs the selection and records it with TRACE:

```python
safety = adsl.filter(pl.col("SAFFL") == "Y")

trace.filter(
    "ADSL",
    "SAFFL == 'Y'",
    result="Safety Population",
    before=adsl.height,
    after=safety.height,
)
```

TRACE records:

```text
INFO [FILTER] [ADSL] SAFFL == 'Y' applied – N=254 → 249
```

The artifacts answer different questions:

```text
Quarto narrative
  Why is this population being selected?

Python code
  How was it implemented?

TRACE
  What operation and diagnostics were recorded during this run?
```

The resulting TLF can then be reviewed against the rationale, code, and TRACE log.

## Example: statistical analysis

A Quarto document might contain:

```markdown
## Primary efficacy analysis

Change from baseline at Week 24 is analysed using ANCOVA with treatment and baseline value in the model.
```

The Python analysis could record:

```python
ancova_results = perform_ancova(glucose_data, treatments)

trace.analyze(
    "ADLBC",
    "Week 24 glucose change",
    method="ANCOVA",
    population="Efficacy",
    result="ancova_results",
)
```

TRACE provides a concise record of the analysis operation:

```text
INFO [ANALYZE] [Week 24 glucose change] analyzed – source=ADLBC, method=ANCOVA, population=Efficacy
```

TRACE does not repeat the model rationale, estimand description, interpretation, or methodological explanation already documented in Quarto.

## Steps and document sections

A coarse TRACE step may align naturally with a Quarto section:

```python
with trace.step("Analysis population"):
    safety = adsl.filter(pl.col("SAFFL") == "Y")
    trace.filter(
        "ADSL",
        "SAFFL == 'Y'",
        result="Safety Population",
        before=adsl.height,
        after=safety.height,
    )
```

Possible TRACE output:

```text
INFO [STEP]   [Analysis population] started
INFO [FILTER] [ADSL] SAFFL == 'Y' applied – N=254 → 249
INFO [STEP]   [Analysis population] completed – 0.031s
```

This alignment is optional. TRACE does not require section names to become steps, and programmers should not instrument every Quarto heading.

## Finalized review logs

Quarto execution can use the same managed `Trace` form as an ordinary Python script:

```python
with Trace("T14_01", log_file="logs/T14_01.log") as trace:
    ...
```

The finalized log can include program-level provenance followed by the complete operation stream:

```text
TRACE EXECUTION

Program:  T14_01
Run ID:   7eab...
Executed: 2026-09-30T09:15:22Z

Input artifacts:
  data/adsl.xpt

Output artifacts:
  outputs/T14_01.rtf

INFO [START] [T14_01] execution started
...
INFO [END] [T14_01] execution completed – 0.84s
```

TRACE does not need to know whether Python is being executed by Quarto. Presentation choices such as hiding console messages from the rendered document remain Quarto or execution-environment concerns.

## Reviewer workflow

For a Quarto-based statistical program, review the artifacts together:

```text
analysis.qmd  ──────►  TRACE log  ──────►  TLF
     │                    │                 │
 intent + code       recorded run          result
```

A reviewer can:

1. read the relevant Quarto narrative and code to understand the intended analysis;
2. follow TRACE to see the important operations and diagnostics recorded during execution;
3. investigate validations, warnings, or unexpected data transitions; and
4. reconcile the resulting TLF with both the documented intent and recorded run.

See [Reviewing Statistical Programs with TRACE](../framework/reviewer-guide.md) for the broader review workflow.

## What TRACE does not add to Quarto

TRACE currently does not provide:

```text
TRACE Quarto extension
TRACE-specific Quarto renderer
automatic embedding of TRACE blocks
automatic extraction of Quarto headings
automatic inference of analysis intent from prose
Quarto-specific TRACE operations
```

Those features would couple TRACE to one authoring environment and should be added only if real-world use demonstrates a clear need.

## Design principle

> **Quarto may provide the narrative around a TRACE-instrumented analysis, but TRACE remains independent of Quarto.**

A statistical programmer who never uses Quarto should receive the same operation vocabulary, lifecycle behavior, provenance, and review value as a programmer who does.
