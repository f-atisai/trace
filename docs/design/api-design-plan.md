# TRACE API Design Plan

Status: **Design in progress**

This document is the working design plan for the TRACE Python public API. It belongs in `docs/design/` while the API is being evaluated. Accepted, stable behavior should eventually move into `docs/api/` or `docs/framework/`.

## Design Principle

> TRACE should log what the statistical programmer means, not how Python logging works.

The Python standard library remains the logging infrastructure. TRACE provides the statistical-programming vocabulary, structured event model, conventions, rendering, and convenience API.

## Phase -1 — Repository and Project Bootstrap

Establish the public project before implementation.

Deliverables:

- repository structure;
- README;
- license;
- contribution guidelines;
- changelog;
- `pyproject.toml`;
- design documentation location;
- initial package namespace;
- development tooling; and
- pre-1.0 versioning policy.

No stable public API is implied by this phase.

## Phase 0 — TRACE Domain Model

Define the structured event model before defining formatted log messages.

Candidate event fields:

```text
severity
operation
object
action
metrics
details
status
context
```

Formatted strings must be renderings of structured events, not the internal source of truth.

## Phase 1 — Canonical TRACE Vocabulary

Define and document the core statistical-programming operations.

Initial candidates:

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

Lifecycle operations such as `START` and `END` may be internal or system-generated.

The vocabulary should deliberately avoid unnecessary synonyms.

## Phase 2 — Minimum Programmer Experience

Prototype TRACE against realistic statistical programs before implementation.

The API must add useful execution visibility without dominating the underlying analysis code.

Target:

```python
trace = Trace("T14_01")

trace.read("ADSL", rows=754, columns=16)
trace.filter("ADSL", "SAFFL == 'Y'", before=754, after=720)
trace.derive("AGEGR1", dataset="ADSL", source="AGE")
trace.output("T14_01", "outputs/T14_01.rtf")
```

## Phase 3 — Tier 1 Public API

Design the smallest useful operation-oriented API.

Candidate surface:

```python
trace.read()
trace.check()
trace.filter()
trace.sort()
trace.derive()
trace.transform()
trace.merge()
trace.aggregate()
trace.analyze()
trace.validate()
trace.output()
```

Every method should use consistent argument conventions.

## Phase 4 — Core Object Semantics

Decide how TRACE identifies datasets, variables, outputs, and other statistical objects.

The core API should remain usable without passing pandas objects. Integration layers may accept richer objects and extract metadata automatically.

## Phase 5 — Generic Structured Logging

Provide an escape hatch for operations that do not map to convenience methods.

Candidate:

```python
trace.log(
    "DERIVE",
    object="AGEGR1",
    action="created",
)
```

Convenience operations remain the preferred API.

## Phase 6 — Configuration API

Design a low-friction initialization experience.

Target:

```python
trace = Trace("T14_01")
```

Optional context:

```python
trace = Trace(
    program="T14_01",
    study="ABC123",
)
```

Advanced Python logging concepts should not be required for normal use.

## Phase 7 — Execution Lifecycle

Define program start, completion, duration, and failure behavior.

Candidate:

```python
with Trace("T14_01") as trace:
    ...
```

Unhandled exceptions must remain visible and must not be silently suppressed.

## Phase 8 — Step-Level Instrumentation

Support logical program stages.

Candidate:

```python
with trace.step("Analysis population"):
    ...
```

The context-manager form should be established before decorator syntax.

## Phase 9 — Decorators

Add decorators as optional syntactic sugar after step semantics are stable.

Candidate:

```python
@trace.step("Create summary")
def create_summary(...):
    ...
```

## Phase 10 — pandas Integration

Add optional DataFrame-aware metadata extraction without making pandas a core dependency.

Examples include automatic row counts and column counts.

The core library should remain extensible to Polars, PyArrow, and other tabular systems.

## Phase 11 — Merge Semantics

Design clinically useful merge logging.

Consider:

- left and right objects;
- keys;
- merge type;
- source row counts;
- result row count;
- unit-explicit matching diagnostics, such as matched subjects or unmatched keys; and
- duplicate-key diagnostics where relevant.

