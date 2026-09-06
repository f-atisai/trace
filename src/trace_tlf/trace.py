from __future__ import annotations

import logging
import sys
from collections.abc import Mapping
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
        """Create and emit a structured TRACE event.

        This is intentionally minimal for Sprint 3. The full generic-event
        contract is deferred to the dedicated generic logging sprint.
        """
        event = self._create_event(
            operation=operation,
            object=object,
            action=action,
            metrics=metrics,
            details=details,
            status=status,
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
