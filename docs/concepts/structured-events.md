# Structured events

TRACE records statistical-programming activity as structured events before rendering it as a human-readable log line.

This is the key architectural distinction between TRACE and arbitrary `logging.info()` messages.

```text
TRACE call
   ↓
structured event
   ↓
renderer
   ↓
execution log
```

A TRACE event can carry information such as:

```text
operation
object
action
metrics
details
status
context
severity
```

For example:

```python
trace.filter(
    "ADSL",
    "SAFFL == 'Y'",
    before=754,
    after=720,
)
```

records the statistical operation and its diagnostics in a structured form. The default renderer then produces a concise line such as:

```text
INFO [FILTER] [ADSL] SAFFL == 'Y' applied – N=754 → 720
```

The user-facing value is consistency. Statistical operations such as `READ`, `FILTER`, `DERIVE`, `MERGE`, `ANALYZE`, `VALIDATE`, and `OUTPUT` follow the same vocabulary and rendering conventions across programs.

## TRACE does not perform the statistical work

TRACE records the operation after or around the code that performs it.

```python
safety = adsl.query("SAFFL == 'Y'")

trace.filter(
    "ADSL",
    "SAFFL == 'Y'",
    before=len(adsl),
    after=len(safety),
)
```

Here, pandas performs the filter. TRACE records what the program reports about that operation.

The same principle applies to Polars or other analytical libraries: TRACE remains backend-independent and does not take ownership of the underlying transformation.

## Why keep events separate from rendered text?

Separating event creation from rendering gives TRACE a stable semantic layer without forcing users to construct arbitrary strings themselves.

That supports:

- consistent human-readable logs;
- validation of operation-specific diagnostics;
- lifecycle context such as `START`, `STEP`, and `END`;
- program-level provenance; and
- future renderers or integrations without changing normal instrumentation calls.

The public API remains intentionally simpler than the internal event model. Ordinary users should work through `Trace` methods rather than depend on internal event classes.

For the supported statistical-operation vocabulary, see [TRACE Core Operations v0.1](../framework/core-operations-v0.1.md). For the public Python methods, see the [TRACE API](../api/README.md).
