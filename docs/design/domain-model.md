# TRACE Domain Model Specification

**Phase:** 0 — Freeze the TRACE Domain Model  
**Status:** Draft specification for review  
**Scope:** Domain model only; no implementation or public method signatures  
**Target milestone:** TRACE `0.x`

## 1. Purpose

TRACE represents the execution of statistical programs as a stream of structured events.

A TRACE event records **what happened during execution**, in a form that can be rendered for humans and consumed by machines.

The structured event is the source of truth.

Human-readable log messages such as:

```text
INFO [FILTER] [ADSL] SAFFL == 'Y' applied – N=754 → 720
```

are renderings of structured data such as:

```json
{
  "severity": "INFO",
  "operation": "FILTER",
  "object": "ADSL",
  "action": "SAFFL == 'Y' applied",
  "metrics": {
    "before": 754,
    "after": 720
  }
}
```

TRACE must never depend on parsing its own formatted log messages to reconstruct execution information.

This separation allows the same event stream to support:

- human-readable `.log` files;
- JSON output;
- execution manifests;
- QC summaries;
- dashboards;
- machine-readable audit records; and
- future integrations.

## 2. Core Domain Model

A TRACE execution event consists conceptually of:

```text
Event
├── severity
├── operation
├── object
├── action
├── metrics
├── details
├── status
└── context
```

The six domain concepts frozen in Phase 0 are:

```text
TRACE Event
TRACE Operation
TRACE Severity
TRACE Status
TRACE Context
TRACE Metrics
```

`object`, `action`, and `details` are event fields rather than independent domain types in Phase 0.

---

# 3. TRACE Event

## 3.1 Definition

A **TRACE Event** is one structured record describing a meaningful occurrence during execution of a statistical program.

Examples include:

- a dataset being read;
- a population filter being applied;
- an analysis variable being derived;
- two datasets being merged;
- a validation being performed;
- an output being written;
- a warning being raised;
- a logical processing step beginning or ending.

An event is descriptive. It records an occurrence; it does not perform the underlying statistical operation.

## 3.2 Canonical event fields

A TRACE Event contains the following conceptual fields:

| Field | Requirement | Meaning |
|---|---|---|
| `severity` | Required | Importance or seriousness of the event |
| `operation` | Required | Standard TRACE classification of what occurred |
| `object` | Conditionally required | Primary subject of the event |
| `action` | Required | Human-readable description of what happened |
| `metrics` | Optional | Structured quantitative information |
| `details` | Optional | Additional structured or textual information |
| `status` | Optional | Outcome state where an outcome is meaningful |
| `context` | Required conceptually | Execution metadata inherited or attached to the event |

## 3.3 Event invariants

Every valid TRACE Event must satisfy these rules:

1. `severity` must have a valid TRACE Severity.
2. `operation` must have a valid TRACE Operation.
3. `action` must communicate a completed, attempted, ongoing, or failed execution occurrence.
4. `metrics` must be structured data, not a preformatted metrics string.
5. `status`, when present, must use the TRACE Status vocabulary.
6. `context` must be logically separable from the event payload.
7. A rendered message must be reproducible from the structured event without parsing an earlier rendered message.
8. A renderer may omit information for readability, but it must not alter the underlying event semantics.
9. Events must describe observed program execution rather than infer undocumented clinical meaning.
10. Events should avoid embedding sensitive subject-level values unless explicitly required by an approved use case.

## 3.4 Object

`object` identifies the primary entity affected by or associated with an operation.

Examples:

```text
ADSL
ADAE
AGEGR1
T14_01
Safety Population
USUBJID uniqueness
```

The object may represent:

- a dataset;
- a dataframe;
- a variable;
- an analysis result;
- a table;
- a listing;
- a figure;
- a file;
- a validation target;
- a program;
- a logical execution step; or
- another named statistical-programming artifact.

### Object rule

TRACE must not require an object to be a Python object.

The conceptual identifier:

```text
ADSL
```

is sufficient.

This keeps the domain model independent of pandas, Polars, PyArrow, or any other execution library.

## 3.5 Action

`action` describes what occurred.

Examples:

```text
loaded
SAFFL == 'Y' applied
created
merged
written
uniqueness check completed
execution started
execution failed
```

The action should be concise and should not duplicate fields already represented structurally unless repetition materially improves human readability.

Good:

```text
operation = FILTER
object    = ADSL
action    = SAFFL == 'Y' applied
```

Avoid:

```text
operation = FILTER
object    = ADSL
action    = FILTER operation performed on ADSL using SAFFL == 'Y'
```

