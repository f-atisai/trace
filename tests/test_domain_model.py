from trace_tlf.context import TraceContext
from trace_tlf.event import TraceEvent
from trace_tlf.operations import Operation
from trace_tlf.severity import Severity
from trace_tlf.status import Status


def test_filter_event_can_represent_before_after():
    event = TraceEvent(
        severity=Severity.INFO,
        operation=Operation.FILTER,
        object="ADSL",
        action="SAFFL == 'Y' applied",
        metrics={"before": 754, "after": 720},
    )
    assert event.metrics["before"] == 754
    assert event.metrics["after"] == 720


def test_validate_event_can_represent_status():
    event = TraceEvent(
        severity=Severity.INFO,
        operation=Operation.VALIDATE,
        object="ADSL",
        action="USUBJID uniqueness verified",
        status=Status.SUCCESS,
    )
    assert event.status is Status.SUCCESS


def test_end_event_can_represent_duration():
    event = TraceEvent(
        severity=Severity.INFO,
        operation=Operation.END,
        object="T14_01",
        action="execution completed",
        status=Status.SUCCESS,
        metrics={"duration_seconds": 8.24},
    )
    assert event.metrics["duration_seconds"] == 8.24


def test_step_event_can_contain_step_context():
    context = TraceContext(
        program="T14_01",
        study="ABC123",
        run_id="run-001",
        step="Analysis population",
        step_path=("Analysis population",),
        trace_version="0.0-prototype",
    )
    event = TraceEvent(
        severity=Severity.INFO,
        operation=Operation.STEP,
        object="Analysis population",
        action="started",
        context=context,
    )
    assert event.context is not None
    assert event.context.step == "Analysis population"
    assert event.context.step_path == ("Analysis population",)


def test_details_and_metrics_stay_separate():
    event = TraceEvent(
        severity=Severity.INFO,
        operation=Operation.MERGE,
        object="ADAE",
        action="merged with ADSL",
        metrics={"left_rows": 4127, "right_rows": 754},
        details={"on": "USUBJID", "how": "left"},
    )
    assert "left_rows" in event.metrics
    assert "on" not in event.metrics
    assert "on" in event.details
    assert "left_rows" not in event.details


def test_sprint_exit_event_representation():
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


def test_event_has_no_rendered_message_field():
    event = TraceEvent(
        severity=Severity.INFO,
        operation=Operation.CHECK,
        object="ADSL",
        action="row count observed",
    )
    assert not hasattr(event, "message")
    assert not hasattr(event, "rendered")


def test_unknown_operation_is_rejected():
    try:
        TraceEvent(
            severity=Severity.INFO,
            operation="SUBSET",
            object="ADSL",
            action="subset applied",
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Unknown operation should be rejected")
