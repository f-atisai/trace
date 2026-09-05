# TRACE Phase 6 — Configuration

**Phase:** 6 — Design Configuration Separately from Logging  
**Status:** Draft normative configuration specification  
**Scope:** `Trace(...)` construction, defaults, configuration boundaries, and advanced logger access

## 1. Purpose

TRACE configuration should be defined separately from operation logging.

A programmer should configure TRACE once:

```python
from trace_tlf import Trace

trace = Trace("T14_01")
```

and then write normal TRACE events:

```python
trace.read(...)
trace.filter(...)
trace.derive(...)
trace.output(...)
```

> **Configure TRACE once; log semantic operations many times.**

## 2. Canonical Constructor

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

Explicit:

```python
trace = Trace(
    program="T14_01",
    study="ABC123",
)
```

Advanced but still ordinary:

```python
trace = Trace(
    program="T14_01",
    log_file="logs/T14_01.log",
    level="INFO",
)
```

This should represent approximately the upper end of routine configuration complexity.

## 3. `program`

`program` is required and identifies the statistical program or execution unit.

Examples:

```text
T14_01
L16_02
F14_03
ADSL
ADAE
qc_T14_01
```

It becomes inherited event context:

```json
{
  "context": {
    "program": "T14_01"
  }
}
```

TRACE should allow both:

```python
Trace("T14_01")
```

and:

```python
Trace(program="T14_01")
```

## 4. `study`

`study` is optional inherited context.

```python
trace = Trace(
    program="T14_01",
    study="ABC123",
)
```

Conceptually:

```json
{
  "context": {
    "program": "T14_01",
    "study": "ABC123"
  }
}
```

It remains optional because TRACE must also support examples, utilities, non-clinical workflows, unit tests, and cross-study programming.

## 5. `log_file`

`log_file` optionally defines the human-readable TRACE log destination.

```python
trace = Trace(
    "T14_01",
    log_file="logs/T14_01.log",
)
```

The user should not have to create or configure a Python `FileHandler`.

When omitted, the recommended initial behavior is:

```text
console output enabled
file output disabled
```

TRACE should not unexpectedly create files in the current directory.

## 6. `level`

`level` controls the minimum emitted severity.

```python
trace = Trace(
    "T14_01",
    level="WARNING",
)
```

Recommended documented values:

```text
DEBUG
INFO
WARNING
ERROR
CRITICAL
```

Default:

```python
level="INFO"
```

Users should not need to import `logging.INFO`.

Configuration level is distinct from event semantics:

```text
operation
status
severity
configured output threshold
```

are separate concepts.

## 7. Configuration Must Not Leak into Operation Calls

Avoid:

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

Avoid passing handlers or formatters to `trace.output()` or `trace.validate()`.

Tier 1 and Tier 2 calls describe execution events, not logger configuration.

## 8. Hide Python Logging Complexity

Do not make this part of the ordinary API:

```python
Trace(
    handlers=[...],
    formatters=[...],
    propagate=False,
    mode="a",
    stream=True,
    encoding="utf8",
)
```

These are implementation details.

Exposing them would make TRACE feel like a thin wrapper over Python logging and undermine its statistical-programming abstraction.

## 9. Advanced Escape Hatch

Expert users may eventually access:

```python
trace.logger
```

Example:

```python
trace = Trace("T14_01")

logger = trace.logger
```

This should be documented as advanced infrastructure, not normal TRACE usage.

Arbitrary mutations to the underlying logger may affect high-level TRACE behavior and need not be guaranteed by the primary API contract.

## 10. Inherited Context

Configuration owns instance-level context.

At minimum:

```text
program
study
```

Potential future fields:

```text
run_id
environment
trace_version
output
user_context
```

Users should not repeat program/study on every event:

```python
trace = Trace(
    "T14_01",
    study="ABC123",
)

trace.filter(
    "ADSL",
    "SAFFL == 'Y'",
    before=754,
    after=720,
)
```

The event should inherit the configured context automatically.

## 11. Context Snapshot Rule

Each emitted event should receive a snapshot of the current inherited context.

Serialized events should not depend on a mutable live `Trace` configuration object.

This preserves event self-containment.

## 12. Recommended Defaults

Conceptually:

```text
program       = required
study         = None
level         = INFO
console       = enabled
log_file      = disabled
format        = TRACE default renderer
encoding      = UTF-8
propagation   = internally controlled
```

Only high-level concepts should be exposed initially.

## 13. Console Default

Console output should be enabled by default.

That gives immediate value in:

```text
local development
CI
containers
notebooks
batch environments
cloud execution
```

File output remains explicit.

## 14. Parent Directory Handling

For:

```python
Trace(
    "T14_01",
    log_file="logs/T14_01.log",
)
```

TRACE should preferably create missing parent directories when safe.

Permission and filesystem failures should raise clear configuration/runtime errors.

## 15. File Mode

Do not expose `mode="a"` or `mode="w"` initially.

