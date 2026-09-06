import pytest

from trace_tlf import Operation, Trace, TraceEvent


def test_trace_smoke_event_and_console_output(capsys):
    trace = Trace("T14_01")

    event = trace.log(
        "CHECK",
        object="ADSL",
        action="prototype event",
    )

    captured = capsys.readouterr()

    assert isinstance(event, TraceEvent)
    assert event.operation is Operation.CHECK
    assert event.object == "ADSL"
    assert event.action == "prototype event"
    assert event.context is not None
    assert event.context.program == "T14_01"
    assert event.context.run_id == trace.run_id
    assert captured.err.strip() == (
        "INFO [CHECK] [ADSL] prototype event"
    )


def test_trace_inherits_study_context():
    trace = Trace("T14_01", study="ABC123")

    event = trace.log(
        "CHECK",
        object="ADSL",
        action="prototype event",
    )

    assert event.context is not None
    assert event.context.study == "ABC123"


def test_trace_writes_optional_file(tmp_path):
    log_file = tmp_path / "logs" / "T14_01.log"
    trace = Trace("T14_01", log_file=log_file)

    trace.log(
        "CHECK",
        object="ADSL",
        action="prototype event",
    )

    assert log_file.read_text(encoding="utf-8").strip() == (
        "INFO [CHECK] [ADSL] prototype event"
    )


def test_trace_uses_info_threshold_by_default():
    trace = Trace("T14_01")

    assert trace.level == "INFO"
    assert trace.logger.level == 20


def test_trace_accepts_case_insensitive_level():
    trace = Trace("T14_01", level="warning")

    assert trace.level == "WARNING"
    assert trace.logger.level == 30


def test_trace_rejects_unknown_level():
    with pytest.raises(ValueError):
        Trace("T14_01", level="VERBOSE")


def test_trace_instances_have_distinct_run_ids_and_loggers():
    first = Trace("T14_01")
    second = Trace("T14_01")

    assert first.run_id != second.run_id
    assert first.logger.name != second.logger.name


def test_trace_does_not_expose_data_transformation_behavior():
    trace = Trace("T14_01")

    assert not hasattr(trace, "query")
    assert not hasattr(trace, "merge_data")
    assert not hasattr(trace, "to_json")
