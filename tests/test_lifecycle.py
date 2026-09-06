import pytest

from trace_tlf import Trace


def test_successful_run_emits_start_and_success_end(capsys):
    trace = Trace("T14_01")

    with trace as active:
        assert active is trace

    output = capsys.readouterr().err.strip().splitlines()

    assert output[0] == "INFO [START] [T14_01] execution started"
    assert output[1].startswith(
        "INFO [END] [T14_01] execution completed – "
    )
    assert output[1].endswith("s")


def test_failed_run_emits_failed_end_and_reraises(capsys):
    trace = Trace("T14_01")

    with pytest.raises(ValueError, match="boom"):
        with trace:
            raise ValueError("boom")

    output = capsys.readouterr().err.strip().splitlines()

    assert output[0] == "INFO [START] [T14_01] execution started"
    assert output[1].startswith(
        "ERROR [END] [T14_01] execution failed – "
    )
    assert output[1].endswith(" – ValueError")


def test_nested_reentry_is_rejected():
    trace = Trace("T14_01")

    with trace:
        with pytest.raises(RuntimeError, match="already running"):
            with trace:
                pass


def test_reuse_after_end_is_rejected():
    trace = Trace("T14_01")

    with trace:
        pass

    with pytest.raises(RuntimeError, match="cannot be reused"):
        with trace:
            pass


def test_simple_trace_construction_emits_no_lifecycle_events(capsys):
    Trace("T14_01")

    assert capsys.readouterr().err == ""


def test_run_id_is_stable_for_instance():
    trace = Trace("T14_01")
    run_id = trace.run_id

    with trace:
        assert trace.run_id == run_id

    assert trace.run_id == run_id


def test_end_event_uses_monotonic_duration(monkeypatch, capsys):
    values = iter([100.0, 108.24])

    monkeypatch.setattr(
        "trace_tlf.trace.time.monotonic",
        lambda: next(values),
    )

    trace = Trace("T14_01")

    with trace:
        pass

    output = capsys.readouterr().err.strip().splitlines()

    assert output[1] == (
        "INFO [END] [T14_01] execution completed – 8.24s"
    )
