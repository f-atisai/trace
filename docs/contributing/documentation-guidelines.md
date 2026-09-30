# TRACE documentation guidelines

Use this guide when writing or reviewing TRACE documentation. It defines the public positioning and terminology that user-facing documentation should follow.

## Position TRACE simply

Lead with what TRACE is and what it gives statistical programmers.

> **TRACE is a lightweight structured logging library for Python statistical programming.**

Short tagline:

> **Structured logging for statistical programming.**

Supporting description:

> TRACE adds a statistical-programming vocabulary and structured event model on top of Python logging, producing consistent execution logs that are easier to understand, troubleshoot, and review.

TRACE builds on Python's standard logging infrastructure. Do not distance the project from logging; explain what TRACE adds to it.

## Lead with user value

User-facing documentation should explain the practical workflow before the internal architecture.

Prefer this order:

1. what TRACE records;
2. how to add TRACE to a statistical program;
3. what the resulting log looks like;
4. why the statistical vocabulary and structure are useful;
5. lifecycle and program-level provenance; and
6. internal architecture or future integration concepts when relevant.

Ordinary users should not need to understand TRACE internals before using `trace.read()`, `trace.filter()`, `trace.derive()`, `trace.merge()`, `trace.analyze()`, `trace.validate()`, or `trace.output()`.

## Preferred terminology

Use these terms in public documentation:

- **structured logging** for the product category;
- **statistical-programming vocabulary** for operations such as `READ`, `FILTER`, `DERIVE`, `MERGE`, `ANALYZE`, `VALIDATE`, and `OUTPUT`;
- **structured events** for TRACE's internal representation of recorded operations;
- **execution logs** for TRACE's rendered user-facing output;
- **run lifecycle** for execution start, steps, completion, and timing;
- **program-level provenance** for program, run ID, execution timestamp, and input/output artifacts;
- **review-friendly** when describing logs designed to help another programmer or reviewer understand a run.

## Terminology to demote

Do not use the following as the primary definition of TRACE or require users to learn them on the main documentation path:

- semantic execution evidence;
- evidence pillars;
- evidence origin;
- supplied evidence;
- observed evidence;
- derived evidence;
- semantic boundaries.

These terms may remain in design or architecture documentation when they are necessary to explain an implementation decision or future integration model. Prefer simpler language when it communicates the same idea.

Do not present `SUPPLIED`, `OBSERVED`, or `DERIVED` as current user-facing product concepts unless the implementation exposes those distinctions directly.

## Explain the relationship with Python logging

Avoid defensive wording such as:

> TRACE is not a logging wrapper.

Prefer:

> TRACE builds on Python's standard logging infrastructure and adds conventions designed for statistical programming.

Python logging provides the mechanism and severity levels. TRACE adds a controlled statistical vocabulary, structured events, consistent rendering, run lifecycle context, and lightweight program-level provenance.

## Keep product and architecture separate

Public product description:

> TRACE is a structured logging library for statistical programming.

Architecture description, when needed:

> TRACE represents recorded operations as structured events independently of their final rendered log lines.

Do not lead with a distinction between a "TRACE Framework" and "TRACE for Python" while TRACE has one primary implementation. Architecture documentation may describe the event model as implementation-independent where that distinction matters.

## Writing principles

- Start with the statistical-programming problem or task.
- Prefer realistic statistical examples over generic software examples.
- Show code and output before extended theory when practical.
- Keep explanations concise and define a concept once in its authoritative location.
- Reference existing explanations instead of repeating them across pages.
- Distinguish what TRACE records from the statistical work performed by pandas, Polars, or another library.
- Do not imply that TRACE independently observed or derived information when the programmer supplied it.
- Preserve the controlled operation vocabulary consistently across documentation and examples.

## Consistency check

Before merging documentation, confirm that a reader can answer these questions without learning TRACE internals first:

1. **What is TRACE?** A lightweight structured logging library for Python statistical programming.
2. **What problem does it solve?** It gives statistical programs a consistent vocabulary and structure for recording important execution events.
3. **Why use it instead of arbitrary `logging.info()` calls?** TRACE adds statistical operations, structured events, consistent output, lifecycle context, and program-level provenance.

If a page needs more specialized terminology, introduce it only after these basics are clear.
