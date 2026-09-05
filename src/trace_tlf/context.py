from dataclasses import dataclass, field
from typing import Optional, Tuple


@dataclass(frozen=True, slots=True)
class TraceContext:
    """Structured execution context attached to a TRACE event."""

    program: str
    study: Optional[str] = None
    run_id: Optional[str] = None
    step: Optional[str] = None
    step_path: Tuple[str, ...] = field(default_factory=tuple)
    trace_version: Optional[str] = None

    def __post_init__(self) -> None:
        if not isinstance(self.program, str) or not self.program.strip():
            raise ValueError("program must be a non-empty string")

        if self.study is not None and not isinstance(self.study, str):
            raise TypeError("study must be a string or None")

        if self.run_id is not None and not isinstance(self.run_id, str):
            raise TypeError("run_id must be a string or None")

        if self.step is not None and not isinstance(self.step, str):
            raise TypeError("step must be a string or None")

        if not isinstance(self.step_path, tuple):
            object.__setattr__(self, "step_path", tuple(self.step_path))

        if not all(isinstance(item, str) for item in self.step_path):
            raise TypeError("step_path must contain only strings")

        if self.trace_version is not None and not isinstance(self.trace_version, str):
            raise TypeError("trace_version must be a string or None")

    def to_dict(self) -> dict:
        result = {
            "program": self.program,
            "study": self.study,
            "run_id": self.run_id,
            "step": self.step,
            "step_path": list(self.step_path),
            "trace_version": self.trace_version,
        }
        return {key: value for key, value in result.items() if value not in (None, [], ())}
