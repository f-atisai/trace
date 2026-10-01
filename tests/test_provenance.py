import os

import pytest

from trace_tlf import Trace


def _temporary_files(tmp_path):
    return [path for path in tmp_path.iterdir() if path.name.startswith(".")]

def test_events_stream_before_context_exit(tmp_path, capsys):
    log_file = tmp_path / "T14_01.log"

    with Trace("T14_01", log_file=log_file) as trace:
        trace.read("ADSL", source="data/adsl.xpt", rows=254)
        streamed = capsys.readouterr().err
        assert "INFO [START] [T14_01] execution started" in streamed
        assert "INFO [READ] [ADSL] loaded" in streamed
        assert not log_file.exists()


def test_final_log_places_provenance_before_events(tmp_path):
    log_file = tmp_path / "T14_01.log"

    with Trace("T14_01", log_file=log_file) as trace:
        trace.read("ADSL", source="data/adsl.xpt", rows=254)
        trace.filter("ADSL", "SAFFL == 'Y'", before=254, after=249)
        trace.output("T14_01", "outputs/tlf_population.rtf")

    output = log_file.read_text(encoding="utf-8")

    assert output.startswith("TRACE EXECUTION\n\nProgram:  T14_01\n")
    assert f"Run ID:   {trace.run_id}" in output
    assert "Executed: " in output
    assert "Input artifacts:\n  data/adsl.xpt" in output
    assert "Output artifacts:\n  outputs/tlf_population.rtf" in output
    assert output.index("TRACE EXECUTION") < output.index("INFO [START]")
    assert output.index("INFO [START]") < output.index("INFO [READ]")
    assert output.index("INFO [READ]") < output.index("INFO [FILTER]")
    assert output.index("INFO [FILTER]") < output.index("INFO [OUTPUT]")
    assert output.index("INFO [OUTPUT]") < output.index("INFO [END]")
    assert _temporary_files(tmp_path) == []


def test_user_exception_still_finalizes_log_and_propagates_unchanged(
    tmp_path,
):
    log_file = tmp_path / "T14_01.log"
    original = ValueError("analysis failed")

    with pytest.raises(ValueError) as caught:
        with Trace("T14_01", log_file=log_file) as trace:
            trace.read("ADSL", source="data/adsl.xpt")
            raise original

    output = log_file.read_text(encoding="utf-8")

    assert caught.value is original
    assert output.startswith("TRACE EXECUTION")
    assert "INFO [READ] [ADSL] loaded" in output
    assert "ERROR [END] [T14_01] execution failed" in output
    assert _temporary_files(tmp_path) == []


def test_nested_step_failure_is_preserved_in_final_log(tmp_path):
    log_file = tmp_path / "T14_01.log"

    with pytest.raises(ValueError, match="step failed"):
        with Trace("T14_01", log_file=log_file) as trace:
            with trace.step("Analysis Population"):
                raise ValueError("step failed")

    output = log_file.read_text(encoding="utf-8")

    assert "INFO [STEP] [Analysis Population] started" in output
    assert "ERROR [STEP] [Analysis Population] failed" in output
    assert "ERROR [END] [T14_01] execution failed" in output


def test_finalization_failure_does_not_mask_user_exception(tmp_path, monkeypatch):
    log_file = tmp_path / "T14_01.log"
    original = ValueError("program failure")
    trace = Trace("T14_01", log_file=log_file)

    def fail_finalization():
        raise OSError("finalization failure")

    monkeypatch.setattr(trace, "_finalize_log", fail_finalization)

    with pytest.raises(ValueError) as caught:
        with trace:
            raise original

    assert caught.value is original
    assert trace._spool_path.exists()


def test_finalization_failure_without_user_exception_is_reported(
    tmp_path,
    monkeypatch,
):
    log_file = tmp_path / "T14_01.log"
    trace = Trace("T14_01", log_file=log_file)

    def fail_finalization():
        raise OSError("finalization failure")

    monkeypatch.setattr(trace, "_finalize_log", fail_finalization)

    with pytest.raises(RuntimeError, match="TRACE log finalization failed"):
        with trace:
            pass

    assert trace._spool_path.exists()


