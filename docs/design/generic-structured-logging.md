# TRACE Phase 5 — Generic Structured Logging

**Phase:** 5 — Design Generic Structured Logging  
**Status:** Draft normative API specification  
**Scope:** Secondary structured-event APIs and escape-hatch behavior

## 1. Purpose

TRACE needs an escape hatch for meaningful statistical-programming events that do not fit cleanly into a Tier 1 helper.

The preferred API remains operation-specific:

```python
trace.derive("AGEGR1")
trace.filter("ADSL", "SAFFL == 'Y'")
trace.validate("ADSL", "USUBJID uniqueness", passed=True)
```

But programmers must also be able to create a valid TRACE Event directly.

The generic API exists to prevent TRACE from becoming restrictive.

> **Generic logging extends the TRACE vocabulary model; it does not bypass it.**

---

## 2. Primary Generic API

The recommended generic API is:

```python
trace.log(
    operation,
    *,
    object=None,
    action,
    metrics=None,
    details=None,
    status=None,
)
```

Example:

```python
trace.log(
    "DERIVE",
    object="AGEGR1",
    action="derived",
)
```

Richer example:

```python
trace.log(
    "DERIVE",
    object="AGEGR1",
    action="derived from AGE",
    details={
        "dataset": "ADSL",
        "method": "cut at 65 years",
    },
)
```

The method should create the same internal `TraceEvent` shape used by Tier 1 helpers.

---

## 3. Why `trace.log()` Is Secondary

The following remains preferred:

```python
trace.derive(
    "AGEGR1",
    dataset="ADSL",
    source="AGE",
)
```

over:

```python
trace.log(
    "DERIVE",
    object="AGEGR1",
    action="derived",
    details={
        "dataset": "ADSL",
        "source": "AGE",
    },
)
```

Why:

- helper methods encode canonical semantics;
- helpers provide operation-specific parameter names;
- helpers can derive standard metrics;
- helpers are easier to review;
- helpers are easier to document;
- helpers produce more consistent events;
- helpers protect users from schema drift.

`trace.log()` is an escape hatch, not the normal programming style.

---

# 4. Generic API Contract

## Proposed signature

```python
trace.log(
    operation,
    *,
    object=None,
    action,
    metrics=None,
    details=None,
    status=None,
)
```

### `operation`

Required canonical TRACE operation.

Examples:

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

Potential lifecycle operations such as `START` and `END` should normally be produced internally rather than manually.

### `object`

Optional semantic object identifier.

Examples:

```text
ADSL
AGEGR1
T14_01
OS
Safety Population
```

The generic API must follow the Phase 4 rule: `object` is semantic, not a runtime dataframe reference.

### `action`

Required concise description of what occurred.

Examples:

```text
derived
reconciled against external specification
mapped to reporting category
prepared for downstream analysis
```

### `metrics`

Optional structured quantitative evidence.

Example:

```python
metrics={
    "before": 754,
    "after": 720,
}
```

### `details`

Optional structured supplementary metadata.

Example:

```python
details={
    "dataset": "ADSL",
    "source": "AGE",
}
```

### `status`

Optional TRACE status.

Exact accepted status values are governed by the Phase 0 status model and later status hardening.

---

# 5. Generic API Must Use Canonical Operations

The escape hatch should not allow ad hoc operation names by default.

Bad:

```python
trace.log(
    "SUBSET",
    object="ADSL",
    action="safety population selected",
)
```

Preferred:

```python
trace.log(
    "FILTER",
    object="ADSL",
    action="safety population selected",
)
```

This preserves the value of the controlled vocabulary.

If users can invent arbitrary operation strings routinely, TRACE loses one of its main benefits.

---

# 6. Unknown Operation Behavior

The default behavior should be strict.

Example:

```python
trace.log(
    "SUBSET",
    object="ADSL",
    action="safety population selected",
)
```

should fail clearly because `SUBSET` is not a canonical TRACE operation.

Conceptually:

```text
UnknownOperationError:
'SUBSET' is not a TRACE operation.
Use 'FILTER' for row-selection events.
```

The exact exception type and suggestion mechanism are implementation details.

The important design rule is:

> **The generic API is flexible in event content, not in canonical vocabulary.**

---

# 7. Why Not Allow Arbitrary Operations?

Allowing:

```python
trace.log("WHATEVER", ...)
```

would create several problems:

