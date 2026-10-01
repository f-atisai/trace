import pytest

from trace_tlf import Trace
from trace_tlf.operations import Operation
from trace_tlf.severity import Severity
from trace_tlf.status import Status


def test_read():
    trace = Trace("T14_01")
    event = trace.read("ADSL", source="adsl.csv", rows=754, columns=16)

    assert event.operation is Operation.READ
    assert event.object == "ADSL"
    assert event.action == "loaded"
    assert event.metrics == {"rows": 754, "columns": 16}
    assert event.details["source"] == "adsl.csv"


def test_check():
    trace = Trace("T14_01")
    event = trace.check("ADSL", "row count observed", metrics={"rows": 754})

    assert event.operation is Operation.CHECK
    assert event.object == "ADSL"
    assert event.action == "row count observed"
    assert event.metrics == {"rows": 754}


def test_filter_derives_removed_and_preserves_result_identity():
    trace = Trace("T14_01")
    event = trace.filter(
        "ADSL",
        "SAFFL == 'Y'",
        result="Safety Population",
        before=754,
        after=720,
    )

    assert event.object == "ADSL"
    assert event.action == "SAFFL == 'Y' applied"
    assert event.details["result"] == "Safety Population"
    assert event.metrics == {
        "before": 754,
        "after": 720,
        "removed": 34,
    }


def test_filter_rejects_empty_result_identity():
    trace = Trace("T14_01")

    with pytest.raises(ValueError):
        trace.filter("ADSL", "SAFFL == 'Y'", result="")


def test_filter_rejects_inconsistent_removed():
    trace = Trace("T14_01")

    with pytest.raises(ValueError):
        trace.filter(
            "ADSL",
            "SAFFL == 'Y'",
            before=754,
            after=720,
            removed=10,
        )


def test_sort():
    trace = Trace("T14_01")
    event = trace.sort(
        "ADAE",
        by=["USUBJID", "AESTDTC"],
        ascending=[True, False],
    )

    assert event.operation is Operation.SORT
    assert event.object == "ADAE"
    assert event.details == {
        "by": ["USUBJID", "AESTDTC"],
        "ascending": [True, False],
    }


def test_derive():
    trace = Trace("T14_01")
    event = trace.derive(
        "AGEGR1",
        dataset="ADSL",
        source="AGE",
        method="format",
    )

    assert event.operation is Operation.DERIVE
    assert event.object == "AGEGR1"
    assert event.details == {
        "dataset": "ADSL",
        "source": "AGE",
        "method": "format",
    }


def test_transform():
    trace = Trace("T14_01")
    event = trace.transform(
        "ADSL",
        "standardized treatment labels",
        source="TRT01A",
        result="TRT01A",
    )

    assert event.operation is Operation.TRANSFORM
    assert event.object == "ADSL"
    assert event.action == "standardized treatment labels"
    assert event.details == {
        "source": "TRT01A",
        "result": "TRT01A",
    }


def test_merge():
    trace = Trace("T14_01")
    event = trace.merge(
        "ADAE",
        "ADSL",
        on="USUBJID",
        how="left",
        result="ADAE_ANALYSIS",
        left_rows=4127,
        right_rows=754,
        result_rows=4127,
        metrics={"matched_subjects": 751},
    )

    assert event.operation is Operation.MERGE
    assert event.details == {
        "left": "ADAE",
        "right": "ADSL",
        "on": "USUBJID",
        "how": "left",
        "result": "ADAE_ANALYSIS",
    }
    assert event.metrics == {
        "matched_subjects": 751,
        "left_rows": 4127,
        "right_rows": 754,
        "result_rows": 4127,
    }


def test_aggregate():
    trace = Trace("T14_01")
    event = trace.aggregate(
        "ADSL",
        by=["TRT01A", "AGEGR1"],
        result="summary",
        method="descriptive statistics",
        rows=6,
    )

    assert event.operation is Operation.AGGREGATE
    assert event.object == "ADSL"
    assert event.details == {
        "by": ["TRT01A", "AGEGR1"],
        "result": "summary",
        "method": "descriptive statistics",
    }
    assert event.metrics == {"rows": 6}


def test_analyze():
    trace = Trace("T14_01")
    event = trace.analyze(
        "ADTTE",
        "Overall survival",
        method="Kaplan-Meier",
        population="ITT",
        result="km_summary",
    )

    assert event.operation is Operation.ANALYZE
    assert event.object == "Overall survival"
    assert event.action == "analyzed"
    assert event.details == {
        "source": "ADTTE",
        "method": "Kaplan-Meier",
        "population": "ITT",
        "result": "km_summary",
    }


def test_validate_pass_maps_status_and_severity():
    trace = Trace("T14_01")
    event = trace.validate("ADSL", "USUBJID is unique", passed=True)

    assert event.operation is Operation.VALIDATE
    assert event.object == "ADSL"
    assert event.action == "USUBJID is unique"
    assert event.status is Status.SUCCESS
    assert event.severity is Severity.INFO


def test_validate_fail_maps_status_and_severity():
    trace = Trace("T14_01")
    event = trace.validate(
        "ADSL",
        "USUBJID is unique",
        passed=False,
        metrics={"duplicates": 2},
    )

    assert event.status is Status.FAIL
    assert event.severity is Severity.WARNING
    assert event.metrics == {"duplicates": 2}


def test_output():
    trace = Trace("T14_01")
    event = trace.output("T14_01", "T14_01.xlsx", format="xlsx", rows=42)

    assert event.operation is Operation.OUTPUT
    assert event.object == "T14_01"
    assert event.action == "written"
    assert event.details["path"] == "T14_01.xlsx"
    assert event.details["format"] == "xlsx"
    assert event.metrics["rows"] == 42


def test_details_are_preserved_and_normalized_metadata_added():
    trace = Trace("T14_01")
    event = trace.read(
        "ADSL",
        source="adsl.csv",
        details={"library": "analysis"},
    )

    assert event.details == {"library": "analysis", "source": "adsl.csv"}


def test_alpha_benchmark_api(capsys):
    trace = Trace("T14_01")
    trace.read("ADSL", source="adsl.csv", rows=754, columns=16)
    trace.filter(
        "ADSL",
        "SAFFL == 'Y'",
        result="Safety Population",
        before=754,
        after=720,
    )
    trace.derive("AGEGR1", dataset="ADSL", source="AGE")
    trace.aggregate(
        "Safety Population",
        by=["TRT01A", "AGEGR1"],
        result="summary",
    )
    trace.output("T14_01", "T14_01.xlsx", rows=6)

    output = capsys.readouterr().err
    assert "INFO [READ] [ADSL] loaded" in output
    assert "INFO [FILTER] [ADSL] SAFFL == 'Y' applied – N=754 → 720" in output
    assert "INFO [DERIVE] [AGEGR1] created" in output
    assert "INFO [AGGREGATE] [Safety Population] summarized" in output
    assert "INFO [OUTPUT] [T14_01] written – T14_01.xlsx, N=6" in output
