from __future__ import annotations

import logging
import os
import sys
import tempfile
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from types import TracebackType
from typing import Any, Literal

from .event import TraceEvent
from .operations import Operation
from .provenance import ExecutionProvenance, render_provenance
from .rendering import render_text
from .trace import Trace as _CoreTrace
from .trace import _LEVELS


class Trace(_CoreTrace):
    """TRACE orchestrator with live streaming and finalized review logs."""

    def read(
        self,
        name: str,
        *,
        source: str | None = None,
        rows: int | None = None,
        columns: int | None = None,
        details: Mapping[str, Any] | None = None,
    ) -> TraceEvent:
        event = super().read(
            name,
            source=source,
            rows=rows,
            columns=columns,
            details=details,
        )
        if source is not None:
            self._register_artifact(source, output=False)
        return event

    def output(
        self,
        name: str,
        path: str | Path,
        *,
        format: str | None = None,
        rows: int | None = None,
        details: Mapping[str, Any] | None = None,
    ) -> TraceEvent:
        event = super().output(
            name,
            path,
            format=format,
            rows=rows,
            details=details,
        )
        self._register_artifact(str(path), output=True)
        return event

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> Literal[False]:
        result = super().__exit__(exc_type, exc, tb)
        if exc_type is None and self.log_file is not None:
            self._finalize_log()
        return result

    def _emit(self, event: TraceEvent) -> None:
        text = render_text(event)
        self.logger.log(_LEVELS[event.severity.value], text)

        if self.log_file is None:
            return
        if event.operation is Operation.START:
            self._start_spool()
        spool_path = getattr(self, "_spool_path", None)
        if spool_path is not None:
            with spool_path.open("a", encoding="utf-8") as spool:
                spool.write(text)
                spool.write("\n")

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
        return logger

    def _start_spool(self) -> None:
        if getattr(self, "_spool_path", None) is not None:
            return
        if self.log_file is None:
            return

        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        handle = tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            prefix=f".{self.log_file.name}.{self.run_id}.",
            suffix=".events.tmp",
            dir=self.log_file.parent,
            delete=False,
        )
        handle.close()
        self._spool_path = Path(handle.name)
        self._executed_at = datetime.now(timezone.utc).isoformat(
            timespec="seconds"
        ).replace("+00:00", "Z")
        self._input_artifacts: list[str] = []
        self._output_artifacts: list[str] = []

    def _register_artifact(self, path: str, *, output: bool) -> None:
        if getattr(self, "_spool_path", None) is None:
            return
        artifacts = (
            self._output_artifacts if output else self._input_artifacts
        )
        if path not in artifacts:
            artifacts.append(path)

    def _finalize_log(self) -> None:
        spool_path = getattr(self, "_spool_path", None)
        if spool_path is None or self.log_file is None:
            return

        provenance = ExecutionProvenance(
            program=self.program,
            run_id=self.run_id,
            executed=self._executed_at,
            input_artifacts=tuple(self._input_artifacts),
            output_artifacts=tuple(self._output_artifacts),
        )
        staging = tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            prefix=f".{self.log_file.name}.{self.run_id}.",
            suffix=".final.tmp",
            dir=self.log_file.parent,
            delete=False,
        )
        staging_path = Path(staging.name)
        try:
            with staging:
                staging.write(render_provenance(provenance))
                staging.write("\n\n")
                with spool_path.open("r", encoding="utf-8") as spool:
                    for line in spool:
                        staging.write(line)
            os.replace(staging_path, self.log_file)
            spool_path.unlink()
            self._spool_path = None
        finally:
            if staging_path.exists():
                staging_path.unlink()