The exact default interacts with lifecycle and run identity, so file mode should remain an implementation detail until those semantics are frozen.

## 16. Encoding

Do not expose encoding initially.

TRACE text output should use UTF-8 internally.

## 17. Streams and Propagation

Do not expose ordinary constructor parameters such as:

```python
stream=True
propagate=False
```

TRACE should select safe internal defaults.

Advanced users can later work through `trace.logger`.

## 18. Formatters

Do not expose arbitrary Python logging formatters in the initial constructor.

TRACE's standard text renderer is part of its consistency promise.

Custom rendering belongs in a later advanced API.

## 19. Configuration Precedence

Future sources may include:

```text
constructor arguments
environment variables
configuration files
TRACE defaults
```

Recommended precedence:

```text
constructor arguments
        ↓
external configuration
        ↓
TRACE defaults
```

Phase 6 freezes constructor behavior only.

## 20. No Configuration File Yet

Do not require:

```text
trace.yaml
trace.toml
.traceconfig
```

for v0.x.

Organization-wide configuration may be added later, but five-minute adoption remains:

```python
trace = Trace("T14_01")
```

## 21. No Required Global Configuration

TRACE should not require:

```python
trace_tlf.configure(...)
```

before creating instances.

Instance-level configuration is easier to test, isolate, and reason about.

## 22. Multiple Instances

This should be valid:

```python
prod_trace = Trace(
    "T14_01",
    log_file="logs/prod.log",
)

qc_trace = Trace(
    "qc_T14_01",
    log_file="logs/qc.log",
)
```

Internal logger naming and handler management must avoid collisions.

## 23. Constructor Validation

Fail early on invalid high-level configuration.

Validate at least:

```text
program is non-empty
study is text when supplied
level is recognized
log_file is path-like/string when supplied
```

Do not impose sponsor-specific naming conventions.

## 24. Level Normalization

TRACE may normalize:

```python
Trace("T14_01", level="info")
```

to:

```text
INFO
```

Exact normalization rules should be frozen during implementation hardening.

## 25. Configuration Does Not Change Event Shape

These:

```python
Trace("T14_01")
```

and:

```python
Trace(
    "T14_01",
    study="ABC123",
    log_file="logs/T14_01.log",
    level="INFO",
)
```

should still produce the same semantic event model.

Configuration affects inherited context and output policy, not operation semantics.

## 26. Architecture

Conceptually:

```text
Trace(...)
   │
   ├── inherited context
   │     ├── program
   │     └── study
   │
   ├── output policy
   │     ├── level
   │     ├── console
   │     └── log_file
   │
   └── internal logger
          ↓
Tier 1 / Tier 2 event creation
          ↓
TraceEvent
          ↓
rendering/output
```

## 27. Future Advanced Configuration

Potential later features:

```text
JSON sinks
multiple sinks
custom renderers
organization defaults
environment variables
rotation
remote telemetry
custom streams
```

Do not add these to the base constructor merely because Python logging supports them.

A future `TraceConfig` object may be appropriate if advanced configuration grows substantially.

## 28. Phase 6 Decisions

**P6-01** — Configuration is instance-level and separate from event calls.

**P6-02** — Canonical constructor:

```python
Trace(
    program,
    *,
    study=None,
    log_file=None,
    level="INFO",
)
```

**P6-03** — `Trace("T14_01")` is the minimum useful configuration.

**P6-04** — `program` is required inherited context.

**P6-05** — `study` is optional inherited context.

**P6-06** — `log_file` is optional and abstracts file-handler setup.

**P6-07** — Default output threshold is `INFO`.

**P6-08** — Console output is enabled by default; file output is explicit.

**P6-09** — Handlers, formatters, propagation, streams, encoding, and file mode are not part of the ordinary constructor.

**P6-10** — UTF-8 and low-level logging behavior remain internal defaults.

**P6-11** — `trace.logger` is the advanced logger escape hatch.

**P6-12** — Configuration affects context and output policy, not event semantics.

**P6-13** — No configuration file or global initialization is required initially.

**P6-14** — Multiple `Trace` instances must remain independently configurable.

## 29. Acceptance Criteria

Phase 6 is complete when:

1. a useful TRACE instance can be created in one line;
2. configuration does not repeat across event calls;
3. ordinary users need no Python logging knowledge;
4. program and study context are inherited automatically;
5. log-file selection is simple;
6. severity threshold selection is simple;
7. low-level controls remain hidden;
8. expert users retain a future escape hatch through `trace.logger`;
9. defaults are sensible and backend-independent;
10. the design preserves the Phase 2 friction budget.

## 30. Outcome

TRACE configuration is intentionally small:

```python
trace = Trace("T14_01")
```

with optional enrichment:

```python
trace = Trace(
    program="T14_01",
    study="ABC123",
    log_file="logs/T14_01.log",
    level="INFO",
)
```

> **Configure TRACE once; keep operation logging focused on statistical meaning.**
