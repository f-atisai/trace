# TRACE

**TRACE — Transparent Reporting and Auditable Code Execution**

TRACE is an open-source **semantic execution evidence framework for statistical programming**, with a Python implementation for recording concise, reviewable execution logs.

It helps reviewers and programmers understand what a statistical program actually did by recording semantic events and execution evidence alongside the program and its outputs. TRACE uses structured logging as an implementation mechanism; it is not intended to be another general-purpose wrapper around Python `logging`.

> **Developer Preview status:** TRACE is preparing for `v0.1.0-alpha`. The documented alpha API is intentionally small and is intended for experimentation and feedback from statistical programmers. APIs may change before v1.0.

## Goals

TRACE is designed to make execution evidence easy to add without requiring programmers to construct repetitive messages or work directly with logging configuration.

The design focuses on:

- a controlled statistical-programming vocabulary;
- semantic events such as READ, FILTER, DERIVE, MERGE, ANALYZE, VALIDATE, and OUTPUT;
- structured diagnostics whose origin can distinguish what TRACE observed, what the program supplied, and what TRACE derived;
- program-level execution provenance that connects a run to its physical input and output artifacts;
- lifecycle and step instrumentation; and
- concise, review-ready output.

Example direction:

```python
from trace_tlf import Trace

with Trace("T14_01") as trace:
    trace.read(
        "ADSL",
        source="analysis/adsl.parquet",
        rows=254,
        columns=16,
    )

    with trace.step("Analysis population"):
        trace.filter(
            "ADSL",
            "SAFFL == 'Y'",
            result="Safety Population",
            before=254,
            after=249,
        )

    trace.derive("AGEGR1", dataset="ADSL", source="AGE")
    trace.aggregate(
        "Safety Population",
        by=["TRT01A", "SEX", "AGEGR1"],
        result="demographics_summary",
    )
    trace.output("T14_01", "outputs/T14_01.rtf")
```

```text
INFO [START]     [T14_01] execution started
INFO [READ]      [ADSL] loaded – N=254, Vars=16
INFO [STEP]      [Analysis population] started
INFO [FILTER]    [ADSL] SAFFL == 'Y' applied – N=254 → 249
INFO [STEP]      [Analysis population] completed – 0.031s
INFO [DERIVE]    [AGEGR1] created – dataset=ADSL, source=AGE
INFO [AGGREGATE] [Safety Population] summarized – by=TRT01A,SEX,AGEGR1
INFO [OUTPUT]    [T14_01] written – outputs/T14_01.rtf
INFO [END]       [T14_01] execution completed – 0.071s
```

`result="Safety Population"` preserves the analytical result identity while `ADSL` remains the object that was filtered.

In TRACE Core, values such as `rows=254` or `before=254` are supplied by the calling program unless an integration inspected runtime state directly. TRACE's evidence model distinguishes **observed**, **supplied**, and **derived** diagnostics.

TRACE is a review companion to the statistical program and its outputs. A clean TRACE execution does **not** establish that an analysis is statistically correct or replace specification review, code review, output review, or independent QC. A validation `PASS` means only that the implemented criterion evaluated successfully.

## Framework and Python implementation

- **TRACE Framework** defines the statistical-programming semantics and methodology for reviewable execution evidence.
- **TRACE for Python** implements the framework for Python statistical programs using structured logging infrastructure.

Keeping the framework distinct from the implementation leaves room for future implementations in other languages.

TRACE Core remains backend-independent. Optional integrations may later inspect pandas, Polars, PyArrow, or other runtime objects to collect observed diagnostics without changing operation semantics.

## Alpha public API

The supported top-level import is intentionally small:

```python
from trace_tlf import Trace
```

All eleven semantic helpers plus context-managed lifecycle and `trace.step()` are alpha public. `trace.log()` remains a supported advanced escape hatch rather than the normal programming style. Domain-model classes, renderers, logger internals, and event factories are not part of the alpha compatibility contract.

See [`docs/api/`](docs/api/) for the complete developer-preview boundary.

## Documentation

- [`docs/framework/`](docs/framework/) — normative TRACE framework specifications and reviewer workflow.
- [`docs/api/`](docs/api/) — public Python alpha API contract.
- [`docs/guides/`](docs/guides/) — task-oriented guidance, including optional Quarto use.
- [`docs/design/`](docs/design/) — governing design specifications, research, prototype findings, and architecture history.
- [`docs/examples/`](docs/examples/) — reviewer-oriented execution examples.

The design documentation index explains which document is authoritative for each concept.

## Package naming

The project is branded **TRACE**, while the Python import package uses `trace_tlf` to avoid conflict with Python's standard-library `trace` module:

```python
from trace_tlf import Trace
```

The intended distribution name is `trace-tlf`, subject to final package-name review before publication.

## Installation

TRACE is not yet published on PyPI. The planned developer preview will use:

```bash
pip install trace-tlf
```

For repository development:

```bash
git clone https://github.com/f-atisai/trace.git
cd trace
python -m pip install -e ".[dev]"
```

Run checks with:

```bash
pytest
ruff check .
mypy src
```

## Contributing

Contributions, API-design discussion, statistical-programming use cases, and implementation feedback are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

## License

TRACE is released under the [MIT License](LICENSE).
