import pytest

from trace_tlf import Trace


def test_step_started_and_completed(capsys):
    trace = Trace("T14_01")

    with trace.step("Analysis population"):
        pass

    output = capsys.readouterr().err.strip().splitlines()

    assert output[0] == (
        "INFO [STEP] [Analysis population] started"
    )
    assert output[1].startswith(
        "INFO [STEP] [Analysis population] completed – "
    )


def test_event_inside_step_inherits_step_context():
    trace = Trace("T14_01")

    with trace.step("Analysis population"):
        event = trace.filter(
            "ADSL",
            "SAFFL == 'Y'",
            before=754,
            after=720,
        )

    assert event.context is not None
    assert event.context.step == "Analysis population"
    assert event.context.step_path == ("Analysis population",)


def test_nested_steps_preserve_full_step_path():
    trace = Trace("T14_01")

    with trace.step("Generate statistics"):
        with trace.step("Demographics"):
            event = trace.aggregate(
                "ADSL",
                by=["TRT01A", "AGEGR1"],
                result="summary",
            )

    assert event.context is not None
    assert event.context.step == "Demographics"
    assert event.context.step_path == (
        "Generate statistics",
        "Demographics",
    )


def test_parent_context_restored_after_child_step():
    trace = Trace("T14_01")

    with trace.step("Generate statistics"):
        with trace.step("Demographics"):
            pass

        event = trace.check(
            "summary",
            "demographics complete",
        )

    assert event.context is not None
    assert event.context.step == "Generate statistics"
    assert event.context.step_path == ("Generate statistics",)


def test_step_failure_emits_failed_and_reraises(capsys):
    trace = Trace("T14_01")

    with pytest.raises(ValueError, match="boom"):
        with trace.step("Analysis population"):
            raise ValueError("boom")

    output = capsys.readouterr().err.strip().splitlines()

    assert output[0] == (
        "INFO [STEP] [Analysis population] started"
    )
    assert output[1].startswith(
        "ERROR [STEP] [Analysis population] failed – "
    )
    assert output[1].endswith(" – ValueError")


def test_step_failure_inside_program_emits_step_then_end_failure(capsys):
    trace = Trace("T14_01")

    with pytest.raises(ValueError, match="boom"):
        with trace:
            with trace.step("Analysis population"):
                raise ValueError("boom")

    output = capsys.readouterr().err.strip().splitlines()

    assert output[0] == "INFO [START] [T14_01] execution started"
    assert output[1] == (
        "INFO [STEP] [Analysis population] started"
    )
    assert output[2].startswith(
        "ERROR [STEP] [Analysis population] failed – "
    )
    assert output[2].endswith(" – ValueError")
    assert output[3].startswith(
        "ERROR [END] [T14_01] execution failed – "
    )
    assert output[3].endswith(" – ValueError")


def test_nested_failure_emits_failure_for_each_active_scope(capsys):
    trace = Trace("T14_01")

    with pytest.raises(ValueError):
        with trace.step("Generate statistics"):
            with trace.step("Demographics"):
                raise ValueError()

    output = capsys.readouterr().err.strip().splitlines()

    assert output[0] == (
        "INFO [STEP] [Generate statistics] started"
    )
    assert output[1] == (
        "INFO [STEP] [Demographics] started"
    )
    assert output[2].startswith(
        "ERROR [STEP] [Demographics] failed – "
    )
    assert output[3].startswith(
        "ERROR [STEP] [Generate statistics] failed – "
    )


def test_step_context_is_cleared_after_exit():
    trace = Trace("T14_01")

    with trace.step("Analysis population"):
        pass

    event = trace.check("ADSL", "post-step check")

    assert event.context is not None
    assert event.context.step is None
    assert event.context.step_path == ()


def test_step_uses_monotonic_duration(monkeypatch, capsys):
    values = iter([20.0, 20.031])

    monkeypatch.setattr(
        "trace_tlf.trace.time.monotonic",
        lambda: next(values),
    )

    trace = Trace("T14_01")

    with trace.step("Analysis population"):
        pass

    output = capsys.readouterr().err.strip().splitlines()

    assert output[1] == (
        "INFO [STEP] [Analysis population] completed – 0.031s"
    )
