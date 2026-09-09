import numpy as np

from trace_tlf import Trace


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
