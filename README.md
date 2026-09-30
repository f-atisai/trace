# TRACE

**Structured logging for statistical programming.**

## Purpose

To provide a lightweight Python library for adding consistent logs to statistical analysis programs.

## Installation

TRACE currently supports Python 3.10+ and can be installed from the repository:

```bash
git clone https://github.com/f-atisai/trace.git
cd trace
python -m pip install -e .
```

## Usage

Please refer to [Getting Started](docs/getting-started.md) to learn how to add TRACE logs to a statistical program.

## Examples

The repo includes two public-data examples:

- [`population_summary.py`](examples/population_summary.py) — a population-summary TLF using public CDISC Pilot Study data.
- [`specific_adverse_events.py`](examples/specific_adverse_events.py) — a multi-dataset adverse-event TLF using ADSL and ADAE.

See [examples/README.md](examples/README.md) for running the examples.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and contribution guidance.
