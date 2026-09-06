import pytest

from trace_tlf import Operation, Status, Trace


def test_log_accepts_canonical_operation_string():
    trace = Trace("T14_01")

    event = trace.log(
        "DERIVE",
        object="AGEGR1",
        action="created",
    )

    assert event.operation is Operation.DERIVE
    assert event.object == "AGEGR1"
    assert event.action == "created"


def test_log_accepts_operation_enum():
    trace = Trace("T14_01")

    event = trace.log(
        Operation.CHECK,
        object="ADSL",
        action="row count observed",
    )

    assert event.operation is Operation.CHECK


def test_log_rejects_noncanonical_subset_with_filter_hint():
    trace = Trace("T14_01")

    with pytest.raises(ValueError, match="FILTER"):
        trace.log(
            "SUBSET",
            object="ADSL",
            action="SAFFL == 'Y' applied",
        )


def test_log_rejects_unknown_operation():
    trace = Trace("T14_01")

    with pytest.raises(ValueError, match="unknown TRACE operation"):
        trace.log(
            "WHATEVER",
            object="ADSL",
            action="did something",
        )


def test_log_requires_nonempty_action():
    trace = Trace("T14_01")

    with pytest.raises(ValueError):
        trace.log(
            "CHECK",
            object="ADSL",
            action="",
        )


def test_log_requires_metrics_mapping():
    trace = Trace("T14_01")

    with pytest.raises(TypeError, match="metrics"):
        trace.log(
            "CHECK",
            object="ADSL",
            action="row count observed",
            metrics=["rows", 754],
        )


def test_log_requires_details_mapping():
    trace = Trace("T14_01")

    with pytest.raises(TypeError, match="details"):
        trace.log(
            "CHECK",
            object="ADSL",
            action="row count observed",
            details="source=adsl.csv",
        )


def test_log_normalizes_status():
    trace = Trace("T14_01")

    event = trace.log(
        "VALIDATE",
        object="ADSL",
        action="USUBJID uniqueness",
        status="success",
    )

    assert event.status is Status.SUCCESS


def test_log_rejects_invalid_status():
    trace = Trace("T14_01")

    with pytest.raises(ValueError, match="invalid status"):
        trace.log(
            "VALIDATE",
            object="ADSL",
            action="USUBJID uniqueness",
            status="PASSED",
        )


def test_generic_derive_is_semantically_equivalent_to_tier1():
    trace = Trace("T14_01")

    tier1 = trace.derive(
        "AGEGR1",
        dataset="ADSL",
        source="AGE",
    )

    generic = trace.log(
        "DERIVE",
        object="AGEGR1",
        action="created",
        details={
            "dataset": "ADSL",
            "source": "AGE",
        },
    )

    assert generic.operation is tier1.operation
    assert generic.object == tier1.object
    assert generic.action == tier1.action
    assert dict(generic.metrics) == dict(tier1.metrics)
    assert dict(generic.details) == dict(tier1.details)
    assert generic.status == tier1.status
    assert generic.context == tier1.context
