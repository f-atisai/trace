import inspect

import pytest

from trace_tlf import Trace
from trace_tlf.operations import Operation
from trace_tlf.rendering import render_text


EXPECTED_METHOD_PARAMETERS = {
    "read": ["self", "name", "source", "rows", "columns", "details"],
    "check": ["self", "name", "check", "metrics", "details"],
    "filter": [
        "self",
        "name",
        "condition",
        "result",
        "before",
        "after",
        "removed",
        "details",
    ],
    "sort": ["self", "name", "by", "ascending", "details"],
    "derive": ["self", "variable", "dataset", "source", "method", "details"],
    "transform": [
        "self",
        "name",
        "transformation",
        "source",
        "result",
        "details",
    ],
    "merge": [
        "self",
        "left",
        "right",
        "on",
        "how",
        "result",
        "left_rows",
        "right_rows",
        "result_rows",
        "metrics",
        "details",
    ],
    "aggregate": ["self", "name", "by", "result", "method", "rows", "details"],
    "analyze": [
        "self",
        "source",
        "analysis",
        "method",
        "population",
        "result",
        "details",
    ],
    "validate": ["self", "name", "check", "passed", "metrics", "details"],
    "output": ["self", "name", "path", "format", "rows", "details"],
    "step": ["self", "name"],
    "log": [
        "self",
        "operation",
        "object",
        "action",
        "metrics",
        "details",
        "status",
    ],
}


def test_constructor_signature_is_frozen_for_alpha():
    parameters = inspect.signature(Trace).parameters

    assert list(parameters) == ["program", "study", "log_file", "level"]
    assert parameters["program"].kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
    assert parameters["study"].kind is inspect.Parameter.KEYWORD_ONLY
    assert parameters["log_file"].kind is inspect.Parameter.KEYWORD_ONLY
    assert parameters["level"].kind is inspect.Parameter.KEYWORD_ONLY
    assert parameters["study"].default is None
    assert parameters["log_file"].default is None
    assert parameters["level"].default == "INFO"


@pytest.mark.parametrize(
    ("method_name", "parameter_names"),
    EXPECTED_METHOD_PARAMETERS.items(),
)
def test_alpha_method_parameter_names_are_frozen(method_name, parameter_names):
    method = getattr(Trace, method_name)
    assert list(inspect.signature(method).parameters) == parameter_names


def test_common_tier1_metadata_is_keyword_only():
    signature = inspect.signature(Trace.filter)

    assert signature.parameters["name"].kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
    assert (
        signature.parameters["condition"].kind
        is inspect.Parameter.POSITIONAL_OR_KEYWORD
    )
    assert signature.parameters["result"].kind is inspect.Parameter.KEYWORD_ONLY
    assert signature.parameters["before"].kind is inspect.Parameter.KEYWORD_ONLY
    assert signature.parameters["after"].kind is inspect.Parameter.KEYWORD_ONLY


def test_core_read_requires_only_semantic_identity():
    event = Trace("T14_01").read("ADSL")

    assert event.operation is Operation.READ
    assert event.object == "ADSL"
    assert event.metrics == {}
    assert event.details == {}


def test_core_filter_does_not_require_runtime_dataframe():
    event = Trace("T14_01").filter(
        "ADSL",
        "SAFFL == 'Y'",
        result="Safety Population",
    )

    assert event.operation is Operation.FILTER
    assert event.object == "ADSL"
    assert event.details["result"] == "Safety Population"


def test_trace_records_operation_but_does_not_perform_it():
    source_rows = [1, 2, 3]
    original = list(source_rows)

    Trace("T14_01").filter("ADSL", "VALUE > 1", before=3, after=2)

    assert source_rows == original


def test_structured_event_is_renderer_input_and_source_of_truth(capsys):
    event = Trace("T14_01").filter(
        "ADSL",
        "SAFFL == 'Y'",
        result="Safety Population",
        before=754,
        after=720,
    )

    emitted = capsys.readouterr().err.strip()

    assert event.object == "ADSL"
    assert event.details["result"] == "Safety Population"
    assert event.metrics == {"before": 754, "after": 720, "removed": 34}
    assert emitted == render_text(event)


def test_constructor_rejects_invalid_public_arguments():
    with pytest.raises(ValueError, match="program"):
        Trace("")

    with pytest.raises(TypeError, match="study"):
        Trace("T14_01", study=123)

    with pytest.raises(ValueError, match="level"):
        Trace("T14_01", level="VERBOSE")


def test_tier1_rejects_non_bool_validation_outcome():
    with pytest.raises(TypeError, match="passed"):
        Trace("T14_01").validate(
            "ADSL",
            "USUBJID is unique",
            passed=1,
        )


def test_filter_rejects_after_count_larger_than_before_count():
    with pytest.raises(ValueError, match="after"):
        Trace("T14_01").filter(
            "ADSL",
            "SAFFL == 'Y'",
            before=10,
            after=12,
        )


def test_negative_named_diagnostics_are_rejected():
    trace = Trace("T14_01")

    with pytest.raises(ValueError, match="rows"):
        trace.read("ADSL", rows=-1)

    with pytest.raises(ValueError, match="result_rows"):
        trace.merge("ADAE", "ADSL", result_rows=-1)

    with pytest.raises(ValueError, match="rows"):
        trace.output("T14_01", "T14_01.rtf", rows=-1)


def test_canonical_operation_aliases_are_not_silently_accepted():
    trace = Trace("T14_01")

    with pytest.raises(ValueError, match="FILTER"):
        trace.log("SUBSET", object="ADSL", action="population selected")

    with pytest.raises(ValueError, match="MERGE"):
        trace.log("JOIN", object="ADAE + ADSL", action="combined")

    with pytest.raises(ValueError, match="READ"):
        trace.log("LOAD", object="ADSL", action="loaded")
