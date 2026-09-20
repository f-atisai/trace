# Using TRACE with Quarto

TRACE works naturally inside Quarto documents because Quarto can execute Python code. Quarto is optional: TRACE remains fully usable in ordinary Python scripts and other execution environments.

The relationship is:

```text
Quarto
  └─ rationale + narrative + code

TRACE
  └─ execution evidence

TLF
  └─ analytical result
```

Quarto explains the analysis. TRACE records important execution evidence. The resulting table, listing, figure, dataset, or other artifact is reviewed as the analytical result.

## Quarto is not required

TRACE does not depend on Quarto and does not require programmers to adopt literate programming.

The same TRACE API works in:

```text
.py scripts
.qmd documents
notebooks
batch pipelines
scheduled jobs
other Python execution environments
```

A Quarto document is therefore one possible host for a TRACE-instrumented statistical program, not a TRACE runtime or prerequisite.

```text
Without Quarto

analysis.py ──────► TRACE log ──────► TLF

With Quarto

analysis.qmd ─────► TRACE log ──────► TLF
```

The semantic TRACE events remain equivalent when the same analysis is implemented in either form.

## Division of responsibility

Quarto and TRACE solve different problems.

| Concern | Quarto | TRACE |
|---|---|---|
| Analytical rationale | Yes | No |
| Narrative explanation | Yes | No |
| Python source code | Yes | Executes alongside it |
| Semantic execution events | No | Yes |
| Execution diagnostics | No | Yes |
| Program-level provenance | No | Yes |
| Statistical output | May present it | Records its production |

TRACE does not duplicate the explanatory prose already present in a Quarto document.

## Example: analysis population

A Quarto section might explain the analytical intent:

```markdown
## Analysis population

The Safety Population includes all participants who received at least one dose of study treatment.
```

The executable Python code then performs the operation and records it with TRACE:

```python
safety = adsl.filter(pl.col("SAFFL") == "Y")

trace.filter(
    "ADSL",
    "SAFFL == 'Y'",
    before=adsl.height,
    after=safety.height,
)
```

The resulting TRACE evidence might be:

```text
INFO [FILTER] [ADSL] SAFFL == 'Y' applied – N=254 → 249
```

The three artifacts answer different questions:

```text
Quarto narrative
  Why is this population being selected?

Python code
  How was it implemented?

TRACE
  What selection was recorded during this execution, and what happened to the row count?
```

The resulting TLF can then be reviewed against the rationale, code, and recorded execution.

## Example: statistical analysis

A Quarto document might contain:

```markdown
## Primary efficacy analysis

Change from baseline at Week 24 is analysed using ANCOVA with treatment and baseline value in the model.
```

The corresponding Python analysis could record:

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

TRACE then provides concise execution evidence such as:

```text
INFO [ANALYZE] [Week 24 glucose change] ANCOVA fitted – source=ADLBC, population=Efficacy
```

TRACE does not repeat the model rationale, estimand description, interpretation, or methodological explanation already documented in Quarto.

## Steps and document sections

A coarse TRACE step may align naturally with a Quarto section:

```markdown
## Analysis population
```

```python
with trace.step("Analysis population"):
    safety = adsl.filter(pl.col("SAFFL") == "Y")
    trace.filter(
        "ADSL",
        "SAFFL == 'Y'",
        before=adsl.height,
        after=safety.height,
    )
```

Possible TRACE evidence:

```text
INFO [STEP]   [Analysis population] started
INFO [FILTER] [ADSL] SAFFL == 'Y' applied – N=254 → 249
INFO [STEP]   [Analysis population] completed – 0.031s
```

This alignment is optional. TRACE does not require section names to become steps, and programmers should not instrument every Quarto heading.

## Rendering behavior

TRACE behaves the same way during Quarto execution as it does during conventional Python execution.

A Quarto workflow may choose to suppress TRACE console messages from the rendered document while still writing them to the configured TRACE destination. That is a presentation choice controlled by the document or execution environment, not a separate TRACE semantic mode.

TRACE does not need to know whether Python is being executed by Quarto.

## Reviewer workflow

For a Quarto-based statistical program, review the three artifacts together:

```text
analysis.qmd  ──────►  TRACE log  ──────►  TLF
     │                    │                 │
 intent + code         execution           result
```

A reviewer can:

1. read the relevant Quarto narrative and code to understand the intended analysis;
2. follow TRACE to see the important operations and diagnostics recorded during execution;
3. investigate validations, warnings, or unexpected data transitions; and
4. reconcile the resulting TLF with both the documented intent and execution evidence.

The broader reviewer workflow is defined in [Reviewing Statistical Programs with TRACE](../framework/reviewer-guide.md).

## What TRACE does not add to Quarto

```text
TRACE Quarto extension
TRACE Quarto renderer
automatic TRACE block embedding
automatic extraction of Quarto headings
automatic inference of analysis intent from prose
Quarto-specific TRACE operations
```

These features would couple TRACE to one authoring environment without evidence that the added complexity improves statistical-programming review.

They should be considered only if later real-world use demonstrates a concrete need.

## Design principle

The governing rule is:

> **Quarto may provide the narrative around a TRACE-instrumented analysis, but TRACE must remain independent of Quarto.**

A statistical programmer who never uses Quarto should receive the same TRACE capabilities, semantic vocabulary, diagnostics, provenance, lifecycle behavior, and reviewer value as a programmer who does.