def test_atomic_replace_preserves_spool_when_publication_fails(
    tmp_path,
    monkeypatch,
):
    log_file = tmp_path / "T14_01.log"
    log_file.write_text("previous complete run\n", encoding="utf-8")
    trace = Trace("T14_01", log_file=log_file)

    def fail_replace(source, destination):
        raise OSError("replace failed")

    monkeypatch.setattr(os, "replace", fail_replace)

    with pytest.raises(RuntimeError, match="TRACE log finalization failed"):
        with trace:
            trace.read("ADSL", source="data/adsl.xpt")

    assert log_file.read_text(encoding="utf-8") == "previous complete run\n"
    assert trace._spool_path.exists()
    assert "INFO [READ] [ADSL] loaded" in trace._spool_path.read_text(
        encoding="utf-8"
    )
    assert not any(path.name.endswith(".final.tmp") for path in tmp_path.iterdir())


def test_existing_destination_is_replaced_with_complete_new_run(tmp_path):
    log_file = tmp_path / "T14_01.log"
    log_file.write_text("old run marker\n", encoding="utf-8")

    with Trace("T14_01", log_file=log_file) as trace:
        trace.read("ADSL", source="data/adsl.xpt")

    output = log_file.read_text(encoding="utf-8")

    assert "old run marker" not in output
    assert output.startswith("TRACE EXECUTION")
    assert output.count("INFO [START] [T14_01] execution started") == 1
    assert output.count("INFO [END] [T14_01] execution completed") == 1


def test_artifact_paths_are_deduplicated_in_first_seen_order(tmp_path):
    log_file = tmp_path / "T14_01.log"

    with Trace("T14_01", log_file=log_file) as trace:
        trace.read("ADSL", source="data/adsl.xpt")
        trace.read("ADSL_COPY", source="data/adsl.xpt")
        trace.read("ADAE", source="data/adae.xpt")
        trace.output("TABLE", "outputs/table.rtf")
        trace.output("TABLE_COPY", "outputs/table.rtf")

    output = log_file.read_text(encoding="utf-8")
    provenance = output.split("\n\nINFO [START]", maxsplit=1)[0]

    assert provenance.count("data/adsl.xpt") == 1
    assert provenance.count("outputs/table.rtf") == 1
    assert provenance.index("data/adsl.xpt") < provenance.index("data/adae.xpt")


def test_no_artifact_run_has_explicit_empty_sections(tmp_path):
    log_file = tmp_path / "T14_01.log"

    with Trace("T14_01", log_file=log_file):
        pass

    output = log_file.read_text(encoding="utf-8")

    assert "Input artifacts:\n  (none)" in output
    assert "Output artifacts:\n  (none)" in output


def test_no_log_file_skips_persistent_provenance(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    trace = Trace("T14_01")

    def fail_persistence(*args, **kwargs):
        raise AssertionError("persistence must not run without log_file")

    monkeypatch.setattr(trace, "_start_spool", fail_persistence)
    monkeypatch.setattr(trace, "_write_direct_log", fail_persistence)

    with trace:
        trace.read("ADSL", source="data/adsl.xpt")

    assert getattr(trace, "_spool_path", None) is None
    assert list(tmp_path.iterdir()) == []


def test_run_id_is_stable_across_stream_and_final_log(tmp_path, capsys):
    log_file = tmp_path / "T14_01.log"
    trace = Trace("T14_01", log_file=log_file)
    run_id = trace.run_id

    with trace:
        assert trace.run_id == run_id
        trace.check("ADSL", "USUBJID is unique")

    capsys.readouterr()
    output = log_file.read_text(encoding="utf-8")

    assert trace.run_id == run_id
    assert f"Run ID:   {run_id}" in output


def test_event_rendering_is_unchanged_in_final_log(tmp_path, capsys):
    log_file = tmp_path / "T14_01.log"

    with Trace("T14_01", log_file=log_file) as trace:
        trace.filter("ADSL", "SAFFL == 'Y'", before=10, after=8)

    streamed_lines = capsys.readouterr().err.strip().splitlines()
    final_lines = log_file.read_text(encoding="utf-8").strip().splitlines()
    event_lines = [
        line
        for line in final_lines
        if line.startswith(
            ("DEBUG ", "INFO ", "WARNING ", "ERROR ", "CRITICAL ")
        )
    ]

    assert event_lines == streamed_lines
    assert all("Run ID:" not in line for line in event_lines)
    assert all("Executed:" not in line for line in event_lines)
