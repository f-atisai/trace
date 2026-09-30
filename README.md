# TRACE

**Structured logging for statistical programming.**

TRACE is a lightweight structured logging library for Python statistical programming. It gives statistical programs a consistent vocabulary for recording data reads, filters, derivations, merges, analyses, validations, and outputs—producing concise execution logs that are easier to understand, troubleshoot, and review.

TRACE builds on Python's standard logging infrastructure and adds conventions designed for statistical programming.

## See it in 60 seconds

Keep writing statistical code with pandas, Polars, or your usual tools. Record the important operation nearby with TRACE.

```python
from trace_tlf import Trace

with Trace("T14_01") as trace:
    safety = adsl.query("SAFFL == 'Y'")

    trace.filter(
        "ADSL",
        "SAFFL == 'Y'",
        before=len(adsl),
        after=len(safety),
    )
```

TRACE produces a concise, consistent log while the program runs:

```text
INFO [START]  [T14_01] execution started
INFO [FILTER] [ADSL] SAFFL == 'Y' applied – N=754 → 720
INFO [END]    [T14_01] execution completed – 0.034s
```

TRACE does not perform the filter. Your statistical code does the work; TRACE records the operation and the diagnostics you provide.

## Why TRACE instead of `logging.info()`?

Python logging provides the logging mechanism and severity levels. TRACE adds a small statistical-programming vocabulary and a consistent structure for recording what happened in the workflow.

```text
READ  CHECK  FILTER  SORT  DERIVE  TRANSFORM
MERGE  AGGREGATE  ANALYZE  VALIDATE  OUTPUT
```

That gives TRACE logs predictable meaning across programs. It also adds:

- structured events rather than arbitrary message strings;
- consistent human-readable rendering;
- execution lifecycle and logical step timing;
- run IDs and execution context; and
- lightweight program-level provenance for input and output artifacts.

The result is a log that can help another programmer or reviewer follow a run without replacing the program, specification, output, or QC process.

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

For a file-based review log with program-level provenance:

```python
with Trace("T14_01", log_file="logs/T14_01.log") as trace:
    ...
```

A finalized log can include the run context before the operation stream:

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

Continue with the [Getting Started guide](docs/guides/getting-started.md) for the complete programmer workflow.

## Core concepts

TRACE deliberately uses a small statistical-programming vocabulary. `START`, `END`, and `STEP` describe execution lifecycle and logical scopes rather than statistical operations.

TRACE represents recorded operations as structured events independently of their final rendered log lines. This keeps the instrumentation consistent while allowing rendering and run metadata to evolve separately.

TRACE Core does not own or wrap the statistical transformation itself. Code such as pandas or Polars performs the work; TRACE records the meaningful operation afterward.

A clean TRACE run does **not** prove statistical correctness, and `VALIDATE PASS` means only that the implemented criterion passed.

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

See [TRACE Statistical Programming Examples](examples/README.md) for data provenance and workflow references, and [TRACE Reviewer Examples](docs/examples/README.md) for the reviewer perspective.

## Developer Preview status

TRACE is in active development toward **v0.1.0-alpha — Developer Preview**. The current package version is `0.1.0a1`.

The alpha is intended for experimentation and feedback from experienced statistical programmers. The public surface is intentionally small and may change before v1.0 as real-world use exposes API friction.

The supported top-level import is:

```python
from trace_tlf import Trace
```

The alpha public API includes the Tier 1 operation helpers, context-managed lifecycle, `trace.step()`, and the advanced `trace.log()` escape hatch. Domain-model classes, renderers, provenance internals, and sink implementation details are not part of the public compatibility contract.

See the [TRACE API](docs/api/) for the authoritative Developer Preview API.

## Documentation

For normal Developer Preview use, follow this path:

1. [Getting Started with TRACE](docs/guides/getting-started.md) — install and instrument your first workflow.
2. [TRACE API](docs/api/) — exact public Python API signatures and semantics.
3. [TRACE Statistical Programming Examples](examples/README.md) — run the public-data flagship examples.
4. [Concepts and reviewer methodology](docs/framework/) — deeper vocabulary, event semantics, provenance, and review guidance.
5. [Using TRACE with Quarto](docs/guides/quarto.md) — optional Quarto workflow.

[TRACE Design Documentation](docs/design/) contains architecture decisions and design history. It is not required to use TRACE.

## Contributing

API design discussion, statistical-programming use cases, bug reports, and implementation contributions are welcome. See [Contributing to TRACE](CONTRIBUTING.md) before opening a pull request.

For repository development:

```bash
python -m pip install -e ".[dev]"
ruff check .
pytest
mypy src
```

## License

TRACE is released under the [MIT License](LICENSE).
