# TRACE Execution Provenance

**Phase:** 10.5 — Define Minimal Execution Provenance  
**Status:** Accepted design specification  
**Scope:** Program-level execution identity and physical input/output artifact provenance

## 1. Purpose

TRACE provenance identifies **which program execution and physical artifacts the recorded execution evidence belongs to**.

It is deliberately minimal. TRACE is not an environment-capture, system-inventory, or reproducibility fingerprinting tool.

The provenance model is:

```text
Execution provenance
├── program
├── run_id
├── started_at
├── ended_at
├── input_artifacts
│   ├── path
│   └── sha256 (optional)
└── output_artifacts
    ├── path
    └── sha256 (optional)
```

Provenance is recorded at **program level**. It must not be repeated on ordinary semantic events.

## 2. Execution identity

### Program

`program` identifies the statistical program being executed.

Examples:

```text
T14_01
tlf_population.py
analysis/tlf-04-efficacy-ancova.qmd
```

TRACE does not prescribe whether a project uses a logical program identifier, filename, or document path. The value should be stable and meaningful to a reviewer.

### Run ID

`run_id` uniquely identifies one TRACE execution.

The run ID distinguishes repeated executions of the same program and allows semantic events, diagnostics, and artifact provenance to be associated with the same run.

The existing TRACE run ID remains the execution identifier; Phase 10.5 does not introduce a second provenance-specific identifier.

## 3. Execution timestamps

TRACE records execution time in UTC using ISO 8601.

Canonical form:

```text
2026-09-12T14:32:18Z
```

The provenance model uses:

```text
started_at
ended_at
```

Both belong to the program run rather than individual semantic events.

`started_at` records when TRACE execution began. `ended_at` records when execution ended, including failed executions where lifecycle handling reaches termination.

Event-level timestamps are a separate concern and are not required by the minimal provenance model.

### Timestamp rules

- use UTC;
- serialize in ISO 8601 form;
- prefer `Z` for UTC output;
- retain sufficient precision for execution identification without requiring sub-second precision in the human-readable rendering;
- do not convert provenance timestamps to local time in the canonical structured representation.

A renderer may present local time additionally in the future, but UTC remains the canonical provenance value.

## 4. Input artifacts

An **input artifact** is an external physical artifact actually consumed by the program during the execution.

Examples:

```text
data/adsl.parquet
data/adae.parquet
specifications/tlf_shell.xlsx
```

An input artifact is not simply every file that exists in the project or every object mentioned by the program.

The minimum representation is:

```text
path
```

An optional hash may be added:

```text
path=data/adsl.parquet
sha256=8f31...
```

### READ is not provenance

A `READ` event and input-artifact provenance are related but distinct.

```text
READ event
    answers: What input object became available to the analysis?

input artifact provenance
    answers: Which physical artifact participated in this execution?
```

For example:

```text
Input artifact: data/adsl.parquet
READ event:     [READ] [ADSL] loaded
```

The artifact path must not be repeated on every semantic event merely because that data contributed downstream.

## 5. Output artifacts

An **output artifact** is an external physical artifact actually produced by the execution.

Examples:

```text
rtf/t14-2-01.rtf
output/tlf_population.rtf
adam/adae.xpt
```

The minimum representation is:

```text
path
```

An optional hash may be added:

```text
path=rtf/t14-2-01.rtf
sha256=a791...
```

An `OUTPUT` semantic event records that the program produced an output. Program-level output provenance identifies the resulting physical artifact associated with the run. The two concepts must not be collapsed merely because they commonly refer to the same file.

## 6. Artifact hashing

Hashes are optional and exist to answer:

> **Is the artifact being reviewed the same physical artifact that participated in this execution?**

When hashing is used, TRACE uses **SHA-256**.

### Hashing rules

- hash the artifact bytes;
- do not hash arbitrary in-memory DataFrames or model objects as part of minimal provenance;
- do not define a semantic-dataframe hash that depends on row ordering, serialization choices, type coercion, or backend behavior;
- do not store artifact contents;
- do not require hashing for basic TRACE adoption;
- do not automatically hash very large artifacts without an explicit implementation policy;
- a missing hash means only that TRACE did not record one, not that the artifact is untrusted or invalid.

Artifact hashing is identity evidence, not proof of analytical correctness or file quality.

## 7. Program-level rendering

A concise reviewer-facing representation may be:

```text
TRACE EXECUTION

Program:  tlf_population.py
Run ID:   7eab...
Started:  2026-09-12T14:32:18Z
Ended:    2026-09-12T14:32:19Z

Input artifacts:
  data/adsl.parquet
  sha256: 8f31...

Output artifacts:
  rtf/tlf_population.rtf
  sha256: a791...
```

With multiple artifacts:

```text
Input artifacts:
  data/adsl.parquet
    sha256: 8f31...
  data/adae.parquet
    sha256: 73ad...

Output artifacts:
  rtf/t14-2-01.rtf
    sha256: a791...
  listings/l14-2-01.rtf
```

The provenance block should appear once for the execution. Ordinary TRACE events remain focused on semantic activity and diagnostics.

## 8. Structured model

Phase 10.5 defines the conceptual structure without freezing the public Python API or storage class.

A structured representation should be able to express:

```text
program: string
run_id: string
started_at: UTC timestamp
ended_at: UTC timestamp | null
input_artifacts: sequence of artifacts
output_artifacts: sequence of artifacts
```

where an artifact contains:

```text
path: string
sha256: string | null
```

`ended_at` may be absent while a run is active. How and when artifacts are registered, finalized, or rendered belongs to implementation design.

## 9. Scope boundaries

Minimal provenance does **not** include:

```text
Git commit
Git branch or dirty state
Python version
package versions
operating system
hostname
username
machine identity
CPU / memory information
container image
full environment variables
working-directory snapshots
source-code copies
artifact contents
```

These may be reconsidered only if a demonstrated review or reproducibility requirement justifies the added complexity, privacy risk, and output noise.

TRACE should not collect broad environment data simply because it is technically available.

## 10. Relationship to execution evidence

Execution provenance is one of three complementary evidence forms:

```text
semantic events       what happened
observed diagnostics  what measurable evidence describes it
execution provenance  which run and artifacts the evidence belongs to
```

Provenance does not change the meaning of a semantic event and must not be injected repeatedly into event details.

The reviewer model and diagnostic-evidence rules are defined in [`reviewer-experience.md`](reviewer-experience.md).

## 11. Phase 10.5 decisions

- Execution provenance is program-level, not event-level.
- `program` and the existing `run_id` identify the execution.
- Canonical execution timestamps are `started_at` and `ended_at` in UTC ISO 8601 form.
- Input provenance includes only external artifacts actually consumed by the run.
- Output provenance includes only external artifacts actually produced by the run.
- Artifact hashes are optional SHA-256 values calculated from file bytes.
- Hashes are artifact-identity evidence, not statistical validation.
- `READ`/`OUTPUT` events and input/output artifact provenance remain conceptually distinct.
- Provenance metadata must not be repeated across semantic events.
- Environment fingerprinting remains out of scope.
- Phase 10.5 defines the model only; it does not freeze provenance API methods or implement hashing/runtime artifact capture.

## 12. Exit criteria

The model can represent:

```text
Program: tlf_population.py
Run ID: 7eab...
Started: 2026-09-12T14:32:18Z
Ended: 2026-09-12T14:32:19Z

Inputs:
  data/adsl.parquet
  sha256=8f31...

Outputs:
  rtf/tlf_population.rtf
  sha256=a791...
```

without introducing environment fingerprinting or adding provenance noise to semantic events.
