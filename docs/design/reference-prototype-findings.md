# TRACE Reference Prototype Findings

**Sprint:** 9 — Friction review  
**Status:** Design review after the reference prototype

The six Sprint 8 programs were reviewed as API exercises rather than implementation tests. The measurements are intentionally approximate: “statistical-program lines” is a friction indicator excluding imports, synthetic fixture construction, TRACE calls, and step declarations.

## Prototype measurements

| Prototype | Emitted TRACE lines | Statistical-program lines | Semantic TRACE calls | Explicit steps | Approx. calls per logical stage |
| --- | ---: | ---: | ---: | ---: | --- |
| `demographics_table.py` | 18 | ~16 | 6 | 5 | Read 1; Population 1; Derive 1; Statistics 2; Output 1 |
| `adverse_events_table.py` | 10 | ~22 | 8 | 0 | Read 2; Population 2; Merge 1; Statistics 2; Output 1 |
| `subject_listing.py` | 7 | ~6 | 5 | 0 | Read 1; Prepare 3; Output 1 |
| `kaplan_meier_figure.py` | 7 | ~25 | 5 | 0 | Read 1; Population 1; Analysis 2; Output 1 |
| `adam_derivation.py` | 26 | ~38 | 12 | 6 | Read 2; Prepare 2; Merge 1; Derive 4; Validate 2; Output 1 |
| `qc_comparison.py` | 9 | ~14 | 7 | 0 | Read 2; QC checks 4; Output 1 |

Across the prototypes there are **77 emitted TRACE lines**, **43 semantic TRACE calls**, and **11 explicit steps**. The ADaM derivation is the strongest stress test: 12 semantic calls plus five step scopes produce 26 emitted log lines.

Operation usage: READ 9, CHECK 2, FILTER 6, SORT 2, DERIVE 4, TRANSFORM 2, MERGE 2, AGGREGATE 2, ANALYZE 1, VALIDATE 7, OUTPUT 6. `trace.log()` was not needed, which is a positive result for the Tier 1 vocabulary.

# What worked

The semantic-helper model held up well. TRACE remains observational: pandas/statistical code performs the work and a nearby TRACE call records its meaning. `filter()`, `derive()`, `aggregate()`, `validate()`, and `output()` were especially natural.

The Phase 4 object-independent boundary also held. Semantic names such as `ADSL`, `ADAE`, `ADLB`, `TEAE_SAFETY`, and `km_curve` were sufficient; none of the programs needed TRACE Core to receive a DataFrame.

`filter(name, condition, before=..., after=...)` is concise and useful. Before/after counts are routine statistical-programming evidence, and the rendered `N=before → after` form is compact.

`derive()` fit true analysis-variable derivations such as `AGEGR1`, `ADY`, `ABLFL`, and `CHG`. `dataset`, `source`, and `method` are meaningful traceability metadata.

CHECK and VALIDATE remained distinct in the QC program. CHECK naturally recorded observations (“row count observed”), while VALIDATE tested expectations and produced PASS/FAIL. Keep the rule: **CHECK observes; VALIDATE asserts**.

AGGREGATE and ANALYZE were also distinguishable in the tested cases: grouped counts used AGGREGATE; Kaplan–Meier used ANALYZE. No missing operation emerged.

Program lifecycle was useful and unobtrusive at program scope. Steps were useful in the larger programs because `step` and `step_path` provide meaningful structured context without decorators.

# What felt awkward

## MERGE is too easy to over-specify

`merge()` is the most verbose helper. A realistic call can repeat `on`, `how`, result identity, three row counts, and matching diagnostics immediately after the actual dataframe merge.

More importantly, `matched`, `unmatched_left`, and `unmatched_right` are semantically ambiguous. In the AE program, “matched” naturally meant distinct subjects; in the ADaM program it naturally meant matched rows. The API does not state the unit. That is a design flaw, not merely verbosity.

`left_rows`, `right_rows`, and `result_rows` are unambiguous and useful. The generic matched/unmatched fields are not.

## Repeated parameters are deliberate but visible

`sort(by=...)`, `aggregate(by=...)`, `merge(on=..., how=...)`, and `analyze(method=...)` repeat information already present in the statistical call. Core TRACE cannot infer this without owning or inspecting the operation, so the repetition is acceptable for now. It is evidence for optional integrations later, not for passing runtime objects into Core.

## TRANSFORM has the weakest semantic shape

TRANSFORM relies heavily on free-text wording. The listing example’s creation of `AGE_SEX` could reasonably be DERIVE. The ADaM example’s attachment of `BASE` could reasonably be described as MERGE. The conceptual boundary is sound, but programmers could classify the same code differently.

The guidance needs to be sharper: DERIVE creates a named analytical concept/variable/flag; TRANSFORM changes representation or structure without creating a new analytical concept.

## ANALYZE has an unclear first argument

