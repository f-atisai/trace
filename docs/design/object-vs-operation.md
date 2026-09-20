# TRACE Phase 4 — Object vs Operation

**Phase:** 4 — Resolve the Object-versus-Operation API Boundary  
**Status:** Accepted architecture decision  
**Scope:** Core API ownership boundary, semantic object identity, and integration responsibilities

## 1. Decision

TRACE Core uses a semantic, object-independent API.

Canonical style:

```python
trace.filter(
    "ADSL",
    "SAFFL == 'Y'",
    before=254,
    after=249,
)
```

not:

```python
trace.filter(
    adsl,
    "SAFFL == 'Y'",
    name="ADSL",
)
```

> **TRACE Core records semantic execution events. Integrations may inspect runtime objects to enrich those events.**

The public API contract is maintained in [TRACE Tier 1 API Specification](tier-1-api.md). This document records the architecture decision behind that contract.

## 2. Why this boundary exists

TRACE is intended to work across pandas, Polars, PyArrow, SQL, DuckDB, custom dataset classes, and future statistical-programming runtimes.

Requiring concrete dataframe objects in Core would introduce backend-specific type handling, optional dependency complexity, object-retention risks, and pressure to infer analytical meaning from implementation details.

The boundary therefore separates two concerns:

```text
semantic declaration       evidence collection
        │                          │
        ▼                          ▼
   TRACE Core              optional integration
        │                          │
        └──────────────┬───────────┘
                       ▼
                  TraceEvent
```

Core defines **what an operation means**. Integrations may collect objective runtime evidence about that operation.

## 3. Semantic object identity

In TRACE Core, `"ADSL"` is a semantic identifier, not a Python variable reference.

Useful identifiers include:

```text
ADSL
ADAE
ADTTE
TEAE_SAFETY
Safety Population
Overall Survival
demographics_summary
T14_01
```

They should survive implementation changes and remain meaningful to a reviewer.

TRACE must not inspect Python variable names and treat names such as `df`, `tmp`, or `merged_df` as authoritative analytical identities.

When an operation acts on one object and produces a separately meaningful result, both identities may matter. For example:

```text
source/object: ADSL
condition:     SAFFL == 'Y'
result:        Safety Population
```

The source remains the event object; the named population is the result of the filter. TRACE does not need a separate `POPULATION` operation.

The event model and object field semantics are defined in [TRACE Domain Model Specification](domain-model.md).

## 4. Core versus integration

A Core call receives semantic identity plus structured evidence:

```python
trace.read(
    "ADSL",
    source="analysis/adsl.parquet",
    rows=254,
    columns=16,
)
```

A future integration may inspect a runtime object and emit the equivalent event:

```python
trace.pandas.read(
    adsl,
    "ADSL",
    source="analysis/adsl.parquet",
)
```

The integration may derive objective metadata such as row count, column count, missingness, or before/after dimensions. It must not redefine the operation's semantics.

The same rule applies to FILTER, MERGE, and other operations: object inspection may enrich an explicitly declared operation; it does not determine which TRACE operation occurred.

## 5. Evidence origin

Core and integrations can produce diagnostics with different evidentiary strength.

```text
SUPPLIED   caller passed the value to TRACE
OBSERVED   TRACE or an integration inspected runtime state or an artifact
DERIVED    TRACE calculated the value from diagnostics with known origins
```

For example:

```python
trace.read("ADSL", rows=len(adsl))
```

records a **supplied** row count from the perspective of TRACE Core. A pandas integration that directly inspects `adsl` may record the equivalent count as **observed**.

The semantic event can be identical while the diagnostic origin differs. Structured TRACE representations must preserve that distinction; the concise text renderer need not label every metric inline.

The governing diagnostic-evidence model is defined in [TRACE Reviewer Experience](reviewer-experience.md).

## 6. Data minimization and retention

TRACE Core events must contain serializable semantic information and safe structured metadata, not retained runtime objects.

Core must not retain DataFrames, LazyFrames, Arrow tables, database relations, model objects, file handles, or logger objects inside events.

Integrations should default to metadata rather than raw clinical data. For example:

```text
rows=254
columns=16
duplicate_subjects=2
```

is appropriate; retaining row values or subject-level records is not.

## 7. Dependency direction

Runtime integrations depend on Core, never the reverse:

```text
integrations → core
```

Core must remain usable without pandas, Polars, PyArrow, or another dataframe dependency installed.

A future package may expose optional integrations through extras, but packaging details are not part of this decision.

## 8. Consequences

This decision means:

- semantic identities remain stable across backends;
- Core stays lightweight and backend-independent;
- Core may record supplied diagnostics without representing them as independently observed;
- integrations may produce observed diagnostics without changing operation meaning;
- TRACE does not become a dataframe transformation framework;
- runtime-object inspection remains optional; and
- public API changes belong in the API specification rather than this architecture record.

The main cost is that Core callers may initially provide some diagnostics explicitly. That trade-off is preferable to coupling the semantic API to a dataframe backend.

## 9. Related specifications

- [TRACE Domain Model Specification](domain-model.md) — event structure and semantic object identity.
- [TRACE Core Operations v0.1](../framework/core-operations-v0.1.md) — canonical operation meanings.
- [TRACE Tier 1 API Specification](tier-1-api.md) — public operation signatures.
- [TRACE Reviewer Experience](reviewer-experience.md) — diagnostic origins and reviewer-facing evidence.
- [TRACE Execution Provenance](provenance.md) — program-level execution and artifact provenance.

Future documents should reference this decision rather than reproduce the Core-versus-integration rationale.
