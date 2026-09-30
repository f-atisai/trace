# Program-level provenance

TRACE can add lightweight run context to a finalized log so a reviewer can identify which program execution and physical artifacts the log belongs to.

Provenance is recorded once for the run rather than repeated on each TRACE event.

The Developer Preview model is:

```text
TRACE EXECUTION

Program:  T14_01
Run ID:   7eab...
Executed: 2026-09-12T14:32:18Z

Input artifacts:
  data/adsl.xpt

Output artifacts:
  outputs/tlf_population.rtf
```

The fields are intentionally small:

- **Program** — the statistical program name supplied to `Trace`.
- **Run ID** — the identifier for one TRACE execution.
- **Executed** — the run timestamp.
- **Input artifacts** — physical sources registered through supported READ behavior.
- **Output artifacts** — physical outputs registered through supported OUTPUT behavior.

## Registering artifacts

During a managed run, TRACE uses supported READ and OUTPUT calls to collect artifact paths.

```python
with Trace("T14_01", log_file="logs/T14_01.log") as trace:
    trace.read("ADSL", source="data/adsl.xpt", rows=len(adsl))

    # statistical work

    trace.output("T14_01", "outputs/tlf_population.rtf")
```

The READ and OUTPUT events still describe the statistical workflow. The provenance block identifies the physical artifacts associated with the run.

```text
READ event        what input became available
input provenance  which physical artifact participated

OUTPUT event      what production action occurred
output provenance which physical artifact was produced
```

## Scope

TRACE provenance is deliberately program-level. It does not add provenance fields to every statistical event.

The current Developer Preview does not expose artifact hashing, environment fingerprinting, or provenance configuration controls.

For implementation details such as log finalization and artifact registration behavior, see the design document [TRACE Execution Provenance](../design/provenance.md). For the supported public behavior, see the [TRACE API](../api/README.md).
