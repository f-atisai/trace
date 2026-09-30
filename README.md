# TRACE

**Structured logging for statistical programming.**

TRACE is a lightweight Python library for adding consistent, statistical-programming-aware logs to analysis programs. It builds on Python's standard logging infrastructure and gives common operations such as filtering, deriving, merging, validating, and writing outputs a shared vocabulary.

## See it in 60 seconds

Keep writing statistical code with pandas, Polars, or your usual tools. Record the important operation nearby with TRACE.

```python
from trace_tlf import Trace

with Trace("T14_01") as trace:
    safety = adsl.query("SAFFL == 'Y'")

    trace.filter(
        "ADSL",
        "SAFFL == 'Y'",
        result="Safety Population",
        before=len(adsl),
        after=len(safety),
    )
```

TRACE produces a concise log while the program runs:

```text
INFO [START]  [T14_01] execution started
INFO [FILTER] [ADSL] SAFFL == 'Y' applied – N=754 → 720
INFO [END]    [T14_01] execution completed – 0.034s
```

TRACE does not perform the filter. Your statistical code does the work; TRACE records the operation and the diagnostics you provide.

## Why TRACE instead of `logging.info()`?

Python logging gives you severity levels and message delivery. TRACE adds a small vocabulary for describing what happened in a statistical workflow:

```text
READ  CHECK  FILTER  SORT  DERIVE  TRANSFORM
MERGE  AGGREGATE  ANALYZE  VALIDATE  OUTPUT
```

That makes logs more consistent across programs and easier for programmers and reviewers to follow.

TRACE also provides run lifecycle events, logical steps, run IDs, and lightweight program-level provenance for registered input and output artifacts.

## Install

TRACE currently targets Python 3.10+ and the Developer Preview is installed directly from the repository:

```bash
git clone https://github.com/f-atisai/trace.git
cd trace
python -m pip install -e .
```

Then:

```python
from trace_tlf import Trace
```

## Start here

- [Getting Started](docs/getting-started.md) — install TRACE and instrument a first statistical program.
- [Logging with TRACE](docs/logging-with-trace.md) — understand lifecycle, steps, file logs, provenance, and what to record.
- [TRACE operations](docs/guides/operations.md) — choose the right operation and see practical examples.

## Examples

TRACE includes three example levels:

- [`basic_analysis_workflow.py`](examples/basic_analysis_workflow.py) — a small ADSL-like workflow.
- [`population_summary.py`](examples/population_summary.py) — a population-summary TLF using public CDISC Pilot Study data.
- [`specific_adverse_events.py`](examples/specific_adverse_events.py) — a multi-dataset adverse-event TLF using ADSL and ADAE.

Run the basic example with:

```bash
python -m pip install -e ".[examples]"
python examples/basic_analysis_workflow.py
```

See [examples/README.md](examples/README.md) for the public-data examples and their setup.

## Developer Preview

TRACE is in active development toward **v0.1.0-alpha — Developer Preview**. The public API is intentionally small and may change before v1.0 as realistic statistical-programming use exposes friction.

A clean TRACE run does **not** prove statistical correctness and does not replace code review, output review, or independent QC.

## Contributing

Contributions grounded in realistic statistical-programming use are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and contribution guidance.

## License

TRACE is released under the [MIT License](LICENSE).
