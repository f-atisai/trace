# TRACE Phase 6 — Configuration

**Phase:** 6 — Design Configuration Separately from Logging  
**Status:** Draft normative configuration specification  
**Scope:** `Trace(...)` construction, defaults, configuration boundaries, and advanced logger access

## 1. Decision

TRACE is configured once per instance; operation calls remain focused on execution semantics.

```python
from trace_tlf import Trace

trace = Trace("T14_01")
trace.read(...)
trace.filter(...)
trace.output(...)
```

> **Configure TRACE once; record semantic operations many times.**

## 2. Canonical constructor

The recommended initial constructor is:

```python
Trace(
    program,
    *,
    study=None,
    log_file=None,
    level="INFO",
)
```

Minimal:

```python
trace = Trace("T14_01")
```

Typical explicit configuration:

```python
trace = Trace(
    program="T14_01",
    study="ABC123",
    log_file="logs/T14_01.log",
    level="INFO",
)
```

This should represent approximately the upper end of routine configuration complexity.

## 3. Configuration fields

### `program`

Required identifier for the statistical program or execution unit, for example `T14_01`, `ADSL`, or `qc_T14_01`. It becomes inherited event context.

### `study`

Optional study identifier. It remains optional so TRACE also supports examples, utilities, tests, non-clinical workflows, and cross-study programs.

### `log_file`

Optional human-readable log destination. When omitted, the initial default is console output with no unexpected file creation.

Users should not need to configure a Python `FileHandler` for normal file logging.

### `level`

Minimum emitted severity. Documented values follow the TRACE severity model:

```text
DEBUG
INFO
WARNING
ERROR
CRITICAL
```

Default: `INFO`.

Severity semantics themselves are defined in [`domain-model.md`](domain-model.md).

## 4. Configuration boundary

Operation methods describe execution events, not logger configuration. Avoid APIs such as:

```python
trace.filter(
    "ADSL",
    "SAFFL == 'Y'",
    before=754,
    after=720,
    level="INFO",
    log_file="logs/T14_01.log",
)
```

Likewise, ordinary `Trace(...)` construction should not expose handler, formatter, propagation, stream, or encoding configuration unless a demonstrated advanced use case requires it.

The statistical-programming abstraction should remain more prominent than the underlying Python logging infrastructure.

## 5. Inherited context

Instance configuration establishes context shared by emitted events. At minimum this includes `program` and optional `study`; lifecycle may add execution identity such as `run_id`.

Context should be established once rather than repeated on every operation call.

The canonical context model belongs to [`domain-model.md`](domain-model.md), while run behavior belongs to [`lifecycle.md`](lifecycle.md).

## 6. Advanced logger access

Expert users may eventually access the underlying logger through:

```python
trace.logger
```

This is an escape hatch, not the normal TRACE API. Direct logger mutation may affect TRACE behavior and need not be guaranteed by the high-level public contract.

TRACE should not require knowledge of `logging.Handler`, `logging.Formatter`, `logger.propagate`, or dictionary configuration for routine use.

## 7. File behavior

Phase 6 establishes that `log_file` selects a file destination but does not independently freeze all run/file-mode semantics.

Questions such as append versus one-file-per-run should be resolved in conjunction with lifecycle and run identity rather than by exposing raw `FileHandler` options in the constructor.

Whatever policy is chosen should be predictable, documented, and safe for repeated statistical-program execution.

## 8. Validation

Configuration should fail early for clearly invalid values such as an empty program identifier or unsupported severity level.

TRACE should avoid silently accepting misspelled configuration keys or ambiguous combinations that could cause evidence to be written somewhere unexpected.

Detailed exception classes and validation mechanics remain implementation concerns unless they become part of the public API contract.

## 9. Related specifications

- [`domain-model.md`](domain-model.md) — context and severity semantics.
- [`minimum-programmer-experience.md`](minimum-programmer-experience.md) — routine-use complexity constraints.
- [`lifecycle.md`](lifecycle.md) — run identity, START/END behavior, and lifecycle-related file semantics.
- [`tier-1-api.md`](tier-1-api.md) — operation methods that consume the configured TRACE instance.
