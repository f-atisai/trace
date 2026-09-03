# TRACE Phase 2 — Minimum Programmer Experience

**Phase:** 2 — Design the Minimum Programmer Experience  
**Status:** Draft normative UX specification  
**Scope:** Programmer-facing experience only; exact public method signatures remain provisional

## 1. Purpose

TRACE should make execution logging easy to add to an existing statistical program without changing the program's fundamental structure.

The benchmark is a real TLF. TRACE should complement statistical code rather than become the dominant abstraction.

> A programmer should still recognize the original TLF immediately after TRACE is added.

## 2. Benchmark

Existing program:

```python
adsl = pd.read_csv("adsl.csv")

safety = adsl.loc[adsl["SAFFL"] == "Y"].copy()

safety["AGEGR1"] = pd.cut(
    safety["AGE"],
    bins=[0, 65, float("inf")],
    labels=["<65", ">=65"],
)

summary = (
    safety.groupby(["TRT01A", "AGEGR1"])
    .size()
    .reset_index(name="N")
)

summary.to_excel("T14_01.xlsx")
```

Acceptable TRACE-enhanced form:

```python
from trace_tlf import Trace

trace = Trace("T14_01")

adsl = pd.read_csv("adsl.csv")
trace.read(adsl, "ADSL")

safety = adsl.loc[adsl["SAFFL"] == "Y"].copy()
trace.filter(
    "ADSL",
    "SAFFL == 'Y'",
    before=len(adsl),
    after=len(safety),
)

safety["AGEGR1"] = pd.cut(
    safety["AGE"],
    bins=[0, 65, float("inf")],
    labels=["<65", ">=65"],
)
trace.derive("AGEGR1", dataset="ADSL", source="AGE")

summary = (
    safety.groupby(["TRT01A", "AGEGR1"])
    .size()
    .reset_index(name="N")
)
trace.aggregate(
    "ADSL",
    by=["TRT01A", "AGEGR1"],
    result="summary",
)

summary.to_excel("T14_01.xlsx")
trace.output("T14_01", "T14_01.xlsx")
```

This is approximately the maximum acceptable routine friction for TRACE v0.x.

## 3. Programmer Experience Contract

### PX-01 — One-line setup

Routine setup should be approximately:

```python
trace = Trace("T14_01")
```

A programmer should not need to configure handlers, formatters, propagation, streams, or logging dictionaries for normal use.

### PX-02 — TRACE does not own transformations

TRACE should not replace:

```python
safety = adsl.loc[adsl["SAFFL"] == "Y"].copy()
```

with a TRACE dataframe transformation wrapper.

The statistical operation remains ordinary pandas, Polars, SQL, or Python. TRACE records what happened.

### PX-03 — One TRACE call per meaningful operation

This is acceptable:

```python
safety = adsl.loc[adsl["SAFFL"] == "Y"].copy()

trace.filter(
    "ADSL",
    "SAFFL == 'Y'",
    before=len(adsl),
    after=len(safety),
)
```

This is not:

```python
trace.start_operation("FILTER")
trace.set_object("ADSL")
trace.set_action("SAFFL == 'Y'")
trace.set_metric("before", len(adsl))
trace.set_metric("after", len(safety))
trace.commit()
```

The internal event model may be structured without exposing event-construction ceremony.

### PX-04 — Common calls stay short

The common path should require only information TRACE cannot reliably infer.

Examples:

```python
trace.read(adsl, "ADSL")
trace.derive("AGEGR1", dataset="ADSL")
trace.output("T14_01", "T14_01.xlsx")
```

### PX-05 — Meaning is explicit

The programmer should normally tell TRACE the semantic operation:

```python
trace.filter(...)
```

rather than relying on TRACE to inspect pandas code and guess that a clinically meaningful filter occurred.

### PX-06 — Explicit metrics are acceptable initially

For v0.x, this is acceptable:

```python
trace.filter(
    "ADSL",
    "SAFFL == 'Y'",
    before=len(adsl),
    after=len(safety),
)
```

Automatic metric extraction may reduce friction later, but Phase 2 does not require magic.

### PX-07 — TRACE is visually subordinate