- vocabulary fragmentation;
- inconsistent logs across programmers;
- hard-to-query execution histories;
- unstable downstream JSON/manifest consumers;
- duplicate semantics such as `JOIN`, `MERGE`, and `COMBINE`;
- reduced value of TRACE as a standard.

When a real semantic gap is discovered, the right response is to evaluate a vocabulary extension deliberately.

---

# 8. Generic Events Must Remain Structured

Avoid a generic API such as:

```python
trace.log("Derived AGEGR1 from AGE using cut at 65")
```

That is merely string logging.

The preferred generic form is structured:

```python
trace.log(
    "DERIVE",
    object="AGEGR1",
    action="derived",
    details={
        "source": "AGE",
        "method": "cut at 65 years",
    },
)
```

Human-readable text remains a rendering of the event.

---

# 9. Relationship to Tier 1 Helpers

Tier 1 helpers should conceptually normalize into the generic event path.

For example:

```python
trace.derive(
    "AGEGR1",
    dataset="ADSL",
    source="AGE",
)
```

could conceptually become:

```python
trace.log(
    "DERIVE",
    object="AGEGR1",
    action="created",
    details={
        "dataset": "ADSL",
        "source": "AGE",
    },
)
```

Likewise:

```python
trace.filter(
    "ADSL",
    "SAFFL == 'Y'",
    before=754,
    after=720,
)
```

could normalize to:

```python
trace.log(
    "FILTER",
    object="ADSL",
    action="SAFFL == 'Y' applied",
    metrics={
        "before": 754,
        "after": 720,
        "removed": 34,
    },
)
```

This suggests an implementation architecture:

```text
Tier 1 helper
      ↓
operation-specific normalization
      ↓
generic structured event creation
      ↓
TraceEvent
      ↓
renderers / handlers
```

However, `trace.log()` itself should not necessarily be the literal internal implementation function. The public API and internal event factory may remain separate.

---

# 10. Should TRACE Provide `trace.info()`?

A possible secondary API is:

```python
trace.info(
    operation="DERIVE",
    object="AGEGR1",
    action="derived",
)
```

This is understandable to Python developers, but it introduces an important problem:

```text
operation
and
severity
```

are separate concepts in TRACE.

A severity-first API encourages users to think in Python logging terms rather than TRACE semantic terms.

Compare:

```python
trace.info(
    operation="DERIVE",
    object="AGEGR1",
    action="derived",
)
```

with:

```python
trace.log(
    "DERIVE",
    object="AGEGR1",
    action="derived",
)
```

The second keeps the operation as the primary concept.

---

# 11. Recommendation on Severity Convenience Methods

For Tier 1 and the first generic API version, do **not** make:

```python
trace.debug()
trace.info()
trace.warning()
trace.error()
trace.critical()
```

part of the main documented surface.

Instead, keep:

```python
trace.log(...)
```

as the generic structured API.

Severity inference should remain TRACE's responsibility where possible.

A future advanced API may allow explicit severity:

```python
trace.log(
    "CHECK",
    object="ADSL",
    action="unexpected category observed",
    severity="WARNING",
)
```

but this should be introduced only after Phase 6 severity rules are frozen.

Therefore, Phase 5 does not yet add `severity` to the public signature.

---

# 12. Why Severity Is Deferred

Phase 0 distinguishes:

```text
Severity
Status
Operation
```

These concepts should remain separate.

For example:

```text
Operation = VALIDATE
Status    = FAIL
Severity  = WARNING
```

or:

```text
Operation = END
Status    = FAIL
Severity  = ERROR
```

Before the severity inference policy is defined, exposing explicit severity broadly would prematurely freeze behavior.

Phase 5 therefore keeps generic logging semantic-first.

---

# 13. `object` Naming

The generic API uses:

```python
object="AGEGR1"
```

because it maps directly to the Phase 0 event field.

This is one place where using `object` is semantically clearer than `name`.

Although `object` is also a Python built-in name, keyword parameters can technically use it.

However, for implementation quality and consistency, an internal method signature may prefer:

```python
object_name=None
```

while the external contract could still expose `object`.

This decision should be resolved during implementation hardening.

A competing option is:

```python
trace.log(
    "DERIVE",
    name="AGEGR1",
    action="derived",
)
```

but that weakens alignment with the domain model.

Current Phase 5 recommendation: retain `object` in the generic API specification and revisit only if typing/implementation ergonomics justify a rename.

---

# 14. Required `action`

