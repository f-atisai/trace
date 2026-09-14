# TRACE Execution Provenance

**Phase:** 10.5 / Developer Preview implementation  
**Status:** Phase 2 implemented  
**Scope:** Program-level execution identity, artifact provenance, and finalized review-log durability

## 1. Purpose

TRACE provenance identifies **which program execution and physical artifacts the recorded execution evidence belongs to**.

Provenance is program-level. It is not repeated on ordinary semantic events, and TRACE does not delay live event output to construct it.

The Developer Preview model is:

```text
Execution provenance
├── program
├── run_id
├── executed
├── input_artifacts
└── output_artifacts
```

Artifact hashing and environment fingerprinting are outside the alpha implementation.

## 2. Execution identity

`program` identifies the statistical program. The existing `run_id` uniquely identifies one TRACE execution; provenance does not introduce a second run identifier.

`executed` is recorded in UTC ISO 8601 form when a managed TRACE run begins:

```text
2026-09-12T14:32:18Z
```

A single execution timestamp is intentionally used in the concise reviewer-facing summary. Event durations remain lifecycle diagnostics rather than provenance fields.

## 3. Artifact provenance

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

A run with no registered artifacts renders `(none)` explicitly in the corresponding provenance sections.

## 4. Streaming and finalized-log architecture

TRACE separates live execution visibility from the finalized review artifact:

```text
TraceEvent
   │
   ├──► live console immediately
   └──► file-backed event spool
                  │
                  ▼
        execution reaches __exit__
                  │
                  ▼
        finalized provenance
                  │
                  ▼
        staging review log
                  │
                  ▼
          atomic replacement
                  │
                  ▼
             log_file
```

TRACE does **not** retain the full event stream in memory. Each rendered semantic event streams immediately and, when `log_file` is configured for a managed run, is appended to an internal file-backed spool in the same order.

On normal completion or an ordinary Python exception, TRACE attempts to finalize the review log after the END event has been emitted. The staging file contains:

```text
provenance block
blank line
complete event spool
```

The staging file is flushed and closed before publication. TRACE then uses atomic replacement where supported by the host filesystem. The destination is never incrementally rewritten by TRACE.

A repeated run targeting the same `log_file` therefore replaces the previous complete review log with the new complete run rather than appending or mixing runs.

## 5. Final log

A finalized review log has this form:

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

Failed program execution is also finalized when Python reaches context-manager exit:

```text
...
ERROR [STEP] [Analysis Population] failed – ValueError
ERROR [END] [T14_01] execution failed – ValueError
```

The semantic event text in the final log is the same rendered text that was streamed live. Provenance fields do not leak into individual semantic event rendering.

## 6. Failure precedence

The statistical program's active exception has absolute precedence over TRACE finalization failures.

If user code raises inside the context, TRACE:

1. attempts to emit the failure-related STEP/END evidence;
2. attempts to finalize the provenance-first log;
3. suppresses any secondary finalization or cleanup failure;
4. propagates the original program exception unchanged.

This applies to failures in provenance rendering, spool reading, staging creation/writing, final-file replacement, and cleanup.

If there is **no** active program exception and finalization fails, TRACE raises a `RuntimeError` indicating that log finalization failed. TRACE must not silently report a successful managed run when its configured review artifact could not be finalized.

## 7. Evidence preservation and cleanup

After successful publication, TRACE removes the completed event spool. Staging files are also removed after successful finalization.

If finalization fails before publication, TRACE preserves the event spool when practical. This retains the streamed execution evidence for diagnosis even though it is an internal file rather than a finalized review artifact.

A failed staging file is cleaned up on a best-effort basis. Cleanup failure does not replace the primary finalization failure and never replaces an already-active program exception.

Temporary spool and staging paths are internal implementation details and are not part of the public API.

## 8. Incomplete runs

Normal Python completion and normal Python exceptions execute context-manager finalization:

```text
normal completion  → finalized provenance-first log
Python exception   → finalized provenance-first log attempted; original exception propagates
```

Hard process termination is different:

```text
process kill
interpreter crash
power loss
os._exit(...)
other termination that bypasses __exit__
        ↓
finalization not guaranteed
```

Such termination may leave only the internal event spool. TRACE does not implement automatic spool discovery, recovery, or replay in the alpha Developer Preview. Recovery tooling may be considered after alpha feedback.

## 9. `log_file` semantics

`log_file` identifies the finalized provenance-first TRACE review artifact for a managed run.

Without `log_file`, TRACE remains a live console tool and does not silently create a persistent provenance log.

The configured destination is published only after the complete new review log has been assembled. If publication fails before replacement, an existing destination remains intact where the filesystem's atomic replacement semantics provide that guarantee.

## 10. Structured events remain authoritative

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

## 11. Alpha scope boundaries

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
public sink, spool, staging, or recovery APIs
```

Artifact hashing remains a post-alpha API discussion and must not change the current constructor during the Developer Preview.

## 12. Frozen Developer Preview rules

- Semantic TRACE events stream live.
- TRACE does not use a full-run in-memory event buffer.
- Provenance is program-level rather than event-level.
- `READ source` and `OUTPUT path` register physical artifacts during managed runs.
- Artifact paths preserve first-seen order and are deduplicated.
- `log_file` is the finalized review artifact.
- Final logs are assembled after execution from provenance plus the event spool.
- Final publication uses a flushed, closed staging file and atomic replacement where supported.
- Normal Python failures still attempt finalization.
- An active program exception is never replaced by a TRACE finalization failure.
- A finalization failure without a program exception is surfaced as a TRACE runtime failure.
- Successful finalization removes temporary files.
- Failed finalization preserves the event spool when practical.
- Hard termination may leave an incomplete spool; alpha performs no automatic recovery.
- The public `Trace` constructor remains unchanged.
- Artifact hashing is deliberately deferred until post-alpha discussion.