TRACE-specific code should usually remain clearly smaller than the statistical code it describes.

A script where TRACE doubles the program size is a warning sign.

### PX-08 — API language follows the canonical vocabulary

Prefer:

```python
trace.read(...)
trace.filter(...)
trace.derive(...)
trace.aggregate(...)
trace.validate(...)
trace.output(...)
```

Avoid exposing generic infrastructure verbs as the main experience:

```python
trace.log_event(...)
trace.emit_operation(...)
trace.register_dataframe_change(...)
```

### PX-09 — No Python logging knowledge required

Routine users should not need to know about:

```python
logging.getLogger(...)
logging.Handler
logging.Formatter
logger.propagate
```

TRACE may use Python logging internally. That is an implementation detail.

### PX-10 — Incremental adoption

A programmer should be able to instrument only selected parts of a program.

Partial TRACE coverage is valid and useful.

## 4. Call Placement

Preferred placement is immediately after the operation being described:

```python
safety = adsl.loc[adsl["SAFFL"] == "Y"].copy()

trace.filter(
    "ADSL",
    "SAFFL == 'Y'",
    before=len(adsl),
    after=len(safety),
)
```

This avoids falsely logging success if the underlying operation fails.

Lifecycle and decorator features may later automate success/failure capture.

## 5. Minimum Information by Operation

Phase 2 does not freeze exact signatures. It defines the minimum useful feel.

### READ

```python
trace.read(adsl, "ADSL")
```

Potentially inferable later:

```text
rows
columns
object type
```

### CHECK

```python
trace.check(
    "ADSL",
    "treatment groups inspected",
    groups=3,
)
```

### FILTER

```python
trace.filter(
    "ADSL",
    "SAFFL == 'Y'",
    before=len(adsl),
    after=len(safety),
)
```

### SORT

```python
trace.sort(
    "ADAE",
    by=["USUBJID", "AESTDTC"],
)
```

### DERIVE

```python
trace.derive(
    "AGEGR1",
    dataset="ADSL",
    source="AGE",
)
```

### TRANSFORM

```python
trace.transform(
    "AESTDTC",
    "parsed to analysis date",
)
```

### MERGE

```python
trace.merge(
    "ADAE",
    "ADSL",
    on="USUBJID",
    how="left",
    result="analysis",
)
```

### AGGREGATE

```python
trace.aggregate(
    "ADSL",
    by=["TRT01A", "AGEGR1"],
    result="summary",
)
```

### ANALYZE

```python
trace.analyze(
    "OS",
    method="Kaplan-Meier",
    population="ITT",
)
```

### VALIDATE

```python
trace.validate(
    "ADSL",
    "USUBJID uniqueness",
    passed=True,
)
```

### OUTPUT

```python
trace.output(
    "T14_01",
    "T14_01.xlsx",
)
```

## 6. Target Log

The benchmark TLF should yield something approximately like:

```text
INFO [READ]      [ADSL] loaded – N=754, Vars=16
INFO [FILTER]    [ADSL] SAFFL == 'Y' applied – N=754 → 720
INFO [DERIVE]    [AGEGR1] created – dataset=ADSL, source=AGE
INFO [AGGREGATE] [ADSL] summarized – by=TRT01A,AGEGR1, result=summary
INFO [OUTPUT]    [T14_01] written – T14_01.xlsx
```

The log should explain the execution without reproducing the entire program.

## 7. What TRACE Must Avoid

### Wrapper-driven programming

Avoid making proxy dataframes or TRACE-owned transformations the canonical path.

### Excessive metadata ceremony

Do not force users to manually provide every Phase 0 event field for normal calls.

### Logging every line

TRACE should instrument meaningful analytical steps, not incidental implementation details.

### Hidden semantic inference by default

TRACE should not assume every `groupby()` means `AGGREGATE` or every `assign()` means `DERIVE`.

Automatic evidence collection is safer than automatic semantic classification.

### Mandatory decorators

Decorators may exist later but should not be required.

### Mandatory context managers

Both forms should remain valid:

```python
trace = Trace("T14_01")
```

and potentially later:

```python
with Trace("T14_01") as trace:
    ...
```

## 8. Friction Budget

For a typical meaningful operation, acceptable overhead is usually:

```text
1 TRACE call
2–6 formatted lines
little duplicated metadata
no change to the statistical operation itself
```

The primary API must optimize for the statistical programmer, not for internal architectural elegance.

## 9. Five-Minute Adoption Test

A Python statistical programmer should be able to:

```python
from trace_tlf import Trace

trace = Trace("T14_01")
```

then add:

```python
trace.read(...)
trace.filter(...)
trace.derive(...)
trace.aggregate(...)
trace.output(...)
```

without first learning event classes, serializers, logging handlers, proxy dataframes, decorators, or context binding.

## 10. Progressive Disclosure

### Level 1 — Basic

```python
trace = Trace("T14_01")
trace.read(...)
trace.filter(...)
trace.output(...)
```

### Level 2 — Rich metadata

```python
trace.derive(
    "AGEGR1",
    dataset="ADSL",
    source="AGE",
    details=...,
)
```

### Level 3 — Lifecycle / steps

Potentially:

```python
with Trace("T14_01") as trace:
    with trace.step("Analysis population"):
        ...
```

### Level 4 — Integrations / automation

Potentially:

```text
automatic dataframe metrics
decorators
JSON output
execution manifests
context binding
```

A basic user should not need Levels 2–4 to benefit from TRACE.

## 11. Comparator Lesson

Phase 2 adopts the low-friction lesson from `pandas-log`:

> Instrumentation should not require rewriting the statistical program.

TRACE still preserves explicit semantic intent:

```text
ordinary statistical code
        ↓
explicit TRACE semantic event
        ↓
optional automatic metric enrichment
```

rather than:

```text
intercept implementation method
        ↓
infer semantic meaning
```

## 12. Programmer Experience Invariants

- A TRACE-enhanced TLF remains recognizably the original TLF.
- The statistical operation is not hidden inside TRACE.
- The normal path requires no Python logging knowledge.
- One meaningful operation normally requires no more than one TRACE call.
- TRACE calls use Phase 1 vocabulary directly.
- Advanced structured-event concepts remain hidden unless needed.
- Partial adoption is supported.
- TRACE calls normally follow successful completion of the operation they describe.
- Automatic metrics may reduce friction later without changing semantic intent.
- If TRACE visually dominates the source code, the API design has failed.

## 13. Phase 2 Decisions

**P2-01** — TRACE augments existing statistical code rather than replacing it.  
**P2-02** — Routine initialization requires approximately one line.  
**P2-03** — One meaningful operation normally maps to one TRACE call.  
**P2-04** — Operation methods directly reflect the Phase 1 vocabulary.  
**P2-05** — Exact structured-event construction is hidden from routine users.  
**P2-06** — Python logging internals are hidden from routine users.  
**P2-07** — Explicit semantic intent is preferred over automatic semantic inference.  
**P2-08** — Automatic metric extraction is permitted later as a friction-reduction mechanism.  
**P2-09** — Partial adoption is supported.  
**P2-10** — The benchmark TLF represents approximately the maximum acceptable routine friction.

## 14. Acceptance Criteria

Phase 2 is complete when:

1. A basic TLF remains clearly recognizable after TRACE is added.
2. TRACE does not own dataframe transformations.
3. Routine configuration requires no logging knowledge.
4. Each meaningful step needs at most one normal TRACE call.
5. Calls use statistical-programming terminology.
6. READ, FILTER, DERIVE, AGGREGATE, and OUTPUT fit naturally into the benchmark.
7. Explicit before/after metrics are easy to express.
8. Partial instrumentation is valid.
9. Advanced features are not prerequisites.
10. TRACE remains visually and conceptually subordinate to the statistical program.

## 15. Phase 2 Outcome

The minimum TRACE programmer experience is:

```text
configure once
      ↓
write ordinary statistical code
      ↓
add one concise TRACE event after meaningful operations
      ↓
receive consistent structured execution logging
```

> **TRACE should complement the code—not dominate it.**

This UX contract should guide Phase 3, where concrete public method signatures are designed.