The generic API should require `action`.

Bad:

```python
trace.log(
    "DERIVE",
    object="AGEGR1",
)
```

This does not explain what happened.

Preferred:

```python
trace.log(
    "DERIVE",
    object="AGEGR1",
    action="derived",
)
```

Tier 1 helpers can supply canonical actions automatically.

For example:

```python
trace.derive("AGEGR1")
```

can generate:

```text
action = "created"
```

The generic API cannot safely assume the same thing in every custom case.

---

# 15. Object May Be Optional

Some valid generic events may not have a meaningful primary object.

Example concept:

```python
trace.log(
    "CHECK",
    action="environment configuration inspected",
    details={"python": "3.12"},
)
```

Therefore `object` should remain optional.

However, operation-specific validation may require it for some operations in the future.

For example:

```text
FILTER
DERIVE
OUTPUT
```

usually have an obvious object.

Strict operation-specific requirements are better handled by Tier 1 helpers.

The generic API should remain somewhat broader.

---

# 16. Metrics and Details

`metrics` and `details` serve different purposes.

## Metrics

Quantitative observations:

```python
metrics={
    "before": 754,
    "after": 720,
    "removed": 34,
}
```

## Details

Descriptive structured metadata:

```python
details={
    "dataset": "ADSL",
    "source": "AGE",
    "method": "cut at 65 years",
}
```

Do not mix them casually.

Bad:

```python
details={
    "before": 754,
    "after": 720,
}
```

when those values are clearly execution metrics.

This distinction supports consistent downstream processing.

---

# 17. Mapping-Only Structured Fields

Phase 5 strengthens the recommendation that:

```text
metrics
details
```

should be mappings.

Conceptually:

```python
Mapping[str, JSONScalar | JSONValue]
```

rather than arbitrary Python objects.

This makes generic events:

- serializable;
- predictable;
- backend-independent;
- safe for JSON/JSONL;
- easier to validate.

Exact recursive JSON-compatible typing is deferred to implementation design.

---

# 18. Example: Unsupported Clinical Workflow

Suppose a programmer reconciles a treatment mapping against an external specification.

No Tier 1 helper perfectly describes that semantic action.

A reasonable event might be:

```python
trace.log(
    "CHECK",
    object="Treatment Mapping",
    action="reconciled against randomization specification",
    metrics={
        "mapped": 754,
        "unmapped": 0,
    },
    details={
        "source": "randomization_spec.xlsx",
    },
)
```

If the reconciliation enforces an acceptance criterion, `VALIDATE` may be better:

```python
trace.log(
    "VALIDATE",
    object="Treatment Mapping",
    action="randomization mapping complete",
    status="SUCCESS",
    metrics={
        "mapped": 754,
        "unmapped": 0,
    },
)
```

The generic API supports edge cases while still using canonical TRACE semantics.

---

# 19. Example: Protocol-Specific Derivation

A study may have a highly protocol-specific categorization that does not warrant a new TRACE operation.

Use:

```python
trace.log(
    "DERIVE",
    object="RESPCAT",
    action="protocol response category derived",
    details={
        "protocol_rule": "Section 9.4.2",
    },
)
```

Do not create:

```text
PROTOCOL_DERIVE
RESPONSE_MAP
CATEGORY_RULE
```

as new operations.

---

# 20. Example: Custom Output Preparation

Suppose an intermediate reporting artifact is prepared but not yet written.

If `TRANSFORM` best represents the action:

```python
trace.log(
    "TRANSFORM",
    object="T14_01 body",
    action="formatted for reporting",
    details={
        "orientation": "landscape",
    },
)
```

This avoids adding a new `FORMAT` core operation prematurely.

---

# 21. Generic API Is Not Raw Message Logging

TRACE should not initially expose a primary method like:

```python
trace.info("Starting demographic calculations")
```

as part of its central design.

That style has no structured operation, object, metrics, or status.

It recreates the inconsistency TRACE is intended to solve.

If raw diagnostic messages are ever supported, they should live in a clearly separate advanced/debugging surface and should not be confused with canonical TRACE Events.

---

# 22. Structured Logging Hierarchy

The intended API hierarchy is:

```text
Tier 1 — Preferred semantic helpers

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

        ↓

Tier 2 — Generic structured event

trace.log()

        ↓

Advanced infrastructure — later

event factories
context binding
explicit severity
custom renderers
handlers
integrations
```

