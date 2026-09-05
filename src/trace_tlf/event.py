from dataclasses import dataclass, field
from typing import Any, Mapping, Optional

from .context import TraceContext
from .operations import Operation
from .severity import Severity
from .status import Status


def _copy_mapping(value: Optional[Mapping[str, Any]], field_name: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise TypeError(f"{field_name} must be a mapping or None")
    return dict(value)


@dataclass(frozen=True, slots=True)
class TraceEvent:
    """Canonical structured TRACE event.

    This model stores semantics only. It deliberately contains no rendered
    log string and no dependency on runtime analytical objects such as
    pandas DataFrames.
    """

    severity: Severity
    operation: Operation
    action: str
    object: Optional[str] = None
    metrics: Mapping[str, Any] = field(default_factory=dict)
    details: Mapping[str, Any] = field(default_factory=dict)
    status: Optional[Status] = None
    context: Optional[TraceContext] = None

    def __post_init__(self) -> None:
        if not isinstance(self.severity, Severity):
            try:
                object.__setattr__(self, "severity", Severity(self.severity))
            except (TypeError, ValueError) as exc:
                raise ValueError(f"invalid severity: {self.severity!r}") from exc

        if not isinstance(self.operation, Operation):
            try:
                object.__setattr__(self, "operation", Operation(self.operation))
            except (TypeError, ValueError) as exc:
                raise ValueError(f"invalid operation: {self.operation!r}") from exc

        if not isinstance(self.action, str) or not self.action.strip():
            raise ValueError("action must be a non-empty string")

        if self.object is not None and not isinstance(self.object, str):
            raise TypeError("object must be a string or None")

        if self.status is not None and not isinstance(self.status, Status):
            try:
                object.__setattr__(self, "status", Status(self.status))
            except (TypeError, ValueError) as exc:
                raise ValueError(f"invalid status: {self.status!r}") from exc

        if self.context is not None and not isinstance(self.context, TraceContext):
            raise TypeError("context must be a TraceContext or None")

        object.__setattr__(self, "metrics", _copy_mapping(self.metrics, "metrics"))
        object.__setattr__(self, "details", _copy_mapping(self.details, "details"))

    def to_dict(self) -> dict[str, Any]:
        """Return a plain structured representation suitable for inspection."""
        result: dict[str, Any] = {
            "severity": self.severity.value,
            "operation": self.operation.value,
            "object": self.object,
            "action": self.action,
            "metrics": dict(self.metrics),
            "details": dict(self.details),
            "status": self.status.value if self.status is not None else None,
            "context": self.context.to_dict() if self.context is not None else None,
        }

        return {
            key: value
            for key, value in result.items()
            if value not in (None, {}, [], ())
        }
