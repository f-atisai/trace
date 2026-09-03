# TRACE

**TRACE — Transparent Reporting and Auditable Code Execution**

TRACE is an open-source Python library for statistical programming, implementing the TRACE framework for transparent, consistent, and auditable execution logs.

The project is intended to make useful execution logging easy to add to statistical programs without requiring programmers to repeatedly construct logging messages or work directly with Python logging configuration.

> TRACE is under development. The API examples and project structure described here are design targets and may change before v1.0.

## Project Status

TRACE is currently under active development.

Current focus: API design and initial Python implementation.

The public API may change before v1.0.

## Project Goals

TRACE aims to provide a lightweight, domain-aware logging layer for statistical programming. The library will build on Python's standard `logging` infrastructure rather than replace it.

The initial design focuses on:

- simple configuration;
- consistent TRACE message generation;
- statistical-programming-aware operations such as READ, FILTER, DERIVE, MERGE, VALIDATE, and OUTPUT;
- optional DataFrame-aware logging;
- step and function instrumentation; and
- clean, review-ready log files.

A future TRACE program should be able to read naturally:

```python
from trace_tlf import Trace

trace = Trace("T14_01")

trace.read("ADSL", rows=754, columns=16)
trace.filter("ADSL", "SAFFL == 'Y'", before=754, after=720)
trace.derive("AGEGR1", dataset="ADSL", source="AGE")
trace.output("T14_01", "outputs/tables/T14_01.rtf")
```

with output resembling:

```text
INFO [READ] [ADSL] loaded – N=754, Vars=16
INFO [FILTER] [ADSL] SAFFL == 'Y' applied – N=754 → 720
INFO [DERIVE] [AGEGR1] created – dataset=ADSL, source=AGE
INFO [OUTPUT] [T14_01] written – outputs/tables/T14_01.rtf
```

These examples describe the intended API direction; they are not yet a stable public contract.

## TRACE Framework and TRACE Python

The project distinguishes between two related concepts:

- **TRACE Framework** — the conventions, vocabulary, message grammar, severity guidance, and methodology for execution logging in statistical programming.
- **TRACE Python** — the Python library that implements those conventions.

Keeping the framework separate from the implementation makes the methodology portable and leaves room for future implementations in other programming languages.

## Repository Structure

```text
trace/
├── src/
│   └── trace_tlf/
├── tests/
├── docs/
│   ├── framework/
│   ├── api/
│   ├── guides/
│   └── design/
├── examples/
├── README.md
├── CONTRIBUTING.md
├── CHANGELOG.md
├── LICENSE
├── pyproject.toml
└── .github/
```

The repository intentionally keeps the library, API documentation, framework documentation, guides, and design records together.

### Documentation

- `docs/framework/` — normative TRACE framework documentation and conventions.
- `docs/api/` — public Python API reference and API documentation.
- `docs/guides/` — task-oriented user guides and clinical-programming examples.
- `docs/design/` — pre-implementation API design, architectural decisions, and design notes.

The active API design plan begins in [`docs/design/api-design-plan.md`](docs/design/api-design-plan.md).

## Package Naming

The project is branded **TRACE**, while the Python import package uses `trace_tlf`:

```python
from trace_tlf import Trace
```

This avoids conflicting with Python's standard-library `trace` module.

The intended distribution name is currently `trace-tlf`, subject to package-name availability and final naming review before publication to PyPI.

## Versioning

TRACE follows [Semantic Versioning](https://semver.org/) for public releases.

During initial development, versions remain below `1.0.0`, for example:

```text
0.1.0
0.2.0
0.5.0
...
1.0.0
```

Before `1.0.0`, the public API may evolve as the design is validated through implementation and real statistical-programming use cases. `1.0.0` will mark the first stable public API contract.

## Installation

TRACE is not yet published as an installable release.

Once the first development release is available, installation is expected to follow the standard Python package workflow:

```bash
pip install trace-tlf
```

## Development

Clone the repository and install the development dependencies:

```bash
git clone https://github.com/f-atisai/trace.git
cd trace
python -m pip install -e ".[dev]"
```

Run the test suite:

```bash
pytest
```

Run static checks:

```bash
ruff check .
mypy src
```

## Contributing

TRACE is in an early design stage. Contributions, API-design discussion, clinical-programming use cases, and implementation feedback are welcome.

See [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

## License

TRACE is released under the [MIT License](LICENSE).
