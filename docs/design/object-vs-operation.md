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
    before=754,
    after=720,
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

The public API contract is maintained in [`tier-1-api.md`](tier-1-api.md). This document records the architecture decision behind that contract.

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
TEAE_SAFETY
demographics_summary
Overall survival
T14_01
```

They should survive implementation changes and remain meaningful to a reviewer.

TRACE must not inspect Python variable names and treat names such as `df`, `tmp`, or `merged_df` as authoritative analytical identities.

The event model and object field semantics are defined in [`domain-model.md`](domain-model.md).

## 4. Core versus integration

A Core call receives semantic identity plus structured evidence:

```python
trace.read(
    "ADSL",
    source="adsl.csv",
    rows=754,
    columns=16,
)
```

A future integration may inspect a runtime object and emit the equivalent event:

```python
trace.pandas.read(
    adsl,
    "ADSL",
    source="adsl.csv",
)
```

The integration may derive objective metadata such as row count, column count, missingness, or before/after dimensions. It must not redefine the operation's semantics.

The same rule applies to FILTER, MERGE, and other operations: object inspection may enrich an explicitly declared operation; it does not determine which TRACE operation occurred.

## 5. Data-minimization and retention

TRACE Core events must contain serializable semantic information and safe structured metadata, not retained runtime objects.

Core must not retain DataFrames, LazyFrames, Arrow tables, database relations, model objects, file handles, or logger objects inside events.

Integrations should default to metadata rather than raw clinical data. For example:

```text
rows=754
columns=16
missing=3
```

is appropriate; retaining row values or subject-level records is not.

## 6. Dependency direction

Runtime integrations depend on Core, never the reverse:

```text
integrations → core
```

Core must remain usable without pandas, Polars, PyArrow, or another dataframe dependency installed.

A future package may expose optional integrations through extras, but packaging details are not part of this decision.

## 7. Consequences

This decision means:

- semantic identities remain stable across backends;
- Core stays lightweight and backend-independent;
- observed diagnostics can be added through integrations without changing operation meaning;
- TRACE does not become a dataframe transformation framework;
- runtime-object inspection remains optional; and
- public API changes belong in the API specification rather than this architecture record.

The main cost is that Core callers may initially provide some diagnostics explicitly. Phase 10's reviewer work may refine how asserted and observed evidence are distinguished without reopening this boundary unnecessarily.

## 8. Related specifications

- [`domain-model.md`](domain-model.md) — event structure and semantic object identity.
- [`../framework/core-operations-v0.1.md`](../framework/core-operations-v0.1.md) — canonical operation meanings.
- [`tier-1-api.md`](tier-1-api.md) — public operation signatures.
- [`reviewer-experience.md`](reviewer-experience.md) — observed diagnostics and reviewer-facing evidence.

Future documents should reference this decision rather than reproduce the Core-versus-integration rationale.
