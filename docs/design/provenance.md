# TRACE Execution Provenance

**Phase:** 10.5 / Developer Preview implementation  
**Status:** Phase 1 implemented  
**Scope:** Program-level execution identity and physical input/output artifact provenance

## 1. Purpose

TRACE provenance identifies **which program execution and physical artifacts the recorded execution evidence belongs to**.

Provenance is program-level. It is not repeated on ordinary semantic events, and it must not require TRACE to delay live event output.

The Developer Preview model is:

```text
Execution provenance
├── program
├── run_id
├── executed
├── input_artifacts
└── output_artifacts
```

Artifact hashing and environment fingerprinting are outside the current alpha implementation.

## 2. Execution identity

`program` identifies the statistical program. The existing `run_id` uniquely identifies one TRACE execution; provenance does not introduce a second run identifier.

`executed` is recorded in UTC ISO 8601 form when a managed TRACE run begins:

```text
2026-09-12T14:32:18Z
```

A single execution timestamp is intentionally used in the concise reviewer-facing summary. Event durations remain lifecycle diagnostics rather than provenance fields.

## 3. Artifact provenance

An input artifact is an external physical artifact consumed by the run. An output artifact is an external physical artifact produced by the run.

For the Developer Preview:

- `trace.read(..., source=...)` registers `source` as an input artifact during a managed run;
- `trace.output(..., path=...)` registers `path` as an output artifact during a managed run;
- first-seen order is preserved;
- duplicate paths are listed once;
- registration does not change READ or OUTPUT event rendering.

READ/OUTPUT events and provenance remain distinct:

```text
READ event             what input object became available
input provenance       which physical artifact participated

OUTPUT event           what production action occurred
output provenance      which physical artifact was produced
```

## 4. Streaming and final-log architecture

TRACE has two output responsibilities:

```text
live console output    what is happening now
final TRACE log        what happened in this run
```

Semantic events continue to stream immediately. TRACE does not hold the full event stream in memory.

When `log_file` is configured, each rendered event is also appended to an internal file-backed event spool:

```text
TraceEvent
   │
   ├──► live console
   └──► temporary event spool
```

At successful managed-run completion, TRACE:

1. emits END through the normal live path;
2. finalizes the program-level provenance summary;
3. creates a staging file containing provenance, a blank line, and the event spool;
4. atomically publishes the staging file to `log_file`;
5. removes the completed event spool.

The resulting review log is:

```text
TRACE EXECUTION

Program:  T14_01
Run ID:   7eab...
Executed: 2026-09-12T14:32:18Z

Input artifacts:
  data/adsl.xpt

Output artifacts:
  outputs/tlf_population.rtf

INFO [START] [T14_01] execution started
INFO [READ] [ADSL] loaded – source=data/adsl.xpt
...
INFO [END] [T14_01] execution completed – 0.84s
```

The semantic event text in the final log is the same rendered text that was streamed live.

## 5. `log_file` semantics

`log_file` identifies the finalized provenance-first TRACE review log for a managed run.

Temporary spool and staging files are internal implementation details. TRACE does not expose them through the public API.

Without `log_file`, TRACE remains a live console tool and does not silently create a persistent provenance log.

## 6. Structured events remain authoritative

The event path remains:

```text
statistical program
       ↓
TraceEvent
       ↓
renderer
       ↓
text event
       ├──► console
       └──► event spool
```

`TraceEvent` remains the source of semantic truth. The spool stores the rendered review representation only so the final human-readable log can be assembled after execution.

## 7. Current scope boundaries

The Developer Preview provenance implementation does not include:

```text
artifact hashes
hash_artifacts constructor option
Git commit or branch
Python/package versions
operating system or machine identity
environment variables
source-code copies
artifact contents
automatic incomplete-run recovery
public sink or spool APIs
```

Artifact hashing remains a post-alpha API discussion and must not change the current constructor during the Developer Preview.

## 8. Phase 1 decisions

- Semantic TRACE events remain live-streaming.
- No full-run semantic event buffer is kept in memory.
- Provenance remains program-level.
- `READ source` and `OUTPUT path` register physical artifacts during managed runs.
- Artifact paths preserve first-seen order and are deduplicated.
- `log_file` represents the finalized review artifact.
- The final log places provenance before semantic events.
- Final logs are assembled through a staging file and atomic replacement.
- No persistent provenance file is created when `log_file` is absent.
- The public `Trace` constructor remains unchanged.
- Hashing and failure-hardening behavior are deferred.

## 9. Phase 2 boundary

Phase 2 will harden normal-exception finalization, finalization failures, spool preservation, cleanup guarantees, repeated destination replacement, and the rule that TRACE failures must not mask an active program exception.

Hard process termination may prevent finalization because Python context-manager exit is not guaranteed. Automatic recovery of incomplete spools is not part of the alpha scope.
