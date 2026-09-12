# Contributing to TRACE

Thank you for your interest in TRACE.

TRACE is currently in active development, with the main focus on defining a small, stable, and useful API for statistical-programming execution logging. Contributions are welcome, particularly when they are grounded in realistic statistical-programming workflows.

## Before Contributing

Please keep the project's core design principle in mind:

> TRACE should log what the statistical programmer means, not how Python logging works.

TRACE is not intended to become a replacement for Python's standard `logging` module, a dataframe transformation library, a TLF generation framework, or a general workflow orchestration system.

## Ways to Contribute

Useful contributions include:

- clinical-programming use cases that expose gaps in the proposed API;
- API design feedback;
- bug reports;
- documentation improvements;
- tests;
- focused implementation changes; and
- proposals for integrations with statistical-programming tools.

For substantial API or architectural changes, open an issue or design discussion before implementing the change.

## Development Setup

Clone the repository and create an isolated environment:

```bash
git clone https://github.com/f-atisai/trace.git
cd trace
python -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

Install TRACE in editable mode with the development dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Run the development checks:

```bash
pytest
ruff check .
mypy src
```

To verify that the distributable package can be built locally:

```bash
python -m build
```

This creates a source distribution and wheel under `dist/`. Build artifacts are
ignored by Git and should not be committed.

## Project Layout

```text
src/trace_tlf/      Python package
tests/              Automated tests
docs/framework/     TRACE framework specification
docs/api/           Public API documentation
docs/guides/        User and clinical-programming guides
docs/design/        API and architectural design work
examples/           Executable usage examples
```

## API Design Changes

Before `1.0.0`, the TRACE public API is allowed to evolve. That does not mean API changes should be casual.

Changes to public methods, event vocabulary, message grammar, configuration behavior, or structured event semantics should:

1. state the problem being solved;
2. include a realistic statistical-programming example;
3. explain the impact on existing API behavior;
4. consider backward compatibility; and
5. update the relevant design or API documentation.

Design proposals belong in `docs/design/` until they become part of the accepted framework or public API.

## Code Style

Keep implementation code explicit, typed where practical, and easy to review.

The development toolchain currently uses:

- `pytest` for testing;
- `ruff` for linting and formatting checks; and
- `mypy` for static type checking.

Avoid introducing runtime dependencies unless they provide clear value to the core library. Integrations such as pandas should remain optional where practical.

## Tests

New behavior should include tests.

Tests should focus on observable contracts, especially:

- structured event contents;
- rendered log messages;
- severity inference;
- lifecycle behavior;
- exception behavior; and
- integration-specific metadata extraction.

## Documentation

Public behavior should be documented with the code that implements it.

Use:

- `docs/framework/` for TRACE conventions and normative methodology;
- `docs/api/` for public Python API documentation;
- `docs/guides/` for task-oriented user guidance;
- `docs/design/` for design rationale and architecture decisions; and
- `docs/examples/` for reviewer-oriented execution examples.

Avoid duplicating authoritative definitions across documentation areas. Define each concept once and reference it elsewhere.
