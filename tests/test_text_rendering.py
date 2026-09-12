from trace_tlf.event import TraceEvent
from trace_tlf.operations import Operation
from trace_tlf.rendering import render_text
from trace_tlf.severity import Severity
from trace_tlf.status import Status


def test_render_read():
    event = TraceEvent(
        severity=Severity.INFO,
        operation=Operation.READ,
        object="ADSL",
        action="loaded",
        metrics={"rows": 754, "columns": 16},
    )
    assert render_text(event) == "INFO [READ] [ADSL] loaded – N=754, Vars=16"


def test_render_check():
    event = TraceEvent(
        severity=Severity.INFO,
        operation=Operation.CHECK,
        object="ADSL",
        action="row count observed",
        metrics={"rows": 754},
    )
    assert render_text(event) == "INFO [CHECK] [ADSL] row count observed – rows=754"


def test_render_filter():
    event = TraceEvent(
        severity=Severity.INFO,
        operation=Operation.FILTER,
        object="ADSL",
        action="SAFFL == 'Y' applied",
        metrics={"before": 754, "after": 720},
    )
    expected = "INFO [FILTER] [ADSL] SAFFL == 'Y' applied – N=754 → 720"
    assert render_text(event) == expected


def test_render_sort():
    event = TraceEvent(
        severity=Severity.INFO,
        operation=Operation.SORT,
        object="ADAE",
        action="sorted",
        details={"by": ["USUBJID", "AESTDTC"], "ascending": True},
    )
    expected = "INFO [SORT] [ADAE] sorted – by=USUBJID,AESTDTC, ascending=True"
    assert render_text(event) == expected


def test_render_derive():
    event = TraceEvent(
        severity=Severity.INFO,
        operation=Operation.DERIVE,
        object="AGEGR1",
        action="created",
        details={"dataset": "ADSL", "source": "AGE"},
    )
    expected = "INFO [DERIVE] [AGEGR1] created – dataset=ADSL, source=AGE"
    assert render_text(event) == expected


def test_render_transform():
    event = TraceEvent(
        severity=Severity.INFO,
        operation=Operation.TRANSFORM,
        object="ADSL",
        action="treatment labels standardized",
        details={"source": "TRT01A", "result": "TRT01A"},
    )
    expected = (
        "INFO [TRANSFORM] [ADSL] treatment labels standardized – "
        "source=TRT01A, result=TRT01A"
    )
    assert render_text(event) == expected


def test_render_merge():
    event = TraceEvent(
        severity=Severity.INFO,
        operation=Operation.MERGE,
        object="ADAE + ADSL",
        action="merged",
        metrics={
            "left_rows": 4127,
            "right_rows": 754,
            "result_rows": 4127,
            "matched_subjects": 751,
        },
        details={"on": "USUBJID", "how": "left", "result": "ADAE_ANALYSIS"},
    )
    expected = (
        "INFO [MERGE] [ADAE + ADSL] merged – on=USUBJID, how=left, "
        "result=ADAE_ANALYSIS, left N=4127, right N=754, result N=4127, "
        "matched_subjects=751"
    )
    assert render_text(event) == expected


def test_render_aggregate():
    event = TraceEvent(
        severity=Severity.INFO,
        operation=Operation.AGGREGATE,
        object="Safety Population",
        action="summarized",
        metrics={"rows": 6},
        details={
            "by": ["TRT01A", "AGEGR1"],
            "result": "summary",
            "method": "descriptive statistics",
        },
    )
    expected = (
        "INFO [AGGREGATE] [Safety Population] summarized – by=TRT01A,AGEGR1, "
        "result=summary, method=descriptive statistics, N=6"
    )
    assert render_text(event) == expected


def test_render_analyze():
    event = TraceEvent(
        severity=Severity.INFO,
        operation=Operation.ANALYZE,
        object="Overall survival",
        action="analyzed",
        details={
            "source": "ADTTE",
            "method": "Kaplan-Meier",
            "population": "ITT",
            "result": "km_summary",
        },
    )
    expected = (
        "INFO [ANALYZE] [Overall survival] analyzed – source=ADTTE, "
        "method=Kaplan-Meier, population=ITT, result=km_summary"
    )
    assert render_text(event) == expected


def test_render_validate_pass():
    event = TraceEvent(
        severity=Severity.INFO,
        operation=Operation.VALIDATE,
        object="ADSL",
        action="USUBJID uniqueness",
        status=Status.SUCCESS,
    )
    assert render_text(event) == "INFO [VALIDATE] [ADSL] USUBJID uniqueness – PASS"


def test_render_validate_fail():
    event = TraceEvent(
        severity=Severity.WARNING,
        operation=Operation.VALIDATE,
        object="ADSL",
        action="USUBJID uniqueness",
        status=Status.FAIL,
        metrics={"duplicates": 2},
    )
    expected = (
        "WARNING [VALIDATE] [ADSL] USUBJID uniqueness – FAIL, duplicates=2"
    )
    assert render_text(event) == expected


def test_render_output():
    event = TraceEvent(
        severity=Severity.INFO,
        operation=Operation.OUTPUT,
        object="T14_01",
        action="written",
        metrics={"rows": 42},
        details={"path": "T14_01.xlsx"},
    )
    assert render_text(event) == "INFO [OUTPUT] [T14_01] written – T14_01.xlsx, N=42"


def test_render_start():
    event = TraceEvent(
        severity=Severity.INFO,
        operation=Operation.START,
        object="T14_01",
        action="execution started",
    )
    assert render_text(event) == "INFO [START] [T14_01] execution started"


def test_render_end_success():
    event = TraceEvent(
        severity=Severity.INFO,
        operation=Operation.END,
        object="T14_01",
        action="execution completed",
        status=Status.SUCCESS,
        metrics={"duration_seconds": 8.24},
    )
    assert render_text(event) == "INFO [END] [T14_01] execution completed – 8.24s"


def test_render_end_failure():
    event = TraceEvent(
        severity=Severity.ERROR,
        operation=Operation.END,
        object="T14_01",
        action="execution failed",
        status=Status.FAIL,
        metrics={"duration_seconds": 2.14},
        details={"exception_type": "ValueError"},
    )
    expected = "ERROR [END] [T14_01] execution failed – 2.14s – ValueError"
    assert render_text(event) == expected


def test_render_step_started():
    event = TraceEvent(
        severity=Severity.INFO,
        operation=Operation.STEP,
        object="Analysis population",
        action="started",
    )
    assert render_text(event) == "INFO [STEP] [Analysis population] started"


def test_render_step_completed():
    event = TraceEvent(
        severity=Severity.INFO,
        operation=Operation.STEP,
        object="Analysis population",
        action="completed",
        status=Status.SUCCESS,
        metrics={"duration_seconds": 0.031},
    )
    expected = "INFO [STEP] [Analysis population] completed – 0.031s"
    assert render_text(event) == expected


def test_event_remains_renderer_agnostic():
    event = TraceEvent(
        severity=Severity.INFO,
        operation=Operation.FILTER,
        object="ADSL",
        action="SAFFL == 'Y' applied",
        metrics={"before": 754, "after": 720},
    )
    assert not hasattr(event, "render")
    assert not hasattr(event, "message")
