from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutionProvenance:
    """Internal program-level provenance summary for one TRACE run."""

    program: str
    run_id: str
    executed: str
    input_artifacts: tuple[str, ...] = ()
    output_artifacts: tuple[str, ...] = ()


def render_provenance(provenance: ExecutionProvenance) -> str:
    """Render the provenance header for a finalized TRACE review log."""
    lines = [
        "TRACE EXECUTION",
        "",
        f"Program:  {provenance.program}",
        f"Run ID:   {provenance.run_id}",
        f"Executed: {provenance.executed}",
        "",
        "Input artifacts:",
    ]
    lines.extend(_render_artifacts(provenance.input_artifacts))
    lines.extend(["", "Output artifacts:"])
    lines.extend(_render_artifacts(provenance.output_artifacts))
    return "\n".join(lines)


def _render_artifacts(artifacts: tuple[str, ...]) -> list[str]:
    if not artifacts:
        return ["  (none)"]
    return [f"  {artifact}" for artifact in artifacts]
