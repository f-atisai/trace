# Contributing to TRACE

Thank you for contributing to TRACE.

TRACE is in Developer Preview. The most valuable contributions are grounded in realistic statistical-programming work and show where the current API is useful, unnatural, ambiguous, or missing an important concept.

TRACE's guiding principle is:

> TRACE should record what the statistical programmer means, not how Python logging works.

TRACE is a lightweight structured logging library for Python statistical programming. It builds on Python's standard logging infrastructure and adds a statistical-programming vocabulary, structured events, consistent rendering, run lifecycle context, and lightweight program-level provenance. TRACE does not own dataframe transformations, generate TLFs, or act as a workflow orchestrator.

## Get the tests passing first

```bash
git clone https://github.com/f-atisai/trace.git
cd trace
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
pytest
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Before submitting a code change, run:

```bash
ruff check .
pytest
mypy src
```

For packaging changes, also run:

```bash
python -m build
```

Build artifacts under `dist/` should not be committed.

## Project structure

```text
src/trace_tlf/      TRACE implementation
tests/              Automated behavior and contract tests
examples/           Executable statistical-programming examples
docs/               User and maintainer documentation
```

The public import is intentionally small:

```python
from trace_tlf import Trace
```

Internal event classes, renderers, provenance internals, sinks, and implementation objects are not public API merely because they can be imported from internal modules.

## Choose the right contribution path

### Bug

A bug is behavior that contradicts the documented public behavior, produces incorrect TRACE output, fails unexpectedly, or regresses previously supported behavior.

A useful bug report includes:

- the TRACE and Python versions or current commit;
- the smallest reproducible program;
- expected behavior;
- actual behavior and TRACE output or exception; and
- whether the issue affects the public API.

A missing API or a preference for different semantics is usually a design proposal rather than a bug.

### API or design proposal

Open an issue before changing public method signatures, operation vocabulary, lifecycle behavior, structured event semantics, provenance behavior, message grammar, or configuration.

A proposal should explain:

1. the statistical-programming problem;
2. a realistic program or reviewer workflow where it occurs;
3. which current TRACE operation or API was attempted;
4. what felt unnatural, ambiguous, verbose, or missing;
5. what the resulting TRACE log should communicate;
6. the proposed change; and
7. the compatibility impact on existing Developer Preview behavior.

A concrete use case is more useful than an abstract request for another helper or option.

If an accepted change alters TRACE's architecture or contributor invariants, update [`docs/design.md`](docs/design.md). Historical design discussion belongs in issues, pull requests, and Git history rather than new phase documents.

### Statistical-programming use case

Real workflows are especially valuable during Developer Preview, even when the contributor does not yet know what the API solution should be.

Describe:

- what you were programming;
- the analytical stage, datasets, or outputs involved;
- which TRACE operations you tried;
- what the statistical code actually did;
- what felt unnatural or missing;
- what you expected the log to communicate; and
- a minimal example when possible.

### Documentation improvement

Documentation changes are welcome when something is incorrect, incomplete, difficult to find, or harder to understand than necessary.

TRACE follows a single-ownership rule: **define each concept once and reference it elsewhere instead of copying the same explanation into multiple files.**

## Working on a change

For a focused contribution:

1. start from an up-to-date `main` branch;
2. create a short-lived branch with a descriptive name;
3. make the smallest change that solves the identified problem;
4. add or update tests for behavioral changes;
5. update documentation when public behavior changes;
6. run `ruff check .`, `pytest`, and `mypy src`; and
7. open a pull request explaining the problem, solution, and verification performed.

Keep unrelated cleanup out of the same pull request.

## Code expectations

Keep the core implementation explicit, typed, and backend-independent.

TRACE records statistical-programming operations; it should not take ownership of the statistical transformation itself. pandas, Polars, NumPy, or other libraries perform the filter, merge, derivation, or analysis and TRACE records the meaningful operation around that work.

Avoid adding runtime dependencies to TRACE Core unless they provide clear cross-backend value. Backend-specific integrations should remain optional.

Prefer observable behavior over private implementation detail when designing tests or APIs.

## Test expectations

Behavioral changes should include tests at the appropriate boundary, especially for:

- public method signatures and argument validation;
- structured event contents;
- rendered TRACE output;
- operation and status behavior;
- lifecycle and step behavior;
- exception propagation;
- provenance finalization and artifact registration; and
- regressions discovered in realistic statistical programs.

If a public signature changes, update the relevant contract tests deliberately rather than weakening them to make the change pass.

## Documentation rules

The release documentation is intentionally small:

```text
README.md
CONTRIBUTING.md

docs/
├── getting-started.md
├── logging-with-trace.md
├── operations.md
└── design.md
```

Use these ownership rules:

- `README.md` — project introduction, quick example, installation, and links to the main docs;
- `docs/getting-started.md` — first successful TRACE workflow;
- `docs/logging-with-trace.md` — normal logging usage, lifecycle, steps, file logs, provenance, and review boundaries;
- `docs/operations.md` — the canonical statistical-operation vocabulary and operation-selection guidance;
- `docs/design.md` — current architecture, public/internal boundaries, and contributor invariants;
- `CONTRIBUTING.md` — development and contribution workflow.

User-facing documentation should:

- describe TRACE as **structured logging for statistical programming**;
- explain user value before internal architecture;
- use realistic statistical examples;
- distinguish the statistical work from the TRACE call that records it;
- keep the controlled operation vocabulary consistent;
- avoid design-history terminology unless it is required to explain current behavior; and
- avoid implying that TRACE independently observed or derived information that the programmer supplied.

Do not create new documentation files merely to preserve design discussion. If the information affects current behavior or contributor constraints, update the appropriate existing document. Otherwise, rely on issues, pull requests, and Git history.

## Pull request checklist

Before requesting review, confirm that:

- the change solves one clearly stated problem;
- `ruff check .` passes;
- `pytest` passes;
- `mypy src` passes;
- new or changed behavior has appropriate tests;
- public behavior is reflected in the appropriate documentation;
- no unnecessary runtime dependency was introduced; and
- API changes are backed by a realistic statistical-programming use case.

Not every contribution needs to change code. A small reproducible use case that exposes API friction can be one of the most useful contributions during Developer Preview.
