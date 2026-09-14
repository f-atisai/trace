# TRACE

**Transparent Reporting and Auditable Code Execution**

TRACE is a **semantic execution evidence framework for statistical programming**. It helps programmers and reviewers see what a statistical program actually did: what data it read, how populations changed, what derivations and analyses ran, what was validated, and which outputs were produced.

TRACE uses structured logging as a mechanism, but it is not a general-purpose logging wrapper.

## See it in 60 seconds

A statistical program keeps ownership of the analysis. TRACE records the meaningful execution evidence around it.

```python
from trace_tlf import Trace

with Trace("T14_01") as trace:
    with trace.step("Analysis population"):
        safety = adsl.query("SAFFL == 'Y'")

        trace.filter(
            "ADSL",
            "SAFFL == 'Y'",
            before=len(adsl),
            after=len(safety),
        )
```

TRACE produces concise semantic events while the program runs:

```text
INFO [START]  [T14_01] execution started
INFO [STEP]   [Analysis population] started
INFO [FILTER] [ADSL] SAFFL == 'Y' applied – N=754 → 720
INFO [STEP]   [Analysis population] completed – 0.031s
INFO [END]    [T14_01] execution completed – 0.034s
```

With `log_file` configured, the final review log also records program-level execution provenance before the semantic event stream:

```text
TRACE EXECUTION

Program:  T14_01
Run ID:   7eab...
Executed: 2026-09-14T14:32:18Z

Input artifacts:
  data/adsl.xpt

Output artifacts:
  outputs/tlf_population.rtf

INFO [START] [T14_01] execution started
...
INFO [END] [T14_01] execution completed – 0.84s
```

The compact model is:

```text
Semantic events
      +
Execution diagnostics
      +
Program-level provenance
      =
Reviewable execution evidence
```

That evidence helps answer reviewer questions such as: Which data entered the run? Which population was selected? Where did counts change? How were datasets combined? Which checks passed or failed? What output artifact was produced?

TRACE is a review companion to the program, specification, output, and QC process. A clean TRACE run does **not** prove statistical correctness, and `VALIDATE PASS` means only that the implemented criterion passed.

## Try TRACE

TRACE currently targets Python 3.10+ and the Developer Preview is being developed directly from this repository.

```bash
git clone https://github.com/f-atisai/trace.git
cd trace
python -m pip install -e .
```

Then:

```python
from trace_tlf import Trace

with Trace("T14_01") as trace:
    trace.read("ADSL", source="data/adsl.xpt", rows=254, columns=48)

    safety = adsl.query("SAFFL == 'Y'")
    trace.filter("ADSL", "SAFFL == 'Y'", before=len(adsl), after=len(safety))

    trace.output("T14_01", "outputs/tlf_population.rtf")
```

For a finalized provenance-first review log:

```python
with Trace("T14_01", log_file="logs/T14_01.log") as trace:
    ...
```

## Core concepts

TRACE deliberately uses a small statistical-programming vocabulary. The canonical semantic operations are:

```text
READ  CHECK  FILTER  SORT  DERIVE  TRANSFORM
MERGE  AGGREGATE  ANALYZE  VALIDATE  OUTPUT
```

`START`, `END`, and `STEP` describe execution lifecycle and logical scopes rather than statistical operations.

TRACE Core does not own or wrap the statistical transformation itself. Code such as pandas or Polars performs the work; TRACE records the execution evidence after meaningful operations.

Diagnostics can represent evidence that was **supplied** by the program, **observed** by an integration, or **derived** by TRACE. The current Core API primarily records programmer-supplied diagnostics while remaining backend-independent.

## Real statistical-programming examples

The flagship examples use the public **CDISC Pilot Study** ADaM datasets and recognizable clinical-reporting workflows:

- [`examples/population_summary.py`](examples/population_summary.py) — analysis-population summary, including population attrition, treatment summaries, validation, and RTF output.
- [`examples/specific_adverse_events.py`](examples/specific_adverse_events.py) — adverse events by SOC and preferred term, including safety-set selection, dataset merging, and subject incidence.

Run them with:

```bash
python -m pip install -e ".[examples]"
python examples/fetch_example_data.py
python examples/population_summary.py
python examples/specific_adverse_events.py
```

See [`examples/README.md`](examples/README.md) for data provenance, workflow references, and reviewer guidance.

## Framework vs Python implementation

**TRACE Framework** defines the semantic execution-evidence model and statistical-programming conventions.

**TRACE for Python** is the Python implementation of that framework. The distribution name is `trace-tlf` and the import package is `trace_tlf`:

```python
from trace_tlf import Trace
```

Keeping the framework separate from the implementation leaves room for future implementations and integrations without changing the core semantics.

## Developer Preview status

TRACE is in active development toward **v0.1.0-alpha — Developer Preview**. The current package version is `0.1.0a1`.

The alpha is intended for experimentation and feedback from experienced statistical programmers. The public surface is intentionally small and may change before v1.0 as real-world use exposes API friction.

The supported top-level import is:

```python
from trace_tlf import Trace
```

The alpha public API includes the Tier 1 semantic helpers, context-managed lifecycle, `trace.step()`, and the advanced `trace.log()` escape hatch. Domain-model classes, renderers, provenance internals, and sink implementation details are not part of the public compatibility contract.

See [`docs/api/`](docs/api/) for the authoritative Developer Preview API boundary.

## Documentation

Use the documentation by purpose rather than reading it front to back:

- [`docs/framework/`](docs/framework/) — TRACE semantics, vocabulary, and reviewer workflow.
- [`docs/api/`](docs/api/) — public Python API.
- [`docs/guides/`](docs/guides/) — task-oriented guidance, including Quarto use.
- [`docs/examples/`](docs/examples/) — reviewer-oriented execution examples.
- [`docs/design/`](docs/design/) — governing design decisions and architecture history.

The README is intentionally a product introduction rather than the architecture specification.

## Contributing

API-design discussion, statistical-programming use cases, bug reports, and implementation contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

For repository development:

```bash
python -m pip install -e ".[dev]"
ruff check .
pytest
mypy src
```

## License

TRACE is released under the [MIT License](LICENSE).
