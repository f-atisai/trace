# TRACE Reference Prototype Contract

**Sprint:** 0 — Define the Prototype Contract  
**Status:** Active prototype scope  
**Repository location:** `docs/design/reference-prototype.md`

## 1. Purpose

This document defines the contract for the TRACE reference prototype.

The prototype is intentionally **disposable**.

Its purpose is to validate whether the frozen TRACE API and event model feel correct when exercised in realistic statistical-programming workflows.

The prototype is **not** the production `v0.1` implementation and must not be treated as production architecture.

Code created during the prototype may be rewritten, reorganized, or discarded entirely after the API review.

> The prototype exists to validate the design, not to preserve the implementation.

## 2. Primary Validation Goals

The reference prototype will validate:

- API ergonomics
- event model
- canonical vocabulary
- text rendering
- program lifecycle
- step instrumentation

The central question is:

> Does TRACE feel natural, concise, and semantically useful in real statistical programs?

## 3. Explicit Non-Goals

The prototype does **not** validate:

- production performance
- backwards compatibility
- packaging and release automation
- plugin architecture
- pandas integration
- Polars integration
- PyArrow integration
- log rotation
- JSON schemas
- remote telemetry
- distributed logging
- asynchronous logging
- advanced handler configuration
- organization-wide configuration
- CLI behavior
- production security hardening
- long-term persistence guarantees

These concerns may be revisited only after the API has been validated.

## 4. Disposable Implementation Rule

Every Python component created for this prototype should be considered replaceable.

The following are explicitly allowed after prototype evaluation:

- rename modules;
- change internal classes;
- change internal data structures;
- replace the renderer architecture;
- rewrite the logger integration;
- remove prototype abstractions;
- change implementation patterns;
- discard the entire prototype.

The prototype must not accumulate compatibility obligations.

No internal API should be considered stable merely because it was used during the reference implementation.

## 5. Frozen Design Inputs

The prototype will implement only the design decisions already frozen through Phases 0–8.

These include:

- TRACE domain model;
- canonical operation vocabulary;
- minimum programmer experience;
- Tier 1 API;
- object-versus-operation semantics;
- generic structured-event escape hatch;
- configuration model;
- program lifecycle behavior;
- step-level instrumentation.

The prototype is intended to test these decisions.

It is not a mandate to preserve them if realistic examples reveal a design flaw.

## 6. Prototype Decision Rule

When implementation convenience conflicts with the frozen programmer experience, the programmer experience wins.

The prototype must not distort the public API merely because a different internal implementation would be easier.

For example, the prototype must not require runtime dataframe objects in core methods simply because that makes metadata extraction convenient.

The prototype exists to test the API contract as designed.

## 7. Scope-Creep Rule

A feature should not be added during the prototype unless it is required to answer one of the defined validation questions.

Before adding a new capability, ask:

> Is this necessary to determine whether the current TRACE API feels right?

If the answer is no, defer it.

Examples that should normally be deferred:

```text
automatic pandas inspection
custom formatter plugins
JSON output
environment-variable configuration
log rotation
telemetry
decorators
CLI tooling
```

## 8. Reference Package Boundary

The reference implementation will remain intentionally small.

Target structure:

```text
src/trace_tlf/
├── __init__.py
├── trace.py
├── event.py
├── operations.py
├── severity.py
├── status.py
├── context.py
└── rendering/
    ├── __init__.py
    └── text.py
```

This structure is a prototype organization, not a production architecture commitment.

## 9. Prototype Responsibilities

The reference implementation should be capable of demonstrating:

```text
Trace construction
structured event creation
Tier 1 operation helpers
generic trace.log()
text rendering
console/file emission
program START/END lifecycle
failure lifecycle
step scopes
nested step context
duration measurement
```

Only enough implementation should be created to exercise these behaviors realistically.

## 10. Acceptance Programs

The prototype will ultimately be exercised against six predefined statistical-programming examples.

These acceptance cases are deliberately chosen to stress different parts of the TRACE API.

### 10.1 Demographics Table

Expected to exercise:

```text
READ
FILTER
DERIVE
AGGREGATE
VALIDATE
OUTPUT
STEP
```

Primary questions:

- Does the basic TLF API remain concise?
- Does derivation logging feel natural?
- Does aggregation terminology work well?
- Do steps improve readability without creating noise?

### 10.2 Adverse Event Summary Table

Expected to exercise:

