import numpy as np

from trace_stat import Trace


def test_named_metrics_accept_numpy_integral_scalars():
    event = Trace("T14_01").read(
        "ADSL",
        rows=np.int64(754),
        columns=np.int32(16),
    )

    assert event.metrics["rows"] == 754
    assert type(event.metrics["rows"]) is int
    assert event.metrics["columns"] == 16
    assert type(event.metrics["columns"]) is int


def test_structured_metrics_normalize_numpy_numeric_scalars():
    event = Trace("T14_01").check(
        "ADSL",
        "prototype metrics",
        metrics={
            "subjects": np.int64(754),
            "rate": np.float64(0.95),
        },
    )

    assert event.metrics == {"subjects": 754, "rate": 0.95}
    assert type(event.metrics["subjects"]) is int
    assert type(event.metrics["rate"]) is float


def test_filter_normalizes_numpy_counts_and_derives_python_int_removed():
    event = Trace("T14_01").filter(
        "ADSL",
        "SAFFL == 'Y'",
        before=np.int64(754),
        after=np.int32(720),
    )

    assert event.metrics == {"before": 754, "after": 720, "removed": 34}
    assert all(type(value) is int for value in event.metrics.values())


def test_merge_normalizes_named_and_custom_numpy_diagnostics():
    event = Trace("T14_01").merge(
        "ADAE",
        "ADSL",
        left_rows=np.int64(4127),
        right_rows=np.int32(754),
        result_rows=np.int64(4127),
        metrics={
            "matched_subjects": np.int64(751),
            "match_rate": np.float64(0.996),
        },
    )

    assert event.metrics == {
        "matched_subjects": 751,
        "match_rate": 0.996,
        "left_rows": 4127,
        "right_rows": 754,
        "result_rows": 4127,
    }
    assert type(event.metrics["matched_subjects"]) is int
    assert type(event.metrics["match_rate"]) is float