`trace.analyze("Overall survival", method="Kaplan-Meier", ...)` felt natural, but `"Overall survival"` is an analysis/endpoint identity, not a dataset. Passing `"ADTTE"` would instead identify the input but lose the analysis identity. Phase 3/4 should explicitly define what `name` means for ANALYZE.

## Intermediate object naming requires discipline

Source datasets and outputs are obvious; intermediate objects such as `TEAE_SAFETY`, `ADLB_WORK`, `demographics_summary`, and `km_curve` require programmer-created semantic names. This is preferable to variable-name introspection, but TRACE needs naming guidance.

## Statistical scalar validation is too strict

Real pandas operations immediately produced NumPy integer scalars from `sum()` and `nunique()`. The examples had to use `int(...)` because the prototype accepts only native Python integers. TRACE should normalize compatible statistical numeric scalars instead of making programmers cast routine results.

## Step noise is real

Every successful step adds a start and completion line. The ADaM example has five steps, adding ten STEP lines. With START/END, 12 semantic operations become 26 emitted lines. Steps should therefore remain coarse program sections, not wrappers around individual operations.

Lifecycle itself was not noisy: two program-level lines are proportionate. The noise appears when step scopes become too granular.

## `details` did not become a dumping ground

This is a good result, but worth monitoring. The Kaplan–Meier example used `details` for method-specific metadata such as time, censor, and strata variables. Those fields should stay in `details` until repeated use across statistical methods demonstrates a stable public parameter.

# What should change

1. **Reopen Phase 3/4 narrowly for MERGE.** Keep `left_rows`, `right_rows`, and `result_rows`. Remove or rename ambiguous `matched`, `unmatched_left`, and `unmatched_right` unless their units are explicit. Method-specific/key-level diagnostics can live in `metrics` until a stable convention emerges.

2. **Clarify ANALYZE in Phase 3/4.** The first argument should represent the analysis identity (for example, `"Overall survival"`), not implicitly the input dataset. Input objects can be metadata when needed.

3. **Strengthen DERIVE vs TRANSFORM guidance in Phase 1/3.** Keep both operations, but define DERIVE as creating a named analytical concept and TRANSFORM as changing representation/structure.

4. **Normalize statistical numeric scalar types in implementation.** Accept safely normalizable NumPy/pandas integral/real scalars. This does not require reopening the domain model.

5. **Document semantic object naming.** Prefer stable domain identities over Python variable names. Do not introduce variable-name introspection.

6. **Document coarse step granularity.** A step should normally correspond to a section heading in a statistical program.

# What should remain frozen

**Phase 0 — Event model:** keep `severity`, `operation`, `object`, `action`, `metrics`, `details`, `status`, and `context`. The prototypes did not require formatted strings as canonical state.

**Phase 1 — Core vocabulary:** keep all eleven statistical operations. All were exercised, and no missing operation emerged. Lower-frequency CHECK, SORT, TRANSFORM, and ANALYZE each had legitimate use cases.

**Phase 4 — Core/integration boundary:** keep semantic identifiers in Core and runtime-object inspection in optional integrations.

**Phase 5 — `trace.log()`:** keep it secondary and vocabulary-constrained. None of the six programs needed it.

**Phase 6 — Configuration:** no additional constructor/configuration surface was justified.

**Phase 7 — Lifecycle:** keep automatic START/END for context-managed Trace instances and silent lifecycle behavior for plain `Trace()`.

**Phase 8 — Step model:** keep nested steps, `step`, `step_path`, monotonic duration, and exception propagation. The issue is granularity/rendering volume, not the structured model.

# What should be deferred

Defer dataframe integrations, automatic metadata extraction, JSON/execution manifests, decorators, renderer customization, quiet/compact step modes, configuration files, handler customization, log rotation, remote logging, CLI/async/plugin architecture, and production release hardening.

Do not add new operations such as FORMAT, REPORT, PLOT, MODEL, or COMPARE. The prototypes produced no evidence that the existing vocabulary cannot represent the tested workflows.

Do not add Kaplan–Meier-specific parameters to `analyze()`. Its `details` usage should remain method-specific until multiple analysis types reveal repeated metadata.

Do not add logger-style `trace.info()`, `trace.warning()`, or similar APIs. Nothing in the prototypes created a need for them.

# Phase reopening decision

The reference prototype does **not** justify a broad redesign of Phases 0–8.

Three narrow design follow-ups are justified before production implementation:

1. **Phase 3/4 — MERGE:** resolve matched/unmatched metric semantics and units.
2. **Phase 3/4 — ANALYZE:** define the semantic identity of its first argument.
3. **Phase 1/3 — DERIVE vs TRANSFORM:** sharpen classification guidance and examples.

Separately, later implementation should normalize common statistical numeric scalar types.

Everything else should remain frozen or deferred. The next activity should be a **small API reconciliation pass focused only on these findings**, not another feature sprint.