```text
READ
FILTER
MERGE
AGGREGATE
VALIDATE
OUTPUT
```

Primary questions:

- Is `merge()` understandable and sufficiently expressive?
- Are row-count metrics useful without being cumbersome?
- Does the API work naturally for common safety-table workflows?

### 10.3 Subject Listing

Expected to exercise:

```text
READ
FILTER
SORT
TRANSFORM
OUTPUT
```

Primary questions:

- Is the distinction between `DERIVE` and `TRANSFORM` clear?
- Does TRACE remain lightweight in simple listing programs?
- Does sorting deserve first-class instrumentation in practice?

### 10.4 Kaplan-Meier Figure

Expected to exercise:

```text
READ
FILTER
ANALYZE
VALIDATE
OUTPUT
```

Primary questions:

- Does `ANALYZE` feel like the correct abstraction for statistical procedures?
- Are analysis methods expressible without excessive metadata?
- Can figure-generation workflows use the same event model naturally?

### 10.5 ADaM Derivation

Expected to exercise:

```text
READ
SORT
FILTER
MERGE
DERIVE
TRANSFORM
VALIDATE
OUTPUT
```

Primary questions:

- Does the vocabulary remain clear in a derivation-heavy program?
- Are `DERIVE` and `TRANSFORM` distinct enough in realistic use?
- Does the API become too verbose in longer programming workflows?

This is expected to be one of the strongest stress tests of the API.

### 10.6 Independent QC Comparison

Expected to exercise:

```text
READ
CHECK
VALIDATE
OUTPUT
```

Primary questions:

- Is the `CHECK` versus `VALIDATE` distinction intuitive?
- Does TRACE support QC workflows without inventing QC-specific operations?
- Are pass/fail semantics useful for independent programming review?

## 11. Acceptance-Case Freeze

The six acceptance programs above are the initial prototype test suite at the workflow level.

Do not replace them with easier examples merely because an API feels awkward.

Additional examples may be added only when they reveal a materially different semantic workflow.

The acceptance set exists specifically to prevent scope drift and cherry-picked validation.

## 12. What Success Looks Like

The prototype is successful if the acceptance programs demonstrate that:

- TRACE calls remain visually subordinate to statistical code;
- one meaningful statistical operation generally maps to one TRACE call;
- canonical vocabulary is understandable in context;
- Tier 1 helpers cover the common workflows;
- `trace.log()` handles legitimate edge cases without becoming the default;
- START/END lifecycle messages are useful in real execution;
- step instrumentation improves larger programs;
- structured events can produce readable text logs;
- runtime analytical objects are not required by TRACE Core;
- the API does not require Python logging knowledge.

## 13. What Failure Looks Like

The prototype has also succeeded if it clearly reveals design problems.

Examples include:

- repeated awkward parameter patterns;
- ambiguity between core operations;
- excessive TRACE-to-program line ratio;
- generic logging used more often than Tier 1 helpers;
- inability to render useful messages from the event model;
- confusing lifecycle behavior;
- step instrumentation that creates excessive noise;
- frequent need to bypass canonical vocabulary;
- strong pressure to pass dataframe objects into Core.

These findings should trigger API revision rather than implementation workarounds.

## 14. Prototype Findings Requirement

After the acceptance programs are run, create:

```text
docs/design/reference-prototype-findings.md
```

The findings document should include:

```text
What worked
What felt awkward
What should change
What should remain frozen
What should be deferred
```

No decision should be made to promote the prototype into the real `v0.1` implementation before this review is complete.

## 15. Production Promotion Rule

The reference prototype must not silently become the production implementation.

Promotion requires an explicit decision after the prototype findings review.

At that point, the project may:

1. retain selected prototype code;
2. refactor selected components;
3. rewrite the implementation against the validated API;
4. reopen one or more design phases.

The default assumption remains that prototype internals are disposable.

## 16. Sprint 0 Output

Sprint 0 produces design documentation only.

No meaningful Python implementation should be added during this sprint.

The expected output is:

```text
docs/design/reference-prototype.md
```

## 17. Sprint 0 Acceptance Criteria

Sprint 0 is complete when:

1. the prototype is explicitly designated disposable;
2. validation goals are documented;
3. non-goals are documented;
4. the six acceptance programs are frozen;
5. scope-creep rules are documented;
6. success and failure criteria are defined;
7. prototype code has no production compatibility commitment;
8. no meaningful Python implementation has begun.

