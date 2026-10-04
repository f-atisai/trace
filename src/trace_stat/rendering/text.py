from __future__ import annotations

from typing import Any

from ..event import TraceEvent
from ..operations import Operation
from ..status import Status


def render_text(event: TraceEvent) -> str:
    """Render a TraceEvent as a concise human-readable TRACE log line.

    Rendering is intentionally separate from TraceEvent. The event remains
    the semantic source of truth; this module owns presentation.
    """
    prefix = _prefix(event)
    body = _body(event)
    return f"{prefix} {body}".rstrip()


def _prefix(event: TraceEvent) -> str:
    parts = [
        event.severity.value,
        f"[{event.operation.value}]",
    ]

    if event.object:
        parts.append(f"[{event.object}]")

    return " ".join(parts)


def _body(event: TraceEvent) -> str:
    operation = event.operation

    if operation is Operation.READ:
        return _render_read(event)
    if operation is Operation.FILTER:
        return _render_filter(event)
    if operation is Operation.SORT:
        return _render_sort(event)
    if operation is Operation.DERIVE:
        return _render_derive(event)
    if operation is Operation.TRANSFORM:
        return _render_transform(event)
    if operation is Operation.MERGE:
        return _render_merge(event)
    if operation is Operation.AGGREGATE:
        return _render_aggregate(event)
    if operation is Operation.ANALYZE:
        return _render_analyze(event)
    if operation is Operation.VALIDATE:
        return _render_validate(event)
    if operation is Operation.OUTPUT:
        return _render_output(event)
    if operation is Operation.START:
        return event.action
    if operation is Operation.END:
        return _render_end(event)
    if operation is Operation.STEP:
        return _render_step(event)

    return _join(event.action, _render_generic_details(event))


def _render_read(event: TraceEvent) -> str:
    parts = []
    rows = event.metrics.get("rows")
    columns = event.metrics.get("columns")
    source = event.details.get("source")

    if source is not None:
        parts.append(f"source={_display(source)}")
    if rows is not None:
        parts.append(f"N={rows}")
    if columns is not None:
        parts.append(f"Vars={columns}")

    return _join(event.action, ", ".join(parts))


def _render_filter(event: TraceEvent) -> str:
    before = event.metrics.get("before")
    after = event.metrics.get("after")

    if before is not None and after is not None:
        return _join(event.action, f"N={before} → {after}")

    removed = event.metrics.get("removed")
    if removed is not None:
        return _join(event.action, f"removed={removed}")

    return event.action


def _render_sort(event: TraceEvent) -> str:
    parts = []
    by = event.details.get("by")
    ascending = event.details.get("ascending")

    if by is not None:
        parts.append(f"by={_display(by)}")
    if ascending is not None:
        parts.append(f"ascending={_display(ascending)}")

    return _join(event.action, ", ".join(parts))


def _render_derive(event: TraceEvent) -> str:
    parts = []
    for key in ("dataset", "source", "method"):
        value = event.details.get(key)
        if value is not None:
            parts.append(f"{key}={_display(value)}")
    return _join(event.action, ", ".join(parts))


def _render_transform(event: TraceEvent) -> str:
    parts = []
    for key in ("source", "result"):
        value = event.details.get(key)
        if value is not None:
            parts.append(f"{key}={_display(value)}")
    return _join(event.action, ", ".join(parts))


def _render_merge(event: TraceEvent) -> str:
    parts = []

    for key in ("on", "how", "result"):
        value = event.details.get(key)
        if value is not None:
            parts.append(f"{key}={_display(value)}")

    rendered_metric_keys = set()
    for key, label in (
        ("left_rows", "left N"),
        ("right_rows", "right N"),
        ("result_rows", "result N"),
    ):
        value = event.metrics.get(key)
        if value is not None:
            parts.append(f"{label}={value}")
            rendered_metric_keys.add(key)

    for key, value in event.metrics.items():
        if key not in rendered_metric_keys:
            parts.append(f"{key}={_display(value)}")

    return _join(event.action, ", ".join(parts))


def _render_aggregate(event: TraceEvent) -> str:
    parts = []

    for key in ("by", "result", "method"):
        value = event.details.get(key)
        if value is not None:
            parts.append(f"{key}={_display(value)}")

    rows = event.metrics.get("rows")
    if rows is not None:
        parts.append(f"N={rows}")

    return _join(event.action, ", ".join(parts))


def _render_analyze(event: TraceEvent) -> str:
    parts = []
    for key in ("source", "method", "population", "result"):
        value = event.details.get(key)
        if value is not None:
            parts.append(f"{key}={_display(value)}")
    return _join(event.action, ", ".join(parts))


def _render_validate(event: TraceEvent) -> str:
    if event.status is Status.SUCCESS:
        outcome = "PASS"
    elif event.status is Status.FAIL:
        outcome = "FAIL"
    elif event.status is Status.SKIP:
        outcome = "SKIP"
    elif event.status is Status.PARTIAL:
        outcome = "PARTIAL"
    else:
        outcome = None

    metrics = _render_metrics(event.metrics)
    suffix = ", ".join(part for part in (outcome, metrics) if part)
    return _join(event.action, suffix)


def _render_output(event: TraceEvent) -> str:
    parts = []

    path = event.details.get("path")
    format_ = event.details.get("format")
    rows = event.metrics.get("rows")

    if path is not None:
        parts.append(_display(path))
    if format_ is not None:
        parts.append(f"format={_display(format_)}")
    if rows is not None:
        parts.append(f"N={rows}")

    return _join(event.action, ", ".join(parts))


def _render_end(event: TraceEvent) -> str:
    duration = event.metrics.get("duration_seconds")
    exception_type = event.details.get("exception_type")

    suffix_parts = []
    if duration is not None:
        suffix_parts.append(_format_duration(duration))
    if exception_type is not None:
        suffix_parts.append(str(exception_type))

    return _join(event.action, " – ".join(suffix_parts), separator=" – ")


def _render_step(event: TraceEvent) -> str:
    duration = event.metrics.get("duration_seconds")
    exception_type = event.details.get("exception_type")

    suffix_parts = []
    if duration is not None:
        suffix_parts.append(_format_duration(duration))
    if exception_type is not None:
        suffix_parts.append(str(exception_type))

    return _join(event.action, " – ".join(suffix_parts), separator=" – ")


def _render_generic_details(event: TraceEvent) -> str:
    parts = []
    metrics = _render_metrics(event.metrics)
    if metrics:
        parts.append(metrics)

    for key, value in event.details.items():
        parts.append(f"{key}={_display(value)}")

    return ", ".join(parts)


def _render_metrics(metrics: dict[str, Any] | Any) -> str:
    return ", ".join(f"{key}={_display(value)}" for key, value in metrics.items())


def _display(value: Any) -> str:
    if isinstance(value, (list, tuple)):
        return ",".join(str(item) for item in value)
    return str(value)


def _format_duration(value: Any) -> str:
    try:
        seconds = float(value)
    except (TypeError, ValueError):
        return str(value)

    if seconds < 1:
        return f"{seconds:.3f}s"

    rendered = f"{seconds:.2f}".rstrip("0").rstrip(".")
    return f"{rendered}s"


def _join(action: str, suffix: str | None, *, separator: str = " – ") -> str:
    if not suffix:
        return action
    return f"{action}{separator}{suffix}"
