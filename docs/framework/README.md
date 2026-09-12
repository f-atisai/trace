# TRACE Framework

TRACE is a **semantic execution evidence framework for statistical programming**. It defines how meaningful execution activity is represented so programmers and reviewers can understand what happened during a run and reconcile that evidence with the program and its outputs.

The framework combines semantic events, observed diagnostics, and execution provenance. Structured logging is an implementation mechanism, not TRACE's purpose.

A clean TRACE execution does not establish statistical correctness or replace specification review, code review, output review, or independent QC.

## Specifications

- [`core-operations-v0.1.md`](core-operations-v0.1.md) defines the canonical statistical-operation vocabulary.
- [`reviewer-guide.md`](reviewer-guide.md) explains how to review a statistical program using TRACE.
- [`../design/domain-model.md`](../design/domain-model.md) defines the structured event model.
- [`../design/reviewer-experience.md`](../design/reviewer-experience.md) defines the reviewer model and diagnostic-evidence boundaries.
- [`../design/provenance.md`](../design/provenance.md) defines program-level execution provenance.

Concepts are defined in their authoritative documents rather than repeated here. See the [`docs/design` index](../design/README.md) for documentation ownership.
