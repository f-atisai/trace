# Contributing to TRACE

Thank you for contributing to TRACE.

TRACE is in Developer Preview. The most valuable contributions are those grounded in realistic statistical-programming work and evidence about where the current API succeeds, feels unnatural, or is missing an important concept.

TRACE's guiding principle is:

> TRACE should record what the statistical programmer means, not how Python logging works.

TRACE is a lightweight structured logging library for Python statistical programming. It builds on Python's standard logging infrastructure and adds a statistical-programming vocabulary, structured events, consistent rendering, run lifecycle context, and lightweight program-level provenance. It is not intended to own dataframe transformations, generate TLFs, or become a general workflow orchestrator.

Documentation should follow the public positioning and terminology defined in the [TRACE documentation guidelines](docs/contributing/documentation-guidelines.md).

Please follow the [Code of Conduct](CODE_OF_CONDUCT.md) in all project interactions.

## Get the tests passing first

A new contributor should be able to clone TRACE and reach a passing test suite in about ten minutes.

```bash
git clone https://github.com/f-atisai/trace.git
cd trace
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
pytest
```

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

If `pytest` passes, the development environment is ready.

Before submitting a code change, run the complete local quality checks:

```bash
ruff check .
pytest
mypy src
```

To verify packaging changes:

```bash
python -m build
```

Build artifacts are written under `dist/` and should not be committed.

## Project structure

```text
src/trace_tlf/      TRACE implementation
tests/              Automated contract and behavior tests
examples/           Executable statistical-programming examples
docs/concepts/      User-facing TRACE concepts
docs/framework/     Operation vocabulary and reviewer methodology
docs/api/           Developer Preview public Python API
docs/guides/        Task-oriented user guidance
docs/design/        Design rationale, architecture, and history
```

The public import is intentionally small:

```python
from trace_tlf import Trace
```

Do not treat internal event classes, renderers, provenance internals, sinks, or implementation objects as public API merely because they can be imported from internal modules. The current public boundary is documented in the [TRACE API](docs/api/README.md).

## Choose the right contribution path

Before writing code, identify what kind of change you have found.

### Bug

A bug is existing behavior that contradicts the documented public contract, produces incorrect TRACE output, fails unexpectedly, or regresses behavior that should continue to work.

A useful bug report includes:

- the TRACE and Python versions or current commit;
- the smallest reproducible program;
- expected behavior;
- actual behavior and TRACE output or exception; and
- whether the problem affects the documented public API.

A missing API or a preference for different semantics is usually not a bug.

### API or design proposal

Open an issue before implementing a change to public method signatures, operation vocabulary, lifecycle behavior, structured event semantics, provenance behavior, message grammar, or configuration.

The proposal should explain:

1. the statistical-programming problem;
2. a realistic program or reviewer workflow where it occurs;
3. which current TRACE operation or API was attempted;
4. what felt unnatural, ambiguous, verbose, or missing;
5. what execution information the programmer expected TRACE to communicate;
6. the proposed API or semantic change; and
7. the compatibility impact on existing Developer Preview behavior.

A concrete use case is more valuable than an abstract request for another helper or configuration option.

Design proposals belong in `docs/design/` only after there is a reason to preserve the design decision in the repository. Accepted user-facing concepts belong in `docs/concepts/`, operation semantics and reviewer methodology belong in `docs/framework/`, and supported Python behavior belongs in `docs/api/`.

### Statistical-programming use case

Real workflows are especially valuable during the Developer Preview, even when the contributor does not yet know what the API solution should be.

When reporting a use case, describe:

- what you were programming;
- the analytical stage, datasets, or outputs involved;
- which TRACE operation or operations you tried;
- what the statistical code actually did;
- what felt unnatural or missing;
- what you expected the resulting log to communicate to another programmer or reviewer; and
- a minimal example when possible.

This kind of feedback helps TRACE evolve from realistic use rather than hypothetical API design.

### Documentation improvement

Documentation changes are welcome when something is incorrect, incomplete, difficult to find, or harder to understand than necessary.

TRACE follows a single-ownership rule for documentation: define each concept once in its authoritative document and reference it elsewhere. Avoid fixing a documentation problem by copying the same explanation into several files.

Use the [documentation guidelines](docs/contributing/documentation-guidelines.md) to keep positioning and terminology consistent.

## Working on a change

For a focused contribution:

1. start from an up-to-date `main` branch;
2. create a short-lived branch with a descriptive name;
3. make the smallest change that solves the identified problem;
4. add or update tests for behavioral changes;
5. update public documentation when public behavior changes;
6. run `ruff check .`, `pytest`, and `mypy src`; and
7. open a pull request explaining the problem, solution, and verification performed.

Keep unrelated cleanup out of the same pull request. Small, reviewable changes make API consequences easier to evaluate.

## Code expectations

Keep the core implementation explicit, typed, and backend-independent.

TRACE should observe or record statistical-programming operations; it should not take ownership of the underlying statistical transformation. For example, pandas or Polars should perform a filter or merge and TRACE should record the meaningful execution information around that operation.

Avoid adding runtime dependencies to TRACE Core unless they provide clear cross-backend value. Dataframe-specific integrations should remain optional rather than making pandas, Polars, or another analytical library a core requirement.

Ruff is the repository linter and import/style checker:

```bash
ruff check .
```

Mypy checks the typed core implementation:

```bash
mypy src
```

## Test expectations

Behavioral changes should include tests at the appropriate contract boundary.

Tests are especially important for:

- public method signatures and argument validation;
- structured event contents;
- rendered TRACE output;
- operation and status behavior;
- lifecycle and step behavior;
- exception propagation;
- provenance finalization and artifact registration; and
- regressions discovered in realistic statistical programs.

Prefer tests of observable behavior over tests coupled to private implementation details.

If a public API signature changes, update the alpha public-contract tests deliberately rather than weakening them to make the change pass.

## Documentation expectations

Public behavior should be documented with the change that implements it.

Use:

- `docs/concepts/` for concise user-facing explanations of TRACE concepts such as structured events and program-level provenance;
- `docs/framework/` for canonical operation vocabulary and reviewer methodology;
- `docs/api/` for the supported Python API;
- `docs/guides/` for task-oriented workflows; and
- `docs/design/` for rationale, alternatives, internal architecture, experimental terminology, and design history.

Executable statistical examples belong under `examples/`.

Do not require ordinary users to read `docs/design/` to learn how to use supported public behavior. Advanced terms such as evidence-origin classifications should stay in design documentation unless they become an exposed user-facing capability.

## Pull request checklist

Before requesting review, confirm that:

- the change solves one clearly stated problem;
- `ruff check .` passes;
- `pytest` passes;
- `mypy src` passes;
- new or changed behavior has appropriate tests;
- public behavior is reflected in the public documentation;
- no unnecessary runtime dependency was introduced; and
- API changes are backed by a realistic statistical-programming use case.

Not every contribution needs to change code. A small reproducible use case that exposes API friction can be one of the most useful contributions to TRACE during the Developer Preview.
