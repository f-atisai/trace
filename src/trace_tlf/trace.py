from __future__ import annotations

import logging
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any
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
    """Disposable reference implementation of the TRACE core orchestrator."""

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

    # ------------------------------------------------------------------
    # Tier 1 API
    # ------------------------------------------------------------------

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

        event_details = self._merge_details(
            details,
            source=source,
        )
        metrics = self._compact_mapping(
            rows=rows,
            columns=columns,
        )

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
        before: int | None = None,
        after: int | None = None,
        removed: int | None = None,
        details: Mapping[str, Any] | None = None,
    ) -> TraceEvent:
        self._require_name(name, "name")
        self._require_text(condition, "condition")
        self._require_non_negative_int(before, "before")
        self._require_non_negative_int(after, "after")
        self._require_non_negative_int(removed, "removed")

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

        return self._record(
            operation=Operation.FILTER,
            object=name,
            action=f"{condition} applied",
            metrics=metrics,
            details=details,
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
        matched: int | None = None,
        unmatched_left: int | None = None,
        unmatched_right: int | None = None,
        details: Mapping[str, Any] | None = None,
    ) -> TraceEvent:
        self._require_name(left, "left")
        self._require_name(right, "right")

        for value, label in (
            (left_rows, "left_rows"),
            (right_rows, "right_rows"),
            (result_rows, "result_rows"),
            (matched, "matched"),
            (unmatched_left, "unmatched_left"),
            (unmatched_right, "unmatched_right"),
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
        metrics = self._compact_mapping(
            left_rows=left_rows,
            right_rows=right_rows,
            result_rows=result_rows,
            matched=matched,
            unmatched_left=unmatched_left,
            unmatched_right=unmatched_right,
        )

        return self._record(
            operation=Operation.MERGE,
            object=f"{left} + {right}",
            action="merged",
            metrics=metrics,
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
        name: str,
        *,
        method: str,
        population: str | None = None,
        result: str | None = None,
        details: Mapping[str, Any] | None = None,
    ) -> TraceEvent:
        self._require_name(name, "name")
        self._require_text(method, "method")

        event_details = self._merge_details(
            details,
            method=method,
            population=population,
            result=result,
        )

        return self._record(
            operation=Operation.ANALYZE,
            object=name,
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

    # ------------------------------------------------------------------
    # Generic structured event API (minimal Sprint 3/4 form)
    # ------------------------------------------------------------------

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
        """Emit a canonical structured TRACE event.

        This is the Tier 2 escape hatch. It accepts only canonical TRACE
        operations and preserves the same TraceEvent model used by Tier 1.
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

    # ------------------------------------------------------------------
    # Shared event path
    # ------------------------------------------------------------------

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
        return TraceEvent(
            severity=severity,
            operation=operation,
            object=object,
            action=action,
            metrics=metrics or {},
            details=details or {},
            status=status,
            context=self.context,
        )

    def _emit(self, event: TraceEvent) -> None:
        self.logger.log(
            _LEVELS[event.severity.value],
            render_text(event),
        )

    # ------------------------------------------------------------------
    # Prototype normalization / validation helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _require_name(value: str, label: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{label} must be a non-empty string")

    @staticmethod
    def _require_text(value: str, label: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{label} must be a non-empty string")

    @staticmethod
    def _require_non_negative_int(
        value: int | None,
        label: str,
    ) -> None:
        if value is None:
            return
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"{label} must be an int or None")
        if value < 0:
            raise ValueError(f"{label} must be >= 0")

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
            key: value
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
        return dict(value)

    @staticmethod
    def _normalize_status(
        status: Status | str | None,
    ) -> Status | None:
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

    # ------------------------------------------------------------------
    # Logger setup
    # ------------------------------------------------------------------

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

            file_handler = logging.FileHandler(
                self.log_file,
                encoding="utf-8",
            )
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