## 3.6 Details

`details` holds supplementary information that does not belong in the core identity of the event or in quantitative metrics.

Examples may include:

```json
{
  "source": "data/adsl.parquet",
  "format": "parquet"
}
```

or:

```json
{
  "keys": ["USUBJID"],
  "how": "left"
}
```

or a concise textual note where structured representation is not appropriate.

### Details rule

Prefer structured key-value details when the information may be useful programmatically.

Use free text only where structure would add little value.

## 3.7 Event identity

Phase 0 does not require a globally unique event identifier.

However, the model must permit a future event identifier or sequence number without breaking the conceptual model.

Possible future metadata includes:

```text
event_id
sequence
timestamp
parent_event_id
step_id
```

These are deliberately not frozen as required Phase 0 fields.

---

# 4. TRACE Operation

## 4.1 Definition

A **TRACE Operation** classifies the type of statistical-programming activity represented by an event.

Operation answers:

> What kind of execution activity occurred?

Examples:

```text
READ
FILTER
DERIVE
MERGE
VALIDATE
OUTPUT
```

## 4.2 Operation principles

TRACE Operations must be:

- domain meaningful;
- stable;
- concise;
- mutually distinguishable where practical;
- independent of a specific dataframe library;
- suitable for human-readable logs;
- suitable for machine aggregation; and
- broad enough to cover common statistical-programming workflows without becoming overly granular.

## 4.3 Phase 0 operation categories

Phase 0 freezes the concept of an operation, not yet the final full vocabulary.

The working operation set is:

```text
READ
CHECK
FILTER
SORT
DERIVE
TRANSFORM
MERGE
AGGREGATE
ANALYZE
VALIDATE
OUTPUT
```

Lifecycle operations under consideration:

```text
START
END
STEP
```

Whether lifecycle terms become first-class public operations or internal/system operations is deferred to the vocabulary phase.

## 4.4 Operation semantics

An operation describes **intent**, not implementation.

For example, these may all map conceptually to `FILTER`:

```python
df.query(...)
df.loc[...]
polars_df.filter(...)
duckdb.sql(...)
```

TRACE should not create separate operations solely because different libraries implement the same statistical-programming intent differently.

## 4.5 Operation stability

Once an operation enters the stable TRACE vocabulary, its semantic meaning should not change casually.

Changes to operation semantics may affect:

- rendered logs;
- JSON consumers;
- execution summaries;
- QC reports;
- dashboards; and
- downstream validation tooling.

For this reason, operations are part of the TRACE domain contract.

---

# 5. TRACE Severity

## 5.1 Definition

A **TRACE Severity** communicates the importance or seriousness of an event.

Severity answers:

> How much attention should this event receive?

TRACE uses Python's established logging severity model rather than inventing a competing system.

Canonical severities:

```text
DEBUG
INFO
WARNING
ERROR
CRITICAL
```

## 5.2 Severity semantics

### DEBUG

Detailed diagnostic information useful primarily during development, troubleshooting, or deep review.

Examples:

- intermediate dimensions;
- branch decisions;
- optional diagnostic values;
- verbose processing details.

DEBUG events should normally be safe to omit from routine production logs.

### INFO

Normal, expected execution activity.

Examples:

- dataset read;
- filter applied;
- variable derived;
- merge completed;
- validation passed;
- output written.

INFO is expected to be the dominant TRACE severity.

### WARNING

Unexpected or potentially concerning behavior that does not necessarily prevent successful execution.

Examples:

- a validation fails but execution is allowed to continue;
- expected metadata is absent but a fallback is available;
- an empty subgroup is encountered;
- a non-fatal mismatch is detected.

### ERROR

A significant failure affecting an operation, step, output, or execution result.

Examples:

- output creation fails;
- required input cannot be read;
- derivation raises an exception;
- validation policy requires failure.

### CRITICAL

A severe failure indicating that execution cannot safely continue or that the execution environment is fundamentally compromised.

CRITICAL should be rare.

## 5.3 Severity is not Status

Severity and Status are distinct.

Example:

```text
severity = WARNING
status   = FAIL
```

means:

> A validation failed, but the failure was considered non-fatal.

Another event might be:

```text
severity = ERROR
status   = FAIL
```

meaning:

> The same or another failure is execution-blocking.

Severity indicates seriousness.

Status indicates outcome.

## 5.4 Severity inference

TRACE may later infer severity from operation and status.

Example:

```text
VALIDATE + PASS → INFO
VALIDATE + FAIL → WARNING
```