This hierarchy should be reflected in documentation.

---

# 23. Documentation Rule

Examples and tutorials should overwhelmingly use Tier 1 helpers.

Good documentation ratio conceptually:

```text
90% Tier 1 helpers
10% trace.log() edge cases
```

The exact ratio is not contractual.

The intent is to prevent generic logging from becoming the default style simply because it is flexible.

---

# 24. Generic API Validation

`trace.log()` should validate:

```text
operation is canonical
action is non-empty
metrics are structured
details are structured
status is valid when present
values are serializable or normalizable
```

It should not silently accept malformed events that later break JSON rendering or execution summaries.

---

# 25. Case Handling for Operations

The API may accept canonical strings such as:

```python
trace.log(
    "DERIVE",
    object="AGEGR1",
    action="derived",
)
```

A future enum may also be supported:

```python
trace.log(
    Operation.DERIVE,
    object="AGEGR1",
    action="derived",
)
```

Whether lowercase strings such as:

```python
"derive"
```

are normalized automatically is deferred.

The canonical serialized value should remain:

```text
DERIVE
```

---

# 26. Generic API and Vocabulary Evolution

When programmers repeatedly use:

```python
trace.log(...)
```

for the same semantic pattern, that is useful design evidence.

For example, if many programs repeatedly require:

```python
trace.log(
    "TRANSFORM",
    object=...,
    action="...",
)
```

for a distinct operation that cannot be expressed cleanly, TRACE maintainers should evaluate whether the vocabulary has a genuine gap.

Therefore generic logging also serves as a pressure-release valve during API evolution.

It prevents premature vocabulary expansion while giving users a supported path.

---

# 27. Phase 5 Decisions

**P5-01** — TRACE provides a generic structured-event method:

```python
trace.log(...)
```

**P5-02** — `trace.log()` is Tier 2 / secondary API.

**P5-03** — Tier 1 operation-specific helpers remain the preferred interface.

**P5-04** — The generic API uses canonical TRACE operations and does not permit ad hoc operation vocabulary by default.

**P5-05** — `action` is required for generic events.

**P5-06** — `object` is optional and semantic, never a required runtime dataframe reference.

**P5-07** — `metrics` and `details` remain separate structured mappings.

**P5-08** — Generic events normalize to the same `TraceEvent` model as Tier 1 helpers.

**P5-09** — Severity-specific convenience methods such as `trace.info()` are not part of the initial recommended API.

**P5-10** — Explicit severity behavior is deferred until severity inference rules are designed.

**P5-11** — Raw unstructured message logging is not the purpose of `trace.log()`.

**P5-12** — Repeated generic-event patterns may inform future controlled vocabulary extensions.

---

# 28. Recommended Phase 5 API

```python
trace.log(
    operation,
    *,
    object=None,
    action,
    metrics=None,
    details=None,
    status=None,
)
```

Example:

```python
trace.log(
    "DERIVE",
    object="AGEGR1",
    action="derived",
)
```

Richer example:

```python
trace.log(
    "VALIDATE",
    object="Treatment Mapping",
    action="randomization mapping complete",
    status="SUCCESS",
    metrics={
        "mapped": 754,
        "unmapped": 0,
    },
    details={
        "source": "randomization_spec.xlsx",
    },
)
```

Preferred equivalent when a helper exists:

```python
trace.derive(
    "AGEGR1",
    dataset="ADSL",
    source="AGE",
)
```

---

# 29. Acceptance Criteria

Phase 5 is complete when:

1. TRACE has a generic structured escape hatch.
2. Generic logging uses the same event model as Tier 1 helpers.
3. canonical vocabulary remains enforced.
4. arbitrary operation strings are not the default.
5. generic logging does not require runtime dataframe objects.
6. `metrics` and `details` remain structured and distinct.
7. Tier 1 helpers remain clearly preferred.
8. raw string logging does not become the canonical API.
9. severity convenience methods remain deferred until severity policy is defined.
10. the generic API can represent unusual clinical-programming events without requiring vocabulary expansion.

---

# 30. Phase 5 Outcome

TRACE now has two clear programmer-facing levels:

```text
Preferred
    trace.derive(...)
    trace.filter(...)
    trace.validate(...)
    ...

Escape hatch
    trace.log(...)
```

The governing rule is:

> **A generic mechanism should prevent TRACE from becoming restrictive without encouraging programmers to abandon TRACE conventions.**
