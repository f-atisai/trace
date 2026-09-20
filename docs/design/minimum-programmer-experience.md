# TRACE Phase 2 — Minimum Programmer Experience

**Phase:** 2 — Design the Minimum Programmer Experience  
**Status:** Draft normative UX specification  
**Scope:** Programmer-facing experience; public signatures are owned by [TRACE Tier 1 API Specification](tier-1-api.md)

## 1. Purpose

TRACE should be easy to add to an existing statistical program without changing its fundamental structure.

> **A programmer should still recognize the original statistical program immediately after TRACE is added.**

TRACE complements statistical code; it does not become the dominant abstraction.

## 2. Programmer experience contract

TRACE v0.x should satisfy these principles:

1. **One-line routine setup.** Normal use should begin approximately with `trace = Trace("T14_01")`; users should not configure Python logging handlers or formatters.
2. **TRACE does not own transformations.** pandas, Polars, SQL, or ordinary Python continues to perform the statistical work. TRACE records the execution semantics.
3. **One TRACE call per meaningful operation.** Structured events must not require multi-call event-construction ceremony.
4. **Common calls stay short.** Routine instrumentation should ask only for information needed to identify the operation and useful evidence.
5. **Meaning is explicit.** The programmer selects the semantic operation (`filter`, `derive`, `aggregate`, and so on); TRACE should not guess analytical intent from implementation syntax.
6. **Explicit diagnostics are acceptable initially.** Automatic integrations may reduce metric friction later, but Core remains usable without runtime-object inspection.
7. **TRACE stays visually subordinate.** If instrumentation approaches the size or complexity of the statistical code, the API is too intrusive.
8. **API language follows the canonical vocabulary.** Generic infrastructure verbs such as `log_event()` should not be the normal programmer experience.
9. **No Python logging knowledge is required.** Python's logging infrastructure is an implementation detail for routine users.
10. **Incremental adoption is valid.** A program may instrument only the operations that provide useful execution evidence.

The canonical vocabulary is defined in [TRACE Core Operations v0.1](../framework/core-operations-v0.1.md); exact method signatures belong to [TRACE Tier 1 API Specification](tier-1-api.md).

## 3. Benchmark

A normal program might contain:

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

TRACE should be addable without restructuring that program:

```python
from trace_tlf import Trace

trace = Trace("T14_01")

adsl = pd.read_csv("adsl.csv")
trace.read("ADSL", source="adsl.csv", rows=len(adsl), columns=len(adsl.columns))

safety = adsl.loc[adsl["SAFFL"] == "Y"].copy()
trace.filter("ADSL", "SAFFL == 'Y'", before=len(adsl), after=len(safety))

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
trace.aggregate("ADSL", by=["TRT01A", "AGEGR1"], result="summary")

summary.to_excel("T14_01.xlsx")
trace.output("T14_01", "T14_01.xlsx")
```

This is approximately the upper bound of acceptable routine friction for TRACE v0.x.

## 4. Call placement

When an operation is logged manually, place the TRACE call after the operation it describes:

```python
safety = adsl.loc[adsl["SAFFL"] == "Y"].copy()
trace.filter("ADSL", "SAFFL == 'Y'", before=len(adsl), after=len(safety))
```

This avoids recording successful completion before the underlying operation has actually succeeded.

Lifecycle and integration features may automate some evidence collection, but they should preserve this execution truthfulness.

## 5. What TRACE should avoid

The minimum experience should not require:

```text
manual TraceEvent construction
handlers or formatters
mandatory decorators
mandatory context managers
runtime dataframe ownership
variable-name introspection
workflow orchestration
logging every line of statistical code
```

Optional lifecycle and step context managers are useful when they clarify execution structure; they are not prerequisites for ordinary operation logging.

## 6. Evaluation criteria

A proposed API or feature should be questioned if it:

- substantially increases instrumentation relative to the statistical code;
- requires logging terminology instead of statistical-programming terminology;
- forces a specific dataframe backend;
- makes partial adoption difficult;
- asks the programmer to repeat information TRACE already owns; or
- creates log events that provide little analytical or reviewer value.

These criteria should be tested against realistic TLF, ADaM, QC, and analysis workflows rather than toy examples alone.

## 7. Related specifications

- [TRACE Core Operations v0.1](../framework/core-operations-v0.1.md) — canonical vocabulary.
- [TRACE Tier 1 API Specification](tier-1-api.md) — public method signatures.
- [TRACE Phase 4 — Object vs Operation](object-vs-operation.md) — semantic Core and runtime-integration boundary.
- [TRACE Phase 6 — Configuration](configuration.md) — routine construction and configuration.
- [TRACE Reviewer Experience](reviewer-experience.md) — evidence that instrumentation should expose to reviewers.