unless configuration or policy promotes the failure to `ERROR`.

The exact inference rules are deferred to a later API design phase.

---

# 6. TRACE Status

## 6.1 Definition

A **TRACE Status** describes the outcome state of an event when the event has a meaningful outcome.

Status answers:

> What was the result?

Not every event requires a status.

For example:

```text
READ ADSL
```

may not need an explicit status if successful completion is already represented by the existence of the event.

## 6.2 Core status vocabulary

Phase 0 defines the following conceptual statuses:

```text
SUCCESS
FAIL
SKIP
PARTIAL
```

Additional candidate states may be introduced only when a clear use case exists.

## 6.3 Status semantics

### SUCCESS

The intended operation or check completed successfully.

### FAIL

The intended operation or check did not satisfy its required outcome.

`FAIL` does not automatically imply execution termination.

### SKIP

The operation was intentionally not executed because a defined condition made it unnecessary or inapplicable.

### PARTIAL

The operation completed only partially, or some expected result was unavailable.

Use sparingly.

## 6.4 Validation-specific display

For reviewer-facing logs, renderers may display:

```text
PASS
FAIL
```

for validation outcomes even if the internal canonical successful status is `SUCCESS`.

This is a rendering concern.

The internal event model must not require parsing display-specific terminology.

## 6.5 Status versus execution lifecycle

Phase 0 does not freeze statuses such as:

```text
STARTED
RUNNING
COMPLETED
```

because these may be represented more cleanly as lifecycle operations.

That decision is deferred.

---

# 7. TRACE Context

## 7.1 Definition

**TRACE Context** contains execution metadata that gives an event meaning within the broader program run.

Context answers:

> Under what execution circumstances did this event occur?

Context is separate from the event's immediate payload.

## 7.2 Context principles

Context should:

- be inheritable across events;
- avoid repeated caller boilerplate;
- remain structured;
- support filtering and grouping;
- support reproducibility and auditability;
- avoid unnecessary environment capture;
- avoid sensitive information by default.

## 7.3 Core context fields

Phase 0 defines the following conceptual context fields:

| Field | Requirement | Meaning |
|---|---|---|
| `program` | Strongly recommended | Program or script identifier |
| `study` | Optional | Study identifier |
| `run_id` | Optional | Identifier for a specific execution |
| `step` | Optional | Current logical processing step |
| `output` | Optional | Associated output identifier |
| `environment` | Optional | Execution environment designation |
| `trace_version` | Recommended | TRACE library version |
| `user_context` | Optional | Additional approved caller-defined metadata |

Example:

```json
{
  "program": "T14_01",
  "study": "ABC123",
  "run_id": "2026-08-31T174500Z",
  "step": "Safety population",
  "output": "T14_01",
  "environment": "validation",
  "trace_version": "0.1.0"
}
```

## 7.4 Context inheritance

A TRACE run may establish context once:

```text
program = T14_01
study   = ABC123
```

All subsequent events may inherit it.

A narrower context may temporarily add:

```text
step = Analysis population
```

without requiring every event call to repeat all existing metadata.

## 7.5 Context mutability

Context may evolve over an execution.

For example:

```text
Program context
└── Step context
    └── Output context
```

However, once an event is created, its captured context must be treated as immutable historical information.

Changing current context must not retroactively modify earlier events.

## 7.6 Sensitive data

TRACE Context must not capture sensitive subject-level clinical data by default.

In particular, context should avoid automatically recording:

- subject identifiers;
- direct identifiers;
- free-text clinical data;
- credentials;
- access tokens;
- secrets;
- connection strings containing credentials.

Any future feature that captures subject-level metadata requires explicit design review.

---

# 8. TRACE Metrics

## 8.1 Definition

**TRACE Metrics** are structured quantitative measurements associated with an event.

Metrics answer:

> What measurable quantities describe this operation?

Examples:

```json
{
  "before": 754,
  "after": 720
}
```

```json
{
  "rows": 754,
  "columns": 16
}
```

```json
{
  "matched": 4127,
  "unmatched_left": 3,
  "unmatched_right": 0
}
```

## 8.2 Metrics principles

Metrics must:

- remain machine-readable;
- use stable semantic names;
- store values rather than formatted fragments;
- avoid units embedded in key names where a cleaner structure is possible;
- permit operation-specific metrics;
- remain optional.

Bad:

```json
{
  "N": "754 -> 720"
}
```

Good:

```json
{
  "before": 754,
  "after": 720
}
```

The renderer may produce:

```text
N=754 → 720
```

## 8.3 Metric value types

Metrics should conceptually support:

```text
integer
floating-point number
boolean
duration
count
percentage
```

String values should generally belong in `details`, unless the value represents a formally defined categorical metric.

## 8.4 Metric naming

Metric names should describe semantics rather than presentation.

Prefer:

```text
before
after
rows
columns
matched
unmatched_left
unmatched_right
duration_seconds
missing
duplicates
```

Avoid:

```text
N_before_text
display_rows
formatted_duration
```

## 8.5 Operation-specific metrics

Different operations may define recommended metrics.

Examples:

### READ

```json
{
  "rows": 754,
  "columns": 16
}
```

### FILTER

```json
{
  "before": 754,
  "after": 720,
  "removed": 34
}
```

### MERGE

```json
{
  "left_rows": 720,
  "right_rows": 4127,
  "result_rows": 4127,
  "matched": 4124,
  "unmatched_left": 3
}
```

### VALIDATE

```json
{
  "checked": 720,
  "failed": 3
}
```

### OUTPUT

```json
{
  "rows": 42
}
```

The operation vocabulary phase will determine which metric names become normative.

## 8.6 Derived metrics

A renderer or summary layer may derive display values.

For example:

```text
removed = before - after
```

However, derived metrics must not be assumed to exist unless their source values are present and their semantics are valid for the operation.

---

# 9. Relationship Between the Domain Types

The conceptual relationship is:

```text
TRACE Event
│
├── has one TRACE Severity
├── has one TRACE Operation
├── has zero or one TRACE Status
├── has one TRACE Context snapshot
├── has zero or more TRACE Metrics
├── identifies an object
├── describes an action
└── may include details
```

A sequence of TRACE Events represents a program execution:

```text
Execution
│
├── Event 1
├── Event 2
├── Event 3
└── ...
```

An execution summary is therefore derived from events.

It is not a parallel source of truth.

---

# 10. Canonical Examples

## 10.1 Read

Structured event:

```json
{
  "severity": "INFO",
  "operation": "READ",
  "object": "ADSL",
  "action": "loaded",
  "metrics": {
    "rows": 754,
    "columns": 16
  },
  "context": {
    "program": "T14_01",
    "study": "ABC123"
  }
}
```

Possible rendering:

```text
INFO [READ] [ADSL] loaded – N=754, Vars=16
```

## 10.2 Filter

Structured event:

```json
{
  "severity": "INFO",
  "operation": "FILTER",
  "object": "ADSL",
  "action": "SAFFL == 'Y' applied",
  "metrics": {
    "before": 754,
    "after": 720
  },
  "context": {
    "program": "T14_01",
    "study": "ABC123"
  }
}
```

Possible rendering:

```text
INFO [FILTER] [ADSL] SAFFL == 'Y' applied – N=754 → 720
```

## 10.3 Derivation

Structured event:

```json
{
  "severity": "INFO",
  "operation": "DERIVE",
  "object": "AGEGR1",
  "action": "created",
  "details": {
    "dataset": "ADSL",
    "source": "AGE"
  },
  "context": {
    "program": "T14_01"
  }
}
```

Possible rendering:

```text
INFO [DERIVE] [AGEGR1] created – dataset=ADSL, source=AGE
```

## 10.4 Validation success

Structured event:

```json
{
  "severity": "INFO",
  "operation": "VALIDATE",
  "object": "ADSL",
  "action": "USUBJID uniqueness",
  "status": "SUCCESS",
  "metrics": {
    "checked": 754,
    "failed": 0
  },
  "context": {
    "program": "T14_01"
  }
}
```

Possible rendering:

```text
INFO [VALIDATE] [ADSL] USUBJID uniqueness – PASS
```

## 10.5 Validation failure

Structured event:

```json
{
  "severity": "WARNING",
  "operation": "VALIDATE",
  "object": "ADSL",
  "action": "USUBJID uniqueness",
  "status": "FAIL",
  "metrics": {
    "checked": 754,
    "failed": 3
  },
  "details": {
    "message": "duplicate values detected"
  },
  "context": {
    "program": "T14_01"
  }
}
```

Possible rendering:

```text
WARNING [VALIDATE] [ADSL] USUBJID uniqueness – FAIL – 3 duplicate values detected
```

## 10.6 Output

Structured event:

```json
{
  "severity": "INFO",
  "operation": "OUTPUT",
  "object": "T14_01",
  "action": "written",
  "details": {
    "path": "outputs/T14_01.rtf",
    "format": "RTF"
  },
  "metrics": {
    "rows": 42
  },
  "context": {
    "program": "T14_01",
    "study": "ABC123"
  }
}
```

