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
from .trace import _LEVELS
from .trace import Trace as _CoreTrace


class Trace(_CoreTrace):
    """TRACE orchestrator with live streaming and finalized review logs."""

    _spool_path: Path | None

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
        if self.log_file is None:
            return result

        if exc_type is not None:
            try:
                self._finalize_log()
            except BaseException:
                # The program exception always takes precedence over TRACE
                # finalization or cleanup failures.
                pass
            return result

        try:
            self._finalize_log()
        except Exception as finalization_error:
            raise RuntimeError(
                "TRACE log finalization failed; the event spool was preserved "
                "when possible"
            ) from finalization_error
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
            return

        # Simple, non-context TRACE usage retains the alpha behavior of
        # writing log_file immediately. Managed runs use the spool above so
        # the completed review log can be finalized with provenance first.
        self._write_direct_log(text)

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

    def _write_direct_log(self, text: str) -> None:
        if self.log_file is None:
            return
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        with self.log_file.open("a", encoding="utf-8") as log:
            log.write(text)
            log.write("\n")

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
        staging_path: Path | None = None
        try:
            staging = tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                prefix=f".{self.log_file.name}.{self.run_id}.",
                suffix=".final.tmp",
                dir=self.log_file.parent,
                delete=False,
            )
            staging_path = Path(staging.name)
            with staging:
                staging.write(render_provenance(provenance))
                staging.write("\n\n")
                with spool_path.open("r", encoding="utf-8") as spool:
                    for line in spool:
                        staging.write(line)
                staging.flush()
                os.fsync(staging.fileno())

            os.replace(staging_path, self.log_file)
            spool_path.unlink()
            self._spool_path = None
        finally:
            if staging_path is not None:
                self._safe_unlink(staging_path)

    @staticmethod
    def _safe_unlink(path: Path) -> None:
        try:
            path.unlink()
        except FileNotFoundError:
            pass
        except OSError:
            # Cleanup is best-effort on a failed finalization path. The
            # primary finalization error must remain the reported failure.
            pass
