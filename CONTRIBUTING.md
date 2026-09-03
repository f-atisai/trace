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

Clone the repository:

```bash
git clone https://github.com/f-atisai/trace.git
cd trace
```

Create and activate a virtual environment, then install TRACE in editable mode with development dependencies:

```bash
python -m pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

Run linting:

```bash
ruff check .
```

Run type checking:

```bash
mypy src
```

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
- `docs/guides/` for user-facing workflows;
- `docs/design/` for design work that is still being evaluated.

## Pull Requests

Keep pull requests focused. A pull request should solve one coherent problem and should avoid unrelated refactoring.

A good pull request includes:

- a concise explanation of the change;
- the motivation;
- tests where applicable;
- documentation updates where applicable; and
- any compatibility implications.

## Versioning

TRACE uses Semantic Versioning.

Until `1.0.0`, backwards-incompatible API changes may occur as the design matures. They should still be deliberate, documented, and reflected in the changelog.

## License

By contributing to TRACE, you agree that your contributions will be licensed under the project's MIT License.