Possible rendering:

```text
INFO [OUTPUT] [T14_01] written – outputs/T14_01.rtf, Rows=42
```

---

# 11. Source-of-Truth Rule

The central Phase 0 rule is:

> TRACE events are structured data first. Formatted log messages are projections of those events.

Therefore:

```text
Structured event
      │
      ├── Human-readable log renderer
      ├── JSON renderer
      ├── Execution summary
      ├── QC report
      ├── Manifest
      └── Dashboard / downstream consumer
```

Not:

```text
Formatted log string
      │
      └── parse text back into data
```

No future TRACE feature should require parsing the display message to recover event semantics.

---

# 12. Data Ownership and Mutation Rules

TRACE records observations about program execution.

TRACE does not own the underlying statistical objects.

Therefore:

1. A TRACE Event must not require persistence of the full dataframe or dataset.
2. Metrics should contain summaries rather than copies of source data.
3. TRACE must not mutate the statistical object merely to log it.
4. TRACE integrations may inspect supported objects to derive metadata.
5. Integration-derived metadata must become ordinary structured event fields after extraction.

This boundary prevents TRACE from becoming a dataframe-processing framework.

---

# 13. Serialization Requirements

Although serialization is not implemented in Phase 0, the domain model must be serialization-friendly.

A TRACE Event should ultimately be representable in formats such as:

```text
JSON
JSON Lines
dictionary-like records
execution manifests
```

without loss of semantic meaning.

Therefore, public event data should avoid depending on:

- live Python object references;
- logger instances;
- handlers;
- formatter objects;
- open file handles;
- non-serializable dataframe objects.

Integrations may temporarily interact with such objects, but the resulting event should contain serializable metadata.

---

# 14. Extensibility Rules

The domain model must permit future additions without invalidating existing events.

Likely future additions include:

```text
timestamp
event_id
sequence
duration
parent_event_id
step_id
exception metadata
source location
process identifier
thread identifier
host information
package versions
```

These are not part of the Phase 0 frozen minimum.

The model should favor additive evolution.

---

# 15. Phase 0 Decisions

The following decisions are frozen for subsequent API design unless a strong design issue requires reopening them.

## Decision 1

TRACE represents execution as **structured events**.

## Decision 2

Formatted log messages are **renderings**, not the source of truth.

## Decision 3

Every event has a TRACE Severity and TRACE Operation.

## Decision 4

Status is separate from severity.

## Decision 5

Metrics are structured quantitative data.

## Decision 6

Context is structured execution metadata and is logically separate from the immediate event payload.

## Decision 7

TRACE objects are conceptual identifiers and do not require pandas or another dataframe implementation.

## Decision 8

TRACE records execution behavior; it does not perform the underlying statistical operation.

## Decision 9

TRACE must remain compatible with machine-readable serialization.

## Decision 10

Subject-level sensitive information is not captured automatically.

---

# 16. Decisions Explicitly Deferred

The following are intentionally deferred to later design phases:

- exact Python classes or dataclasses;
- exact constructor signatures;
- exact public method signatures;
- enum versus string representation;
- final operation vocabulary;
- lifecycle operation representation;
- timestamp requirements;
- event identifiers;
- severity inference rules;
- validation-specific helper methods;
- pandas integration behavior;
- renderer implementation;
- JSON schema;
- context manager behavior;
- decorator behavior;
- exception schema;
- execution-summary schema.

Freezing these prematurely would couple the domain model to implementation choices.

---

# 17. Phase 0 Acceptance Criteria

Phase 0 is complete when the project agrees that:

1. TRACE's fundamental unit is a structured execution event.
2. The six core domain concepts are clearly distinguished.
3. severity and status have separate meanings.
4. operation represents statistical-programming intent.
5. metrics contain structured measurements.
6. context contains inherited execution metadata.
7. formatted strings are never the source of truth.
8. the domain model is independent of pandas.
9. the event representation can later be serialized without redesigning the programmer-facing API.
10. the model is sufficient to represent common READ, FILTER, DERIVE, VALIDATE, and OUTPUT examples.

---

# 18. Phase 0 Outcome

The TRACE domain model is:

```text
Execution
└── TRACE Event
    ├── TRACE Severity
    ├── TRACE Operation
    ├── Object
    ├── Action
    ├── TRACE Metrics
    ├── Details
    ├── TRACE Status
    └── TRACE Context
```

This model becomes the foundation for the next design phase:

**Phase 1 — Freeze the canonical TRACE operation vocabulary.**