TRACE should observe and describe merges rather than replace dataframe merge operations.

## Phase 12 — Validation API

Make validation a first-class operation.

Candidate:

```python
trace.validate(
    "ADSL",
    check="USUBJID uniqueness",
    passed=True,
)
```

Convenience validators may be added later.

## Phase 13 — Severity Inference

Define operation-specific default severity behavior so programmers do not repeatedly choose log levels.

Examples:

- normal operations → `INFO`;
- failed non-fatal validation → `WARNING`;
- execution failure → `ERROR`.

## Phase 14 — Message Grammar

Define the canonical human-readable grammar.

Target:

```text
LEVEL [OPERATION] [OBJECT] ACTION – DETAILS
```

Messages should remain concise and easy for reviewers to scan.

## Phase 15 — Structured Events and Rendering

Separate event creation from rendering.

The same event should eventually support human-readable log files and structured formats such as JSON without changing the public operation API.

## Phase 16 — Exception Semantics

Define failure logging, traceback behavior, step failure behavior, and exception re-raising.

TRACE must never turn failures into apparent success.

## Phase 17 — Execution Context

Define metadata inherited by all events, such as:

- study;
- program;
- output identifier;
- run identifier;
- environment; and
- library version.

Avoid repeating context on every operation call.

## Phase 18 — Naming Conventions

Keep the public API predictable and concise.

Prefer:

```python
trace.filter()
```

over redundant forms such as:

```python
trace.log_filter()
```

## Phase 19 — Explicit Non-Goals

For the initial release series, TRACE is not:

- a dataframe manipulation library;
- a TLF generation framework;
- an SDTM/ADaM validator;
- a workflow orchestration platform;
- a reporting engine;
- an ETL framework; or
- a replacement for Python's standard logging system.

Its core responsibility is consistent, review-ready execution reporting.

## Phase 20 — Paper Prototypes

Apply the proposed API to realistic programs before freezing implementation.

Recommended cases:

1. demographics table;
2. adverse-event summary;
3. subject listing;
4. Kaplan-Meier figure;
5. ADaM derivation program; and
6. QC comparison program.

## Phase 21 — API Friction Review

Review every method for:

- readability;
- argument duplication;
- unnecessary verbosity;
- consistency;
- discoverability; and
- usefulness in realistic clinical code.

## Phase 22 — v0.1 API Candidate

Freeze the first intentionally small candidate API for implementation and testing.

This is a development API, not the `1.0.0` compatibility contract.

## Phase 23 — Cross-Method Consistency

Establish shared argument patterns and terminology across all operation methods.

A user who knows one TRACE method should be able to infer how another method behaves.

## Phase 24 — Automatic Metrics

Introduce convenience metadata extraction only after explicit APIs are understood.

Automation should reduce typing without obscuring what TRACE records.

## Phase 25 — Output Metadata

Define useful metadata for tables, listings, figures, datasets, and other generated artifacts.

Keep output logging focused on provenance and execution rather than report-generation responsibilities.

## Phase 26 — Execution Summaries

Design optional end-of-run summaries based on the structured event stream.

Possible content includes status, duration, operation counts, warnings, and errors.

## Phase 27 — Project Configuration

Consider optional TRACE configuration in `pyproject.toml` or another supported configuration source.

Configuration files must remain optional for basic adoption.

## Phase 28 — Additional Integrations

After the core API is stable, consider integrations such as:

- Polars;
- PyArrow;
- Statsmodels; and
- Lifelines.

Language-specific implementations may later share the TRACE framework specification.

## Phase 29 — Pre-1.0 Stabilization

Before `1.0.0`, explicitly define which public symbols, operation names, message semantics, and configuration behaviors become compatibility commitments.

## Phase 30 — Stable Programmer Experience

The long-term target is a small, readable API that can be added to an existing statistical program in minutes while producing consistent, auditable execution records.

`1.0.0` should represent a stable public contract, not simply feature completeness.
