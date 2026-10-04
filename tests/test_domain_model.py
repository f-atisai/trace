from dataclasses import fields

import pytest

from trace_stat.context import TraceContext
from trace_stat.event import TraceEvent
from trace_stat.operations import Operation
from trace_stat.severity import Severity
from trace_stat.status import Status


def test_event_preserves_structured_fields():
    context = TraceContext(
        program="T14_01",
        study="ABC123",
        run_id="run-001",
        step="Analysis population",
        step_path=("Analysis population",),
    )
    event = TraceEvent(
        severity=Severity.INFO,
        operation=Operation.MERGE,
        object="ADAE + ADSL",
        action="merged",
        metrics={"left_rows": 4127, "right_rows": 754},
        details={"on": "USUBJID", "how": "left"},
        status=Status.SUCCESS,
        context=context,
    )
    assert event.to_dict() == {
        "severity": "INFO",
        "operation": "MERGE",
        "object": "ADAE + ADSL",
        "action": "merged",
        "metrics": {"left_rows": 4127, "right_rows": 754},
        "details": {"on": "USUBJID", "how": "left"},
        "status": "SUCCESS",
        "context": {
            "program": "T14_01",
            "study": "ABC123",
            "run_id": "run-001",
            "step": "Analysis population",
            "step_path": ["Analysis population"],
        },
    }


def test_event_normalizes_string_enums_for_serialization():
    event = TraceEvent(
        severity="INFO",
        operation="FILTER",
        object="ADSL",
        action="SAFFL == 'Y' applied",
        metrics={"before": 754, "after": 720},
    )
    assert event.to_dict() == {
        "severity": "INFO",
        "operation": "FILTER",
        "object": "ADSL",
        "action": "SAFFL == 'Y' applied",
        "metrics": {"before": 754, "after": 720},
    }


def test_event_copies_mapping_containers():
    metrics = {"rows": 754}
    details = {"source": "adsl.csv"}
    event = TraceEvent(
        severity=Severity.INFO,
        operation=Operation.READ,
        object="ADSL",
        action="loaded",
        metrics=metrics,
        details=details,
    )

    metrics["rows"] = 0
    details["source"] = "changed.csv"

    assert event.metrics == {"rows": 754}
    assert event.details == {"source": "adsl.csv"}


def test_event_schema_contains_only_structured_fields():
    assert [field.name for field in fields(TraceEvent)] == [
        "severity",
        "operation",
        "action",
        "object",
        "metrics",
        "details",
        "status",
        "context",
    ]


@pytest.mark.parametrize(
    ("field_name", "value", "error_type"),
    [
        ("severity", "NOTICE", ValueError),
        ("operation", "SUBSET", ValueError),
        ("action", "", ValueError),
        ("object", 42, TypeError),
        ("status", "PASS", ValueError),
        ("context", {}, TypeError),
        ("metrics", [], TypeError),
        ("details", [], TypeError),
    ],
)
def test_event_rejects_invalid_fields(field_name, value, error_type):
    values = {
        "severity": Severity.INFO,
        "operation": Operation.CHECK,
        "action": "row count observed",
    }
    values[field_name] = value

    with pytest.raises(error_type, match=field_name):
        TraceEvent(**values)
