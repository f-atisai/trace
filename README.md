# TRACE

**TRACE — Transparent Reporting and Auditable Code Execution**

TRACE is an open-source **semantic execution evidence framework for statistical programming**, with a Python implementation for recording concise, reviewable execution logs.

It helps reviewers and programmers understand what a statistical program actually did by recording semantic events and execution evidence alongside the program and its outputs. TRACE uses structured logging as an implementation mechanism; it is not intended to be another general-purpose wrapper around Python `logging`.

> **Status:** TRACE is under active development. The current focus is API design and initial Python implementation; the public API may change before v1.0.

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

trace = Trace("T14_01")

trace.read(
    "ADSL",
    source="analysis/adsl.parquet",
    rows=254,
    columns=16,
)
trace.filter("ADSL", "SAFFL == 'Y'", before=254, after=249)
trace.derive("AGEGR1", dataset="ADSL", source="AGE")
trace.aggregate(
    "Safety Population",
    by=["TRT01A", "SEX", "AGEGR1"],
    result="demographics_summary",
)
trace.output("T14_01", "outputs/T14_01.rtf")
```

```text
INFO [READ]      [ADSL] loaded – N=254, Vars=16
INFO [FILTER]    [ADSL] SAFFL == 'Y' applied – N=254 → 249
INFO [DERIVE]    [AGEGR1] created – dataset=ADSL, source=AGE
INFO [AGGREGATE] [Safety Population] summarized – by=TRT01A,SEX,AGEGR1
INFO [OUTPUT]    [T14_01] written – outputs/T14_01.rtf
```

In TRACE Core, values such as `rows=254` or `before=254` are supplied by the calling program unless an integration inspected runtime state directly. TRACE's structured evidence model preserves the distinction between **observed**, **supplied**, and **derived** diagnostics.

TRACE is a review companion to the statistical program and its outputs. A clean TRACE execution does **not** establish that an analysis is statistically correct or replace specification review, code review, output review, or independent QC. A validation `PASS` means only that the implemented criterion evaluated successfully.

## Framework and Python implementation

- **TRACE Framework** defines the statistical-programming semantics and methodology for reviewable execution evidence.
- **TRACE Python** implements the framework for Python statistical programs using structured logging infrastructure.

Keeping the framework distinct from the implementation leaves room for future implementations in other languages.

TRACE Core remains backend-independent. Optional integrations may later inspect pandas, Polars, PyArrow, or other runtime objects to collect observed diagnostics without changing operation semantics.

## Documentation

- [`docs/framework/`](docs/framework/) — normative TRACE framework specifications and reviewer workflow.
- [`docs/api/`](docs/api/) — public Python API reference.
- [`docs/guides/`](docs/guides/) — task-oriented guidance, including optional Quarto use.
- [`docs/design/`](docs/design/) — governing design specifications, research, prototype findings, and architecture history.
- [`docs/examples/`](docs/examples/) — reviewer-oriented execution examples.

The active design roadmap begins in [`docs/design/api-design-plan.md`](docs/design/api-design-plan.md). The design documentation index explains which document is authoritative for each concept.

## Package naming

The project is branded **TRACE**, while the Python import package uses `trace_tlf` to avoid conflict with Python's standard-library `trace` module:

```python
from trace_tlf import Trace
```

The intended distribution name is `trace-tlf`, subject to final package-name review before publication.

## Installation

TRACE is not yet published as an installable release. A future development release is expected to use the standard Python package workflow:

```bash
pip install trace-tlf
```

## Development

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

Contributions, API-design discussion, clinical-programming use cases, and implementation feedback are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

## License

TRACE is released under the [MIT License](LICENSE).
