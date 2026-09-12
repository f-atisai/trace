from __future__ import annotations

import logging
import sys
import time
from collections.abc import Mapping, Sequence
from numbers import Integral, Real
from pathlib import Path
from types import TracebackType
from typing import Any, Literal
from uuid import uuid4

from .context import TraceContext
from .event import TraceEvent
from .operations import Operation
from .rendering import render_text
from .severity import Severity
from .status import Status

_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

_OPERATION_HINTS = {
    "SUBSET": "FILTER",
    "WHERE": "FILTER",
    "JOIN": "MERGE",
    "COMBINE": "MERGE",
    "LOAD": "READ",
    "EXPORT": "OUTPUT",
}


class Trace:
    """TRACE for Python alpha public orchestrator."""

    def __init__(
        self,
        program: str,
        *,
        study: str | None = None,
        log_file: str | Path | None = None,
        level: str = "INFO",
    ) -> None:
        if not isinstance(program, str) or not program.strip():
            raise ValueError("program must be a non-empty string")
        if study is not None and not isinstance(study, str):
            raise TypeError("study must be a string or None")

        self.program = program
        self.study = study
        self.run_id = uuid4().hex
        self.level = self._normalize_level(level)
        self.log_file = Path(log_file) if log_file is not None else None
        self.context = TraceContext(
            program=self.program,
            study=self.study,
            run_id=self.run_id,
        )
        self.logger = self._build_logger()
        self._lifecycle_state = "NOT_STARTED"
        self._started_at: float | None = None
        self._step_stack: list[str] = []

    def __enter__(self) -> Trace:
        if self._lifecycle_state == "RUNNING":
            raise RuntimeError("Trace instance is already running")
        if self._lifecycle_state == "ENDED":
            raise RuntimeError(
                "Trace instance lifecycle has ended and cannot be reused"
            )
        self._lifecycle_state = "RUNNING"
        self._started_at = time.monotonic()
        self._record(
            operation=Operation.START,
            object=self.program,
            action="execution started",
            severity=Severity.INFO,
        )
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> Literal[False]:
        if self._lifecycle_state != "RUNNING":
            raise RuntimeError("Trace lifecycle is not running")
        started_at = self._started_at
        duration = time.monotonic() - started_at if started_at is not None else 0.0
        self._lifecycle_state = "ENDED"
        self._started_at = None
        if exc_type is None:
            self._record(
                operation=Operation.END,
                object=self.program,
                action="execution completed",
                metrics={"duration_seconds": duration},
                status=Status.SUCCESS,
                severity=Severity.INFO,
            )
            return False
        try:
            self._record(
                operation=Operation.END,
                object=self.program,
                action="execution failed",
                metrics={"duration_seconds": duration},
                details={"exception_type": exc_type.__name__},
                status=Status.FAIL,
                severity=Severity.ERROR,
            )
        except Exception:
            # Never replace the program's original exception with instrumentation failure.
            pass
        return False

    def step(self, name: str) -> _StepScope:
        self._require_text(name, "step name")
        return _StepScope(self, name)

    def read(
        self,
        name: str,
        *,
        source: str | None = None,
        rows: int | None = None,
        columns: int | None = None,
        details: Mapping[str, Any] | None = None,
    ) -> TraceEvent:
        self._require_name(name, "name")
        self._require_non_negative_int(rows, "rows")
        self._require_non_negative_int(columns, "columns")
        event_details = self._merge_details(details, source=source)
        metrics = self._compact_mapping(rows=rows, columns=columns)
        return self._record(
            operation=Operation.READ,
            object=name,
            action="loaded",
            metrics=metrics,
            details=event_details,
        )

    def check(
        self,
        name: str,
        check: str,
        *,
        metrics: Mapping[str, Any] | None = None,
        details: Mapping[str, Any] | None = None,
    ) -> TraceEvent:
        self._require_name(name, "name")
        self._require_text(check, "check")
        return self._record(
            operation=Operation.CHECK,
            object=name,
            action=check,
            metrics=metrics,
            details=details,
        )

    def filter(
        self,
        name: str,
        condition: str,
        *,
        result: str | None = None,
        before: int | None = None,
        after: int | None = None,
        removed: int | None = None,
        details: Mapping[str, Any] | None = None,
    ) -> TraceEvent:
        self._require_name(name, "name")
        self._require_text(condition, "condition")
        if result is not None:
            self._require_name(result, "result")
        self._require_non_negative_int(before, "before")
        self._require_non_negative_int(after, "after")
        self._require_non_negative_int(removed, "removed")
        if before is not None and after is not None and after > before:
            raise ValueError("after must be <= before for a FILTER operation")
        if removed is None and before is not None and after is not None:
            removed = before - after
        if (
            before is not None
            and after is not None
            and removed is not None
            and before - after != removed
        ):
            raise ValueError(
                "removed must equal before - after when all three are supplied"
            )
        metrics = self._compact_mapping(
            before=before,
            after=after,
            removed=removed,
        )
        event_details = self._merge_details(details, result=result)
        return self._record(
            operation=Operation.FILTER,
            object=name,
            action=f"{condition} applied",
            metrics=metrics,
            details=event_details,
        )

    def sort(
        self,
        name: str,
        *,
        by: str | Sequence[str],
        ascending: bool | Sequence[bool] | None = None,
        details: Mapping[str, Any] | None = None,
    ) -> TraceEvent:
        self._require_name(name, "name")
        by_value = self._normalize_string_or_sequence(by, "by")
        event_details = self._merge_details(
            details,
            by=by_value,
            ascending=ascending,
        )
        return self._record(
            operation=Operation.SORT,
            object=name,
            action="sorted",
            details=event_details,
        )

    def derive(
        self,
        variable: str,
        *,
        dataset: str | None = None,
        source: str | Sequence[str] | None = None,
        method: str | None = None,
        details: Mapping[str, Any] | None = None,
    ) -> TraceEvent:
        self._require_name(variable, "variable")
        event_details = self._merge_details(
            details,
            dataset=dataset,
            source=source,
            method=method,
        )
        return self._record(
            operation=Operation.DERIVE,
            object=variable,
            action="created",
            details=event_details,
        )

    def transform(
        self,
        name: str,
        transformation: str,
        *,
        source: str | None = None,
        result: str | None = None,
        details: Mapping[str, Any] | None = None,
    ) -> TraceEvent:
        self._require_name(name, "name")
        self._require_text(transformation, "transformation")
        event_details = self._merge_details(
            details,
            source=source,
            result=result,
        )
        return self._record(
            operation=Operation.TRANSFORM,
            object=name,
            action=transformation,
            details=event_details,
        )

    def merge(
        self,
        left: str,
        right: str,
        *,
        on: str | Sequence[str] | None = None,
        how: str | None = None,
        result: str | None = None,
        left_rows: int | None = None,
        right_rows: int | None = None,
        result_rows: int | None = None,
        metrics: Mapping[str, Any] | None = None,
        details: Mapping[str, Any] | None = None,
    ) -> TraceEvent:
        self._require_name(left, "left")
        self._require_name(right, "right")
        for value, label in (
            (left_rows, "left_rows"),
            (right_rows, "right_rows"),
            (result_rows, "result_rows"),
        ):
            self._require_non_negative_int(value, label)
        on_value = (
            self._normalize_string_or_sequence(on, "on")
            if on is not None
            else None
        )
        event_details = self._merge_details(
            details,
            left=left,
            right=right,
            on=on_value,
            how=how,
            result=result,
        )
        event_metrics = self._normalize_mapping(metrics, "metrics")
        event_metrics.update(
            self._compact_mapping(
                left_rows=left_rows,
                right_rows=right_rows,
                result_rows=result_rows,
            )
        )
        return self._record(
            operation=Operation.MERGE,
            object=f"{left} + {right}",
            action="merged",
            metrics=event_metrics,
            details=event_details,
        )

    def aggregate(
        self,
        name: str,
        *,
        by: str | Sequence[str] | None = None,
        result: str | None = None,
        method: str | None = None,
        rows: int | None = None,
        details: Mapping[str, Any] | None = None,
    ) -> TraceEvent:
        self._require_name(name, "name")
        self._require_non_negative_int(rows, "rows")
        by_value = (
            self._normalize_string_or_sequence(by, "by")
            if by is not None
            else None
        )
        event_details = self._merge_details(
            details,
            by=by_value,
            result=result,
            method=method,
        )
        metrics = self._compact_mapping(rows=rows)
        return self._record(
            operation=Operation.AGGREGATE,
            object=name,
            action="summarized",
            metrics=metrics,
            details=event_details,
        )

    def analyze(
        self,
        source: str,
        analysis: str,
        *,
        method: str,
        population: str | None = None,
        result: str | None = None,
        details: Mapping[str, Any] | None = None,
    ) -> TraceEvent:
        self._require_name(source, "source")
        self._require_name(analysis, "analysis")
        self._require_text(method, "method")
        event_details = self._merge_details(
            details,
            source=source,
            method=method,
            population=population,
            result=result,
        )
        return self._record(
            operation=Operation.ANALYZE,
            object=analysis,
            action="analyzed",
            details=event_details,
        )

    def validate(
        self,
        name: str,
        check: str,
        *,
        passed: bool,
        metrics: Mapping[str, Any] | None = None,
        details: Mapping[str, Any] | None = None,
    ) -> TraceEvent:
        self._require_name(name, "name")
        self._require_text(check, "check")
        if not isinstance(passed, bool):
            raise TypeError("passed must be a bool")
        status = Status.SUCCESS if passed else Status.FAIL
        severity = Severity.INFO if passed else Severity.WARNING
        return self._record(
            operation=Operation.VALIDATE,
            object=name,
            action=check,
            metrics=metrics,
            details=details,
            status=status,
            severity=severity,
        )

    def output(
        self,
        name: str,
        path: str | Path,
        *,
        format: str | None = None,
        rows: int | None = None,
        details: Mapping[str, Any] | None = None,
    ) -> TraceEvent:
        self._require_name(name, "name")
        self._require_non_negative_int(rows, "rows")
        if not isinstance(path, (str, Path)):
            raise TypeError("path must be a string or Path")
        path_value = str(path)
        if not path_value:
            raise ValueError("path must not be empty")
        event_details = self._merge_details(
            details,
            path=path_value,
            format=format,
        )
        metrics = self._compact_mapping(rows=rows)
        return self._record(
            operation=Operation.OUTPUT,
            object=name,
            action="written",
            metrics=metrics,
            details=event_details,
        )

    def log(
        self,
        operation: Operation | str,
        *,
        object: str | None = None,
        action: str,
        metrics: Mapping[str, Any] | None = None,
        details: Mapping[str, Any] | None = None,
        status: Status | str | None = None,
    ) -> TraceEvent:
        """Emit an advanced canonical structured TRACE event.

        This is the supported alpha escape hatch for unusual semantic events.
        Tier 1 helpers remain the preferred statistical-programming API.
        """
        normalized_operation = self._normalize_operation(operation)
        self._require_text(action, "action")
        if object is not None:
            self._require_text(object, "object")
        normalized_metrics = self._normalize_mapping(metrics, "metrics")
        normalized_details = self._normalize_mapping(details, "details")
        normalized_status = self._normalize_status(status)
        return self._record(
            operation=normalized_operation,
            object=object,
            action=action,
            metrics=normalized_metrics,
            details=normalized_details,
            status=normalized_status,
        )

    def _record(
        self,
        *,
        operation: Operation | str,
        object: str | None,
        action: str,
        metrics: Mapping[str, Any] | None = None,
        details: Mapping[str, Any] | None = None,
        status: Status | str | None = None,
        severity: Severity = Severity.INFO,
    ) -> TraceEvent:
        event = self._create_event(
            operation=operation,
            object=object,
            action=action,
            metrics=metrics,
            details=details,
            status=status,
            severity=severity,
        )
        self._emit(event)
        return event

    def _create_event(
        self,
        *,
        operation: Operation | str,
        object: str | None,
        action: str,
        metrics: Mapping[str, Any] | None,
        details: Mapping[str, Any] | None,
        status: Status | str | None,
        severity: Severity = Severity.INFO,
    ) -> TraceEvent:
        normalized_operation = self._normalize_operation(operation)
        normalized_status = self._normalize_status(status)
        normalized_metrics = {
            key: self._normalize_numeric(value)
            for key, value in (metrics or {}).items()
        }
        normalized_details = {
            key: self._normalize_numeric(value)
            for key, value in (details or {}).items()
        }
        return TraceEvent(
            severity=severity,
            operation=normalized_operation,
            object=object,
            action=action,
            metrics=normalized_metrics,
            details=normalized_details,
            status=normalized_status,
            context=self._event_context(),
        )

    def _emit(self, event: TraceEvent) -> None:
        self.logger.log(_LEVELS[event.severity.value], render_text(event))

    def _event_context(self) -> TraceContext:
        step_path = tuple(self._step_stack)
        step = step_path[-1] if step_path else None
        return TraceContext(
            program=self.program,
            study=self.study,
            run_id=self.run_id,
            step=step,
            step_path=step_path,
            trace_version=self.context.trace_version,
        )

    @staticmethod
    def _require_name(value: str, label: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{label} must be a non-empty string")

    @staticmethod
    def _require_text(value: str, label: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{label} must be a non-empty string")

    @staticmethod
    def _require_non_negative_int(value: int | None, label: str) -> None:
        if value is None:
            return
        if isinstance(value, bool) or not isinstance(value, Integral):
            raise TypeError(f"{label} must be an integral value or None")
        if value < 0:
            raise ValueError(f"{label} must be >= 0")

    @staticmethod
    def _normalize_numeric(value: Any) -> Any:
        if isinstance(value, bool):
            return value
        if isinstance(value, Integral):
            return int(value)
        if isinstance(value, Real):
            return float(value)
        return value

    @staticmethod
    def _normalize_string_or_sequence(
        value: str | Sequence[str],
        label: str,
    ) -> str | list[str]:
        if isinstance(value, str):
            if not value.strip():
                raise ValueError(f"{label} must not be empty")
            return value
        if not isinstance(value, Sequence):
            raise TypeError(f"{label} must be a string or sequence of strings")
        normalized = list(value)
        if not normalized:
            raise ValueError(f"{label} must not be empty")
        if not all(isinstance(item, str) and item.strip() for item in normalized):
            raise TypeError(f"{label} must contain only non-empty strings")
        return normalized

    @staticmethod
    def _compact_mapping(**values: Any) -> dict[str, Any]:
        return {
            key: Trace._normalize_numeric(value)
            for key, value in values.items()
            if value is not None
        }

    @staticmethod
    def _merge_details(
        details: Mapping[str, Any] | None,
        **values: Any,
    ) -> dict[str, Any]:
        merged = dict(details or {})
        for key, value in values.items():
            if value is not None:
                merged[key] = value
        return merged

    @staticmethod
    def _normalize_operation(operation: Operation | str) -> Operation:
        if isinstance(operation, Operation):
            return operation
        if not isinstance(operation, str):
            raise TypeError("operation must be an Operation or string")
        normalized = operation.upper()
        try:
            return Operation(normalized)
        except ValueError as exc:
            hint = _OPERATION_HINTS.get(normalized)
            if hint is not None:
                raise ValueError(
                    f"unknown TRACE operation {operation!r}; "
                    f"use canonical operation {hint!r}"
                ) from exc
            allowed = ", ".join(item.value for item in Operation)
            raise ValueError(
                f"unknown TRACE operation {operation!r}; "
                f"expected one of: {allowed}"
            ) from exc

    @staticmethod
    def _normalize_mapping(
        value: Mapping[str, Any] | None,
        label: str,
    ) -> dict[str, Any]:
        if value is None:
            return {}
        if not isinstance(value, Mapping):
            raise TypeError(f"{label} must be a mapping or None")
        return {
            key: Trace._normalize_numeric(item)
            for key, item in value.items()
        }

    @staticmethod
    def _normalize_status(status: Status | str | None) -> Status | None:
        if status is None or isinstance(status, Status):
            return status
        if not isinstance(status, str):
            raise TypeError("status must be a Status, string, or None")
        try:
            return Status(status.upper())
        except ValueError as exc:
            allowed = ", ".join(item.value for item in Status)
            raise ValueError(
                f"invalid status {status!r}; expected one of: {allowed}"
            ) from exc

    def _build_logger(self) -> logging.Logger:
        logger_name = f"trace_tlf.{self.program}.{self.run_id}"
        logger = logging.getLogger(logger_name)
        logger.setLevel(_LEVELS[self.level])
        logger.propagate = False
        logger.handlers.clear()
        formatter = logging.Formatter("%(message)s")
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(_LEVELS[self.level])
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        if self.log_file is not None:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(self.log_file, encoding="utf-8")
            file_handler.setLevel(_LEVELS[self.level])
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        return logger

    @staticmethod
    def _normalize_level(level: str) -> str:
        if not isinstance(level, str):
            raise TypeError("level must be a string")
        normalized = level.upper()
        if normalized not in _LEVELS:
            allowed = ", ".join(_LEVELS)
            raise ValueError(
                f"invalid level {level!r}; expected one of: {allowed}"
            )
        return normalized


class _StepScope:
    """Internal context manager for TRACE step instrumentation."""

    def __init__(self, trace: Trace, name: str) -> None:
        self._trace = trace
        self._name = name
        self._started_at: float | None = None
        self._entered = False

    def __enter__(self) -> _StepScope:
        if self._entered:
            raise RuntimeError("step scope cannot be re-entered")
        self._entered = True
        self._trace._step_stack.append(self._name)
        self._started_at = time.monotonic()
        try:
            self._trace._record(
                operation=Operation.STEP,
                object=self._name,
                action="started",
                severity=Severity.INFO,
            )
        except Exception:
            self._trace._step_stack.pop()
            self._entered = False
            self._started_at = None
            raise
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> Literal[False]:
        if not self._entered:
            raise RuntimeError("step scope is not active")
        duration = (
            time.monotonic() - self._started_at
            if self._started_at is not None
            else 0.0
        )
        try:
            if exc_type is None:
                self._trace._record(
                    operation=Operation.STEP,
                    object=self._name,
                    action="completed",
                    metrics={"duration_seconds": duration},
                    status=Status.SUCCESS,
                    severity=Severity.INFO,
                )
            else:
                try:
                    self._trace._record(
                        operation=Operation.STEP,
                        object=self._name,
                        action="failed",
                        metrics={"duration_seconds": duration},
                        details={"exception_type": exc_type.__name__},
                        status=Status.FAIL,
                        severity=Severity.ERROR,
                    )
                except Exception:
                    # Never replace the program's original exception with instrumentation.
                    pass
        finally:
            popped = self._trace._step_stack.pop()
            if popped != self._name:
                raise RuntimeError("TRACE step stack became inconsistent")
            self._entered = False
            self._started_at = None
        return False
